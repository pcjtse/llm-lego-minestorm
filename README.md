# LEGO Mindstorms NXT MCP Server

This server acts as a Model Context Protocol (MCP) server for controlling a LEGO Mindstorms NXT robot through natural language commands from Claude or other AI assistants.

## Features

- Natural language command processing
- Basic movement controls (forward, backward, left, right)
- Position-based navigation (goto red circle, goto green circle)
- Model Context Protocol (MCP) interface
- Real-time robot control and status tracking
- Claude Desktop integration
- NXT Brick auto-detection and connection

## Setup

1. Install system dependencies (required for NXT communication):
```bash
# Ubuntu/Debian
sudo apt-get install libusb-1.0-0-dev

# macOS
brew install libusb

# Windows
# Install Mindstorms NXT driver from LEGO website
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Connect your NXT brick via USB and start the server:
```bash
python server.py
```

4. Configure Claude Desktop:
- Copy `claude_desktop_config.json` to your Claude Desktop configuration directory
- Restart Claude Desktop to load the new configuration
- The robot control interface will be available as a new capability in Claude Desktop

## Model Context Protocol (MCP)

The server implements the Model Context Protocol for natural language robot control. Here are examples of actual message exchanges:

### Example 1: Basic Movement Command

Request:
```json
{
    "messages": [
        "Hello, I'd like to control the robot",
        "Move forward for 2 seconds"
    ],
    "context": {
        "robot_status": {
            "status": "idle",
            "position": null,
            "current_action": null
        }
    }
}
```

Response:
```json
{
    "response": {
        "status": "success",
        "message": "Moved forward for 2 seconds"
    },
    "context": {
        "robot_status": {
            "status": "idle",
            "position": null,
            "current_action": null
        }
    }
}
```

### Example 2: Target Navigation

Request:
```json
{
    "messages": [
        "Move forward for 2 seconds",
        "Go to the red circle"
    ],
    "context": {
        "robot_status": {
            "status": "idle",
            "position": null,
            "current_action": null
        }
    }
}
```

Response:
```json
{
    "response": {
        "status": "success",
        "message": "Reached red-circle"
    },
    "context": {
        "robot_status": {
            "status": "idle",
            "position": "red-circle",
            "current_action": null
        }
    }
}
```

### Example 3: Error Handling

Request:
```json
{
    "messages": [
        "Jump up and down"
    ],
    "context": {
        "robot_status": {
            "status": "idle",
            "position": null,
            "current_action": null
        }
    }
}
```

Response:
```json
{
    "detail": "Unknown command"
}
```

## Hardware Setup

1. Required Components:
   - LEGO Mindstorms NXT Brick
   - Two NXT motors connected to ports A (left) and B (right)
   - NXT Color Sensor connected to port 1
   - USB cable for connection

2. Sensor Configuration:
   - The color sensor should be mounted at the front of the robot
   - Color sensor values:
     - Red: Value 5
     - Green: Value 3
     - Make sure the sensor is at an appropriate height to detect the circles

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
You are controlling a LEGO Mindstorms NXT robot through an MCP server. The robot can move in basic directions and find colored circles.

Current context: The robot is idle and ready for commands.
```

## Requirements

- Python 3.8+
- LEGO Mindstorms NXT
- USB connection to NXT brick
- libusb (for NXT communication)
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