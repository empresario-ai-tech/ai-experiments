# -*- coding: utf-8 -*-
# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
## Setup

To install the dependencies for this script, run:

``` 
pip install google-genai opencv-python pyaudio pillow mss
```

Before running this script, ensure the `GOOGLE_API_KEY` environment
variable is set to the api-key you obtained from Google AI Studio.

Important: **Use headphones**. This script uses the system default audio
input and output, which often won't include echo cancellation. So to prevent
the model from interrupting itself it is important that you use headphones. 

## Run

To run the script:

```
python live_api_starter.py
```

The script takes a video-mode flag `--mode`, this can be "camera", "screen", or "none".
The default is "camera". To share your screen run:

```
python live_api_starter.py --mode screen
```
"""

import asyncio
import base64
import io
import os
import sys
import traceback

import cv2
import pyaudio
import PIL.Image
import mss

import argparse

from IPython import display

from google import genai
from google.genai import types

from pydantic import BaseModel

if sys.version_info < (3, 11, 0):
    import taskgroup, exceptiongroup

    asyncio.TaskGroup = taskgroup.TaskGroup
    asyncio.ExceptionGroup = exceptiongroup.ExceptionGroup

FORMAT = pyaudio.paInt16
CHANNELS = 1
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHUNK_SIZE = 1024

MODEL = "models/gemini-2.0-flash-exp"

DEFAULT_MODE = "none"

client = genai.Client(http_options={"api_version": "v1alpha"})

CONFIG = {
    "generation_config": {
        "response_modalities": ["AUDIO"]
    },
    "speech_config": {
        "voice_config": {
            "prebuilt_voice_config": {
                "voice_name": "Aoede"
            }
        }
    }
}

pya = pyaudio.PyAudio()

# # Set device to GPU if available
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# # Move model to the selected device
# model = torch.hub.load('google/gemini-2.0-flash-exp', 'gemini2_flash_exp')
# model.to(device)

# # Verify GPU detection
# print("CUDA available:", torch.cuda.is_available())
# if torch.cuda.is_available():
#     print("CUDA device count:", torch.cuda.device_count())
#     print("CUDA device name:", torch.cuda.get_device_name(0))

# # Example of moving data to GPU
# def process_data(data):
#     # Move input data to the same device as the model
#     data = data.to(device)
#     output = model(data)
#     return output

class AudioLoop:
    def __init__(self, video_mode=DEFAULT_MODE):
        self.video_mode = video_mode

        self.audio_in_queue = None
        self.out_queue = None

        self.session = None

        self.recipes = {}  # Store recipes in memory
        self.send_text_task = None
        self.receive_audio_task = None
        self.play_audio_task = None

    async def send_text(self):
        while True:
            text = await asyncio.to_thread(
                input,
                "message > ",
            )
            if text.lower() == "q":
                break
            await self.session.send(input=text or ".", end_of_turn=True)

    def _get_frame(self, cap):
        # Read the frameq
        ret, frame = cap.read()
        # Check if the frame was read successfully
        if not ret:
            return None
        # Fix: Convert BGR to RGB color space
        # OpenCV captures in BGR but PIL expects RGB format
        # This prevents the blue tint in the video feed
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = PIL.Image.fromarray(frame_rgb)  # Now using RGB frame
        img.thumbnail([1024, 1024])

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        mime_type = "image/jpeg"
        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_frames(self):
        # This takes about a second, and will block the whole program
        # causing the audio pipeline to overflow if you don't to_thread it.
        cap = await asyncio.to_thread(
            cv2.VideoCapture, 0
        )  # 0 represents the default camera

        while True:
            frame = await asyncio.to_thread(self._get_frame, cap)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

        # Release the VideoCapture object
        cap.release()

    def _get_screen(self):
        sct = mss.mss()
        monitor = sct.monitors[0]

        i = sct.grab(monitor)

        mime_type = "image/jpeg"
        image_bytes = mss.tools.to_png(i.rgb, i.size)
        img = PIL.Image.open(io.BytesIO(image_bytes))

        image_io = io.BytesIO()
        img.save(image_io, format="jpeg")
        image_io.seek(0)

        image_bytes = image_io.read()
        return {"mime_type": mime_type, "data": base64.b64encode(image_bytes).decode()}

    async def get_screen(self):

        while True:
            frame = await asyncio.to_thread(self._get_screen)
            if frame is None:
                break

            await asyncio.sleep(1.0)

            await self.out_queue.put(frame)

    async def send_realtime(self):
        while True:
            msg = await self.out_queue.get()
            await self.session.send(input=msg)

    async def listen_audio(self):
        mic_info = pya.get_default_input_device_info()
        self.audio_stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SEND_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        if __debug__:
            kwargs = {"exception_on_overflow": False}
        else:
            kwargs = {}
        while True:
            data = await asyncio.to_thread(self.audio_stream.read, CHUNK_SIZE, **kwargs)
            await self.out_queue.put({"data": data, "mime_type": "audio/pcm"})

    async def manage_recipe(self, fc) -> str:
        """Manages recipe creation and updates using natural language input."""
        try:
            action = fc.args.get('action')
            recipe_name = fc.args.get('recipe_name')
            changes_text = fc.args.get('changes', '')

            print("action: ", action)
            print("recipe_name: ", recipe_name)
            print("changes_text: ", changes_text)
            
            result = ""
            if action == "get":
                if recipe_name not in self.recipes:
                    result = f"Recipe '{recipe_name}' not found."
                else:
                    result = f"Recipe '{recipe_name}': {self.recipes[recipe_name]}"
            elif action in ["create", "update"]:
                if not changes_text:
                    result = f"Cannot {action} recipe '{recipe_name}' without changes."
                    return result

                # Create a contextual prompt based on the action
                if action == "create":
                    prompt = f"""
                    Create recipe for '{recipe_name}' with the following details:
                    {changes_text}
                    
                    Extract the ingredients and instructions from the above description and format them as a JSON object.
                    """
                else:  # update
                    existing_recipe = self.recipes.get(recipe_name)
                    if not existing_recipe:
                        result = f"Recipe '{recipe_name}' not found. Use create to make a new recipe."
                        return result
                        
                    prompt = f"""
                    Update recipe for '{recipe_name}'
                    
                    Current recipe:
                    Ingredients: {existing_recipe['ingredients']}
                    Instructions: {existing_recipe['instructions']}
                    
                    Requested changes:
                    {changes_text}
                    
                    Provide the complete updated recipe as a JSON object with all ingredients and instructions.
                    """

                model_client = genai.Client()

                # Parse the natural language input using the model
                parse_response = await model_client.aio.models.generate_content(
                    model='gemini-2.0-flash-exp',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=[
                                                'You are a helpful recipe creator and updater.',
                                                'Your mission is to create and update recipes based on natural language input.'
                                            ],
                        response_mime_type='application/json',
                        response_schema=RecipeDetails,
                    )
                )
                
                recipe_details = RecipeDetails.model_validate_json(parse_response.text)
                
                if action == "create":
                    if recipe_name in self.recipes:
                        result = f"Recipe '{recipe_name}' already exists. Use update to modify it."
                    else:
                        self.recipes[recipe_name] = {
                            'ingredients': recipe_details.ingredients,
                            'instructions': recipe_details.instructions
                        }
                        result = f"Created new recipe '{recipe_name}' successfully."
                else:  # update
                    self.recipes[recipe_name].update({
                        'ingredients': recipe_details.ingredients,
                        'instructions': recipe_details.instructions
                    })
                    result = f"Updated recipe '{recipe_name}' successfully."

            print("result: ", result)
            tool_response = types.LiveClientToolResponse(
                function_responses=[types.FunctionResponse(
                    name="manage_recipe",
                    id=fc.id,
                    response={'result': result},
                )]
            )
            print('\n>>> ', tool_response)
            await self.session.send(input=tool_response)

        except Exception as e:
            error_result = f"Error managing recipe: {str(e)}"
            print("error_result: ", error_result)

            tool_response = types.LiveClientToolResponse(
                function_responses=[types.FunctionResponse(
                    name="manage_recipe",
                    id=fc.id,
                    response={'error': error_result},
                )]
            )
            await self.session.send(input=tool_response)

    async def receive_audio(self):
        "Background task to reads from the websocket and write pcm chunks to the output queue"
        while True:
            turn = self.session.receive()
            async for response in turn:
                if data := response.data:
                    self.audio_in_queue.put_nowait(data)
                    continue
                if text := response.text:
                    print(text, end="")
                
                server_content = response.server_content
                if server_content is not None:
                    self.handle_server_content(server_content)
                    continue

                tool_call = response.tool_call
                if tool_call is not None:
                    for fc in tool_call.function_calls:
                        if fc.name == "manage_recipe":
                            print("Calling Managing recipe")
                            asyncio.create_task(self.manage_recipe(fc))
                        elif fc.name == "turn_on_the_lights":
                            asyncio.create_task(self.turn_on_the_lights(fc))
                        elif fc.name == "turn_off_the_lights":
                            asyncio.create_task(self.turn_off_the_lights(fc))
                        elif fc.name == "get_current_weather":
                            asyncio.create_task(self.get_current_weather(fc))

            # If you interrupt the model, it sends a turn_complete.
            # For interruptions to work, we need to stop playback.
            # So empty out the audio queue because it may have loaded
            # much more audio than has played yet.
            while not self.audio_in_queue.empty():
                self.audio_in_queue.get_nowait()

    async def play_audio(self):
        stream = await asyncio.to_thread(
            pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=RECEIVE_SAMPLE_RATE,
            output=True,
        )
        while True:
            bytestream = await self.audio_in_queue.get()
            await asyncio.to_thread(stream.write, bytestream)
    
    def handle_server_content(self, server_content):
        model_turn = server_content.model_turn
        if model_turn:
            for part in model_turn.parts:
                executable_code = part.executable_code
                if executable_code is not None:
                    print('-------------------------------')
                    print(f'``` python\n{executable_code.code}\n```')
                    print('-------------------------------')

                code_execution_result = part.code_execution_result
                if code_execution_result is not None:
                    print('-------------------------------')
                    print(f'```\n{code_execution_result.output}\n```')
                    print('-------------------------------')

        grounding_metadata = getattr(server_content, 'grounding_metadata', None)
        if grounding_metadata is not None:
            display.display(
                display.HTML(grounding_metadata.search_entry_point.rendered_content))

        return
    
    async def get_current_weather(self, fc) -> str:
        """Returns the current weather.

        Args:
        location: The city and state, e.g. San Francisco, CA
        """
        print("Getting current weather")
        weather = """
            As of 12:25 AM EST on Sunday, February 9, 2025, here's the current weather and forecast for Toronto, Ontario:
            Current temperature: 2.5°C
            Current conditions: Partly cloudy
            Forecast for the next 24 hours:
            - 12:25 AM EST: 2.5°C, partly cloudy
            - 1:25 AM EST: 2.5°C, partly cloudy
            - 2:25 AM EST: 2.5°C, partly cloudy
            - 3:25 AM EST: 2.5°C, partly cloudy
            - 4:25 AM EST: 2.5°C, partly cloudy
        """
        tool_response = types.LiveClientToolResponse(
            function_responses=[types.FunctionResponse(
                name="get_current_weather",
                id=fc.id,
                response={'result': weather},
            )]
        )
        print('\n>>> ', tool_response)
        await self.session.send(input=tool_response)

    async def turn_on_the_lights(self, fc):
        print("Turning on the lights")
        tool_response = types.LiveClientToolResponse(
            function_responses=[types.FunctionResponse(
                name="turn_on_the_lights",
                id=fc.id,
                response={'result': 'The lights have been turned on successfully.'},
            )]
        )
        print('\n>>> ', tool_response)

        # Send the tool response first
        await self.session.send(input=tool_response)
        # # Then send a message to narrate the result
        # await self.session.send(input="The lights have been turned on successfully.", end_of_turn=True)

    async def turn_off_the_lights(self, fc):
        print("Turning off the lights")
        tool_response = types.LiveClientToolResponse(
            function_responses=[types.FunctionResponse(
                name="turn_off_the_lights",
                id=fc.id,
                response={'result': 'ok'},
            )]
        )
        print('\n>>> ', tool_response)

        # Send the tool response first
        await self.session.send(input=tool_response)
        # # Then send a message to narrate the result
        # await self.session.send(input="The lights have been turned off successfully.", end_of_turn=True)

    async def run(self, tools=None):
        try:
            if tools is None:
                tools=[]

            CONFIG["tools"] = tools

            async with (
                client.aio.live.connect(model=MODEL, config=CONFIG) as session,
                asyncio.TaskGroup() as tg,
            ):
                self.session = session

                self.audio_in_queue = asyncio.Queue()
                self.out_queue = asyncio.Queue(maxsize=5)

                send_text_task = tg.create_task(self.send_text())
                tg.create_task(self.send_realtime())
                tg.create_task(self.listen_audio())
                if self.video_mode == "camera":
                    tg.create_task(self.get_frames())
                elif self.video_mode == "screen":
                    tg.create_task(self.get_screen())

                tg.create_task(self.receive_audio())
                tg.create_task(self.play_audio())

                await send_text_task
                raise asyncio.CancelledError("User requested exit")

        except asyncio.CancelledError:
            pass
        except (ExceptionGroup if sys.version_info >= (3, 11, 0) else exceptiongroup.ExceptionGroup) as EG:
            self.audio_stream.close()
            traceback.print_exception(EG)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        type=str,
        default=DEFAULT_MODE,
        help="pixels to stream from",
        choices=["camera", "screen", "none"],
    )
    args = parser.parse_args()
    main = AudioLoop(video_mode=args.mode)

    # Add recipe management tool
    manage_recipe = {
        'name': 'manage_recipe',
        'description': 'Manage cooking recipes through voice commands. Get existing recipes, create new ones, or update existing ones.',
        'parameters': {
            'type': 'OBJECT',
            'properties': {
                'action': {
                    'type': 'STRING',
                    'enum': ['create', 'update', 'get'],
                    'description': 'Action to perform: get (retrieve existing recipe), create (make new recipe, changes optional), update (modify existing recipe, changes required)'
                },
                'recipe_name': {
                    'type': 'STRING',
                    'description': 'Name of the recipe to work with'
                },
                'changes': {
                    'type': 'STRING',
                    'description': 'Natural language description of recipe ingredients and instructions. Required for update action, optional for create action, ignored for get action'
                }
            },
            'required': ['action', 'recipe_name']
        }
    }

    class RecipeDetails(BaseModel):
        ingredients: list[str]
        instructions: list[str]

    turn_on_the_lights = {'name': 'turn_on_the_lights'}
    turn_off_the_lights = {'name': 'turn_off_the_lights'}
    get_current_weather = {'name': 'get_current_weather'}

    tools = [
        {'function_declarations': [
            manage_recipe,
            turn_on_the_lights,
            turn_off_the_lights,
            get_current_weather
        ]}
    ]
    asyncio.run(main.run(tools))