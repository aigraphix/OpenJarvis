# Review Summary: Communication Layer & Structured Events

**Files Reviewed:**
1. `frontend/src/components/Chat/InputArea.tsx`
2. `src/openjarvis/agents/orchestrator.py`

**Overall Assessment:**
The system has functional components for chat interaction and agent orchestration, but the **communication layer is inconsistent and brittle.** The frontend uses fragile keyword matching for intent, while the backend supports two distinct agent protocols (`function_calling` vs `structured`), suggesting a lack of a unified "structured event" definition.

**High Priority Action Items (Bugs/Architecture):**

1.  **Frontend Intent Detection (Critical):** The keyword checks in `InputArea.tsx` (e.g., checking for "generate pdf") are highly fragile. This logic *must* be moved to the backend where it can be processed against the entire conversation context, not just the current input string.
2.  **Backend Protocol Abstraction (High):** The `orchestrator.py` needs an abstraction layer to harmonize the `function_calling` and `structured` modes. The goal should be to define a single, canonical *Event Structure* that the agent outputs, which the `run` method can then process uniformly.

**Suggested Refactoring:**
1.  **`InputArea.tsx`:** Remove all logic related to checking for specific phrases that trigger side effects (like opening the Canvas panel). It should only manage input state and call the API endpoint with the text.
2.  **`orchestrator.py`:** Refactor the `run` method to treat the output of the model as an abstract `AgentEvent` object, rather than branching logic based on the mode string. This single event object should contain fields like `event_type` (e.g., `TOOL_CALL`, `FINAL_ANSWER`, `SYSTEM_ACTION`) and associated data.

Please confirm if this assessment aligns with your vision for the structured event system so I can proceed with suggesting specific patches.