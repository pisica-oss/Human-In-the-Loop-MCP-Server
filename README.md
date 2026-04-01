# Human-In-the-Loop MCP Server

Minimal MCP server with a single tool: `get_multiline_input`. Opens a GUI dialog for the user to type multi-line text, enabling session continuation without spending extra credits.

## Copilot Instructions

Add this to your `copilot-instructions.md`:

```
After completing each task, please use the get_multiline_input MCP tool to ask me what I'd like to work on next, rather than ending the session. This helps me stay in flow.
```

## Setup (VS Code)

Add to your VS Code MCP config (`settings.json` or `.vscode/mcp.json`):

```json
{
  "servers": {
    "human-in-the-loop": {
      "type": "stdio",
      "command": "python",
      "args": ["path/to/human_loop_server.py"]
    }
  }
}
```

## Tool

### `get_multiline_input`

Opens a tkinter dialog window for multi-line text input.

**Parameters:**
- `session_tag` (str, required): A unique memorable word (e.g. "tiger", "comet"). Shown in the window title so the user can identify which agent opened the dialog when running multiple agents in parallel.

**Returns:**
```json
{"success": true, "user_input": "the text the user typed"}
```

Or if cancelled:
```json
{"success": false, "cancelled": true}
```

## Requirements

- Python >= 3.12
- `fastmcp >= 2.8.1`
- `pydantic >= 2.0.0`
- A desktop environment (tkinter GUI)

## License

MIT
