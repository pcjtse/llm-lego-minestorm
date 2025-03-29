from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from enum import Enum
from ev3dev2.motor import LargeMotor, MoveTank, OUTPUT_A, OUTPUT_B
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_1
import uvicorn
from typing import Optional, Dict, Any
import json

class Direction(str, Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    LEFT = "left"
    RIGHT = "right"

class Target(str, Enum):
    RED_CIRCLE = "red-circle"
    GREEN_CIRCLE = "green-circle"

class RobotStatus(BaseModel):
    status: str
    position: Optional[str] = None
    current_action: Optional[str] = None

class MCPMessage(BaseModel):
    messages: list
    context: Optional[Dict[str, Any]] = None
    response_format: Optional[Dict[str, Any]] = None

app = FastAPI(title="LEGO Mindstorms MCP Server")

# Initialize robot components
try:
    tank_drive = MoveTank(OUTPUT_A, OUTPUT_B)
    color_sensor = ColorSensor(INPUT_1)
except Exception as e:
    print(f"Warning: Could not initialize robot components: {e}")
    # For testing without actual robot hardware
    tank_drive = None
    color_sensor = None

current_status = RobotStatus(status="idle")

def move_robot(direction: Direction, duration: float = 1.0):
    if not tank_drive:
        raise HTTPException(status_code=503, detail="Robot hardware not initialized")
    
    speed = 50  # 50% speed
    
    try:
        if direction == Direction.FORWARD:
            tank_drive.on_for_seconds(left_speed=speed, right_speed=speed, seconds=duration)
        elif direction == Direction.BACKWARD:
            tank_drive.on_for_seconds(left_speed=-speed, right_speed=-speed, seconds=duration)
        elif direction == Direction.LEFT:
            tank_drive.on_for_seconds(left_speed=-speed, right_speed=speed, seconds=duration/2)
        elif direction == Direction.RIGHT:
            tank_drive.on_for_seconds(left_speed=speed, right_speed=-speed, seconds=duration/2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Robot movement error: {str(e)}")

def find_color(target_color: str):
    if not color_sensor:
        raise HTTPException(status_code=503, detail="Color sensor not initialized")
    
    # Simple color detection logic - can be enhanced based on specific requirements
    while True:
        current_color = color_sensor.color_name
        if (target_color == "red" and current_color == "Red") or \
           (target_color == "green" and current_color == "Green"):
            tank_drive.off()
            return True
        
        # Search pattern: move forward while scanning
        tank_drive.on(left_speed=30, right_speed=30)

def parse_command(message: str) -> tuple[str, Optional[float]]:
    """Parse command from natural language message."""
    message = message.lower()
    
    # Check for movement commands
    for direction in Direction:
        if direction.value in message:
            duration = 1.0  # default duration
            # Try to extract duration if specified
            import re
            if match := re.search(r'(\d+(?:\.\d+)?)\s*(?:second|sec|s)', message):
                duration = float(match.group(1))
            return ('move', direction.value, duration)
    
    # Check for target commands
    if 'red' in message and 'circle' in message:
        return ('goto', 'red-circle', None)
    if 'green' in message and 'circle' in message:
        return ('goto', 'green-circle', None)
    
    return ('unknown', None, None)

@app.post("/mcp")
async def handle_mcp_message(mcp_message: MCPMessage):
    if not mcp_message.messages or len(mcp_message.messages) == 0:
        raise HTTPException(status_code=400, detail="No messages provided")
    
    last_message = mcp_message.messages[-1]
    command_type, command_value, duration = parse_command(last_message)
    
    try:
        if command_type == 'move':
            current_status.status = "moving"
            current_status.current_action = f"Moving {command_value}"
            move_robot(Direction(command_value), duration or 1.0)
            response = {"status": "success", "message": f"Moved {command_value} for {duration or 1.0} seconds"}
        
        elif command_type == 'goto':
            current_status.status = "navigating"
            current_status.current_action = f"Moving to {command_value}"
            target = Target(command_value)
            if target == Target.RED_CIRCLE:
                find_color("red")
            elif target == Target.GREEN_CIRCLE:
                find_color("green")
            response = {"status": "success", "message": f"Reached {command_value}"}
        
        else:
            raise HTTPException(status_code=400, detail="Unknown command")
        
        current_status.status = "idle"
        current_status.current_action = None
        if command_type == 'goto':
            current_status.position = command_value
        
        return {
            "response": response,
            "context": {
                "robot_status": current_status.dict()
            }
        }
    
    except Exception as e:
        current_status.status = "error"
        current_status.current_action = None
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status")
async def get_status():
    return current_status

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000) 