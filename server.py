from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
from typing import Optional, Dict, Any
import json
import nxt.locator
from nxt.motor import Motor, PORT_A, PORT_B
from nxt.sensor import Color20, PORT_1
import time
import uvicorn

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

app = FastAPI(title="LEGO Mindstorms NXT MCP Server")

# Initialize robot components
try:
    # Find and connect to the first NXT brick
    brick = nxt.locator.find_one_brick()
    # Initialize motors
    left_motor = Motor(brick, PORT_A)
    right_motor = Motor(brick, PORT_B)
    # Initialize color sensor
    color_sensor = Color20(brick, PORT_1)
    print("Successfully connected to NXT brick")
except Exception as e:
    print(f"Warning: Could not initialize NXT components: {e}")
    brick = None
    left_motor = None
    right_motor = None
    color_sensor = None

current_status = RobotStatus(status="idle")

def move_robot(direction: Direction, duration: float = 1.0):
    if not (left_motor and right_motor):
        raise HTTPException(status_code=503, detail="Robot hardware not initialized")
    
    power = 75  # 75% power
    
    try:
        if direction == Direction.FORWARD:
            left_motor.run(power)
            right_motor.run(power)
        elif direction == Direction.BACKWARD:
            left_motor.run(-power)
            right_motor.run(-power)
        elif direction == Direction.LEFT:
            left_motor.run(-power)
            right_motor.run(power)
        elif direction == Direction.RIGHT:
            left_motor.run(power)
            right_motor.run(-power)
        
        # Wait for the specified duration
        time.sleep(duration)
        
        # Stop motors
        left_motor.idle()
        right_motor.idle()
        
    except Exception as e:
        # Make sure motors are stopped even if there's an error
        try:
            left_motor.idle()
            right_motor.idle()
        except:
            pass
        raise HTTPException(status_code=500, detail=f"Robot movement error: {str(e)}")

def find_color(target_color: str):
    if not color_sensor:
        raise HTTPException(status_code=503, detail="Color sensor not initialized")
    
    try:
        # NXT Color sensor values:
        # 1: black, 2: blue, 3: green, 4: yellow, 5: red, 6: white
        target_value = 5 if target_color == "red" else 3  # 5 for red, 3 for green
        
        max_search_time = 10  # Maximum search time in seconds
        start_time = time.time()
        
        while time.time() - start_time < max_search_time:
            current_color = color_sensor.get_color()
            if current_color == target_value:
                left_motor.idle()
                right_motor.idle()
                return True
            
            # Search pattern: move forward while scanning
            left_motor.run(50)
            right_motor.run(50)
            time.sleep(0.1)  # Small delay between readings
        
        # If we get here, we didn't find the color
        left_motor.idle()
        right_motor.idle()
        raise HTTPException(status_code=404, detail=f"Could not find {target_color} circle")
        
    except Exception as e:
        # Make sure motors are stopped
        try:
            left_motor.idle()
            right_motor.idle()
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))

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