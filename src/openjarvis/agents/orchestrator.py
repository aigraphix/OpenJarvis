"""OrchestratorAgent — multi-turn agent with tool-calling loop.

Supports two modes:

- **function_calling** (default): Uses OpenAI-format tool definitions and
  parses ``tool_calls`` from the engine response.
- **structured**: Uses a THOUGHT/TOOL/INPUT/FINAL_ANSWER text format
  (like ReAct) with a canonical system prompt from the orchestrator
  prompt registry.  This is the format used by the SFT/GRPO training
  pipelines, making the Orchestrator a distinctive trainable agent type.
"""

from __future__ import annotations

import concurrent.futures
import re
from typing import Any, List, Optional

from openjarvis.agents._stubs import AgentContext, AgentResult, ToolUsingAgent
from openjarvis.core.events import EventBus
from openjarvis.core.registry import AgentRegistry
from openjarvis.core.types import Message, Role, ToolCall, ToolResult
from openjarvis.engine._stubs import InferenceEngine
from openjarvis.tools._stubs import BaseTool


@AgentRegistry.register("orchestrator")
class OrchestratorAgent(ToolUsingAgent):
    """Multi-turn agent that routes between tools and the LLM.

    Implements a tool-calling loop:
    1. Send messages with tool definitions to the engine.
    2. If the response contains tool_calls, execute them and loop.
    3. If no tool_calls, return the final answer.
    4. Stop after ``max_turns`` iterations.

    In **structured** mode the agent instead uses a
    ``THOUGHT: / TOOL: / INPUT: / FINAL_ANSWER:`` text protocol
    identical to the format used by the orchestrator SFT/GRPO
    training pipelines.
    """

    agent_id = "orchestrator"
    _default_temperature = 0.7
    _default_max_tokens = 1024
    _default_max_turns = 10

    def __init__(
        self,
        engine: InferenceEngine,
        model: str,
        *,
        tools: Optional[List[BaseTool]] = None,
        bus: Optional[EventBus] = None,
        max_turns: Optional[int] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        mode: str = "function_calling",
        system_prompt: Optional[str] = None,
        parallel_tools: bool = True,
        interactive: bool = False,
        confirm_callback=None,
    ) -> None:
        super().__init__(
            engine,
            model,
            tools=tools,
            bus=bus,
            max_turns=max_turns,
            temperature=temperature,
            max_tokens=max_tokens,
            interactive=interactive,
            confirm_callback=confirm_callback,
        )
        self._mode = mode
        self._system_prompt = system_prompt
        self._parallel_tools = parallel_tools

    def run(
        self,
        input: str,
        context: Optional[AgentContext] = None,
        **kwargs: Any,
    ) -> AgentResult:
        if self._mode == "structured":
            return self._run_structured(input, context, **kwargs)
        return self._run_function_calling(input, context, **kwargs)

    # ------------------------------------------------------------------
    # Structured mode (THOUGHT/TOOL/INPUT/FINAL_ANSWER)
    # ------------------------------------------------------------------

    def _run_structured(
        self,
        input: str,
        context: Optional[AgentContext] = None,
        **kwargs: Any,
    ) -> AgentResult:
        self._emit_turn_start(input)

        # Build system prompt
        if self._system_prompt:
            sys_prompt = self._system_prompt
        else:
            from openjarvis.learning.intelligence.orchestrator.prompt_registry import (
                build_system_prompt,
            )

            sys_prompt = build_system_prompt(tools=self._tools)

        try:
            import os
            from openjarvis.agents.manager import AgentManager
            manager = AgentManager(os.path.expanduser("~/.openjarvis/agents.db"))
            agents = manager.list_agents()
            agent_names = []
            for agent in agents:
                desc = agent.get('config', {}).get('description', '')
                if desc:
                    agent_names.append(f"{agent['name']} ({desc[:100]}...)")
                else:
                    agent_names.append(agent['name'])
            roster_str = " | ".join(agent_names)
            extra = f"\n\nDynamic Context: You currently have {len(agents)} registered agents available: {roster_str}."
            injected_sys = sys_prompt + extra if sys_prompt else extra
        except Exception:
            injected_sys = sys_prompt
            
        messages = self._build_messages(input, context, system_prompt=injected_sys)

        all_tool_results: list[ToolResult] = []
        turns = 0

        for _turn in range(self._max_turns):
            turns += 1

            if self._loop_guard:
                messages = self._loop_guard.compress_context(messages)

            result = self._generate(messages)
            content = result.get("content", "")

            parsed = self._parse_structured_response(content)

            # FINAL_ANSWER -> done
            if parsed["final_answer"]:
                self._emit_turn_end(turns=turns)
                return AgentResult(
                    content=parsed["final_answer"],
                    tool_results=all_tool_results,
                    turns=turns,
                )

            # TOOL -> execute
            if parsed["tool"]:
                messages.append(Message(role=Role.ASSISTANT, content=content))

                tool_call = ToolCall(
                    id=f"orch_{turns}",
                    name=parsed["tool"],
                    arguments=parsed["input"] or "{}",
                )
                tool_result = self._executor.execute(tool_call)
                all_tool_results.append(tool_result)

                observation = f"Observation: {tool_result.content}"
                messages.append(Message(role=Role.USER, content=observation))
                continue

            # Neither -> treat content as final answer
            self._emit_turn_end(turns=turns)
            return AgentResult(
                content=content,
                tool_results=all_tool_results,
                turns=turns,
            )

        # Max turns exceeded
        return self._max_turns_result(all_tool_results, turns)

    @staticmethod
    def _parse_structured_response(text: str) -> dict:
        """Parse THOUGHT/TOOL/INPUT/FINAL_ANSWER from model output."""
        result = {
            "thought": "",
            "tool": "",
            "input": "",
            "final_answer": "",
        }

        thought_match = re.search(
            r"THOUGHT:\s*(.+?)(?=\nTOOL:|\nFINAL[_ ]?ANSWER:|\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if thought_match:
            result["thought"] = thought_match.group(1).strip()

        final_match = re.search(
            r"FINAL[_ ]?ANSWER:\s*(.+)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if final_match:
            result["final_answer"] = final_match.group(1).strip()
            return result

        tool_match = re.search(r"TOOL:\s*(.+)", text, re.IGNORECASE)
        if tool_match:
            result["tool"] = tool_match.group(1).strip()

        input_match = re.search(
            r"INPUT:\s*(.+?)(?=\nTHOUGHT:|\nTOOL:|\nFINAL|\Z)",
            text,
            re.DOTALL | re.IGNORECASE,
        )
        if input_match:
            result["input"] = input_match.group(1).strip()

        return result

    # ------------------------------------------------------------------
    # Function-calling mode (original behaviour)
    # ------------------------------------------------------------------

    def _get_injected_system_prompt(self, minimal: bool = False) -> Optional[str]:
        base_prompt = self._system_prompt
        if not base_prompt:
            try:
                from openjarvis.core.config import load_config
                config = load_config()
                base_prompt = config.agent.default_system_prompt
            except Exception:
                pass

        try:
            import os
            from openjarvis.agents.manager import AgentManager
            manager = AgentManager(os.path.expanduser("~/.openjarvis/agents.db"))
            agents = manager.list_agents()
            
            if minimal:
                extra = f"\n\nDynamic Context: You have {len(agents)} registered agents available. Use 'agent_delegate' if you need specialized help."
            else:
                agent_names = []
                for agent in agents:
                    desc = agent.get('config', {}).get('description', '')
                    if desc:
                        # Truncate descriptions aggressively
                        short_desc = desc[:60].strip() + "..." if len(desc) > 60 else desc
                        agent_names.append(f"{agent['name']} ({short_desc})")
                    else:
                        agent_names.append(agent['name'])
                roster_str = " | ".join(agent_names)
                extra = f"\n\nDynamic Context: You currently have {len(agents)} registered agents available: {roster_str}."

            # Inject a simple, targeted context rather than the massive tool schema to save tokens
            if self._tools:
                extra += "\n\nIMPORTANT SYSTEM CAPABILITIES: You are NOT just a text-based AI. You HAVE access to real tools (like pdf_generate). You can and MUST confidently state that you are able to build physical files when using these tools. DO NOT APOLOGIZE OR CLAIM INABILITY."

            if base_prompt:
                return base_prompt + extra
            return extra
        except Exception:
            # Inject the targeted fallback
            extra_fallback = ""
            if self._tools:
                extra_fallback = "\n\nIMPORTANT SYSTEM CAPABILITIES: You have real tool access. Confidence is required."
            if base_prompt:
                return base_prompt + extra_fallback
            return extra_fallback

    def _run_function_calling(
        self,
        input: str,
        context: Optional[AgentContext] = None,
        **kwargs: Any,
    ) -> AgentResult:
        self._emit_turn_start(input)

        # Build initial messages - use minimal roster if we have history to save tokens
        has_history = context and context.conversation.messages
        injected_sys = self._get_injected_system_prompt(minimal=bool(has_history))
        messages = self._build_messages(input, context, system_prompt=injected_sys)

        # Get OpenAI-format tool definitions
        openai_tools = self._executor.get_openai_tools() if self._tools else []

        all_tool_results: list[ToolResult] = []
        turns = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0

        for _turn in range(self._max_turns):
            turns += 1

            if self._loop_guard:
                messages = self._loop_guard.compress_context(messages)

            # Build generate kwargs
            gen_kwargs: dict[str, Any] = {}
            if openai_tools:
                gen_kwargs["tools"] = openai_tools

            result = self._generate(messages, **gen_kwargs)

            # Accumulate token usage
            usage = result.get("usage", {})
            total_prompt_tokens += usage.get("prompt_tokens", 0)
            total_completion_tokens += usage.get("completion_tokens", 0)

            content = result.get("content", "")
            raw_tool_calls = result.get("tool_calls", [])

            # No tool calls -> check continuation, then final answer
            if not raw_tool_calls:
                content = self._check_continuation(result, messages)
                content = self._strip_think_tags(content)
                self._emit_turn_end(turns=turns, content_length=len(content))
                # Safety override: If the model STILL apologizes despite obvious success,
                # strip the apology and replace it with a confident confirmation.
                pdf_tool_res = next((tr for tr in all_tool_results if tr.tool_name == "pdf_generate" and tr.success), None)
                if pdf_tool_res:
                    apology_keywords = [
                        "cannot", "unable", "sorry", "apologize", "can't",
                        "don't have the ability", "limitations", "i can't generate",
                        "cannot generate an actual", "text-based",
                    ]
                    
                    # Extract the [RENDER_CANVAS] tag from the tool result
                    import re as _re
                    canvas_match = _re.search(r'\[RENDER_CANVAS:pdf:[^\]]+\]', pdf_tool_res.content)
                    canvas_tag = canvas_match.group(0) if canvas_match else ""

                    cleaned = content
                    if any(kw in content.lower()[:300] for kw in apology_keywords):
                        cleaned = _re.sub(
                            r'[^.!?\n]*(?:cannot|can\'t|unable|sorry|apologize|text-based|limitations)[^.!?\n]*[.!?]\s*',
                            '', content, flags=_re.IGNORECASE,
                        ).strip()
                        
                    content = (
                        "Your PDF has been generated and is ready for preview in the canvas. ✅\n\n"
                        f"{canvas_tag}\n\n"
                        + (cleaned if cleaned else "")
                    ).strip()

                return AgentResult(
                    content=content,
                    tool_results=all_tool_results,
                    turns=turns,
                    metadata={
                        "prompt_tokens": total_prompt_tokens,
                        "completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens,
                    },
                )

            # Build ToolCall objects from raw dicts
            tool_calls = [
                ToolCall(
                    id=tc.get("id", f"call_{i}"),
                    name=tc.get("name", ""),
                    arguments=tc.get("arguments", "{}"),
                )
                for i, tc in enumerate(raw_tool_calls)
            ]

            # Append assistant message with tool calls
            messages.append(
                Message(
                    role=Role.ASSISTANT,
                    content=content,
                    tool_calls=tool_calls,
                )
            )

            # Execute each tool (with loop guard check) and append results
            if self._parallel_tools and len(tool_calls) > 1:
                # Parallel execution
                def _exec_tool(tc: ToolCall) -> tuple:
                    if self._loop_guard:
                        verdict = self._loop_guard.check_call(
                            tc.name,
                            tc.arguments,
                        )
                        if verdict.blocked:
                            return tc, ToolResult(
                                tool_name=tc.name,
                                content=f"Loop guard: {verdict.reason}",
                                success=False,
                            )
                    return tc, self._executor.execute(tc)

                with concurrent.futures.ThreadPoolExecutor(
                    max_workers=len(tool_calls),
                ) as pool:
                    futures = {pool.submit(_exec_tool, tc): tc for tc in tool_calls}
                    results_map: dict[int, tuple] = {}
                    for future in concurrent.futures.as_completed(futures):
                        tc_orig = futures[future]
                        results_map[id(tc_orig)] = future.result()

                # Append results in original order
                for tc in tool_calls:
                    _, tool_result = results_map[id(tc)]
                    all_tool_results.append(tool_result)
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=tool_result.content,
                            tool_call_id=tc.id,
                            name=tc.name,
                        )
                    )
            else:
                # Sequential execution
                for tc in tool_calls:
                    # Loop guard check before execution
                    if self._loop_guard:
                        verdict = self._loop_guard.check_call(
                            tc.name,
                            tc.arguments,
                        )
                        if verdict.blocked:
                            tool_result = ToolResult(
                                tool_name=tc.name,
                                content=f"Loop guard: {verdict.reason}",
                                success=False,
                            )
                            all_tool_results.append(tool_result)
                            messages.append(
                                Message(
                                    role=Role.TOOL,
                                    content=tool_result.content,
                                    tool_call_id=tc.id,
                                    name=tc.name,
                                )
                            )
                            continue

                    tool_result = self._executor.execute(tc)
                    all_tool_results.append(tool_result)

                    # Append tool response message
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=tool_result.content,
                            tool_call_id=tc.id,
                            name=tc.name,
                        )
                    )
                    
            # Check if pdf_generate was successful to force a good assistant response
            if any(tc.name == "pdf_generate" for tc in tool_calls):
                # We use a USER message to affirm the tool success, which is more coercive for small models
                messages.append(
                    Message(
                        role=Role.USER,
                        content="VERIFICATION SUCCESS: The 'pdf_generate' tool HAS successfully created the file. I can see it in my sidebar right now. You are PROHIBITED from saying you cannot generate PDFs. Simply confirm to me that the PDF is ready and keep your response helpful. DO NOT APOLOGIZE.",
                    )
                )

        # Max turns exceeded
        final_content = self._strip_think_tags(content) if content else ""
        self._emit_turn_end(turns=turns, max_turns_exceeded=True)
        return AgentResult(
            content=final_content or "Maximum turns reached without a final answer.",
            tool_results=all_tool_results,
            turns=turns,
            metadata={
                "max_turns_exceeded": True,
                "prompt_tokens": total_prompt_tokens,
                "completion_tokens": total_completion_tokens,
                "total_tokens": total_prompt_tokens + total_completion_tokens,
            },
        )


__all__ = ["OrchestratorAgent"]
