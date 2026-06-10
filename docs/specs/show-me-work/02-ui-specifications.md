# UI Specifications

## 3.1 Panels

- Left Panel: Orchestrator logic, model thinking, and compiler flags.
- Center Panel: Chat interface for user and model messages.
- Right Panel: Collapsible toggles (32 options).

## Right Panel Toggle Categories

- Model selection (Claude, GPT, Gemini).
- Orchestrator rules (example: Strict mode).
- Compiler sensitivity (example: Flag hallucinations).
- Display filters (example: Show only compiler flags).

## 3.2 Example Toggle Config

```json
{
  "model": "claude",
  "orchestrator": {
    "strictMode": true
  },
  "compiler": {
    "flagHallucinations": true,
    "sensitivity": "medium"
  },
  "display": {
    "showOnlyCompilerFlags": false
  }
}
```
