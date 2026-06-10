# Browser Plugin (Optional)

## 6.1 Orchestrator Plugin

- Target: ChatGPT web interface.
- Function: Prepends custom instructions to user prompts.
- Example instruction: Answer in bullet points. Cite sources.
- Tech: Chrome Extension (Manifest V3).

## 6.2 Compiler Plugin

- Target: ChatGPT web interface.
- Function: Scans responses for hallucinations and stale date/context cues.
- Injected flag example: [WARNING: Unsourced claim]
- Tech: Chrome Extension with content scripts.
