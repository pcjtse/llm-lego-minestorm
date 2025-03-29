# LEGO Mindstorms MCP Server

This server acts as a Model Context Protocol (MCP) server for controlling a LEGO Mindstorms robot through natural language commands from Claude or other AI assistants.

## Features

- Natural language command processing
- Basic movement controls (forward, backward, left, right)
- Position-based navigation (goto red circle, goto green circle)
- Model Context Protocol (MCP) interface
- Real-time robot control and status tracking
- Claude Desktop integration

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python server.py
```

3. Configure Claude Desktop:
- Copy `claude_desktop_config.json` to your Claude Desktop configuration directory
- Restart Claude Desktop to load the new configuration
- The robot control interface will be available as a new capability in Claude Desktop

## Model Context Protocol (MCP)

The server implements the Model Context Protocol, accepting requests at the `/mcp` endpoint. Messages should be formatted as follows:

```json
{
    "messages": [
        "Previous message 1",
        "Previous message 2",
        "Current command for the robot"
    ],
    "context": {
        "optional": "context data"
    }
}
```

Response format:
```json
{
    "response": {
        "status": "success",
        "message": "Action description"
    },
    "context": {
        "robot_status": {
            "status": "idle",
            "position": "current position",
            "current_action": null
        }
    }
}
```

## Sample Prompts

Here are some example natural language commands that the robot understands:

### Basic Movement
- "Move forward for 2 seconds"
- "Go backward"
- "Turn left"
- "Turn right for 1.5 seconds"

### Target Navigation
- "Go to the red circle"
- "Find the green circle"
- "Navigate to the red circle"
- "Move to the green circle"

### Sample Claude Prompt
```
You are controlling a LEGO Mindstorms robot through an MCP server. The robot can move in basic directions and find colored circles.

Current context: The robot is idle and ready for commands.
```

## Requirements

- Python 3.8+
- LEGO Mindstorms EV3
- ev3dev OS on the robot
- Claude Desktop (for natural language control)

## API Endpoints

- `POST /mcp` - Main MCP endpoint for natural language commands
- `GET /status` - Get current robot status

## License

MIT License

Copyright (c) 2024 [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 