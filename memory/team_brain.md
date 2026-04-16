
### OpenJarvis Stream Bridge (2026-04-16)
OpenJarvis stream_bridge had a bug where used_real_streaming would re-stream the original request messages, completely bypassing tool execution context and orchestrator content edits. Fixed by enforcing word-by-word playback of the agent_result.content.
