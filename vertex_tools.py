import os
import sys

from google import genai
from google.genai import types

# Initialize client for Vertex AI (uses your gcloud auth / service account)


def get_current_weather(location: str = "Boston, MA"):
    """
    Get the current weather in a given location

    Args:
        location: The city name of the location for which to get the weather.

    """
    # This example uses a mock implementation.
    # You can define a local function or import the requests library to call an API
    return {
        "location": location,
        "temperature": 38,
        "description": "Partly Cloudy",
        "icon": "partly-cloudy",
        "humidity": 65,
        "wind": {"speed": 10, "direction": "NW"},
    }


# https://ai.google.dev/gemini-api/docs/function-calling?example=chart#function-declarations
get_current_weather_func = types.FunctionDeclaration(
    name="get_current_weather",
    description="Get the current weather in a given location",
    # Function parameters are specified in JSON schema format
    parameters={
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name of the location for which to get the weather.",
                "default": {"string_value": "Boston, MA"},
            }
        },
    },
)

# https://ai.google.dev/gemini-api/docs/function-calling?example=chart#function-declarations
schedule_meeting_function = {
    "name": "schedule_meeting",
    "description": "Schedules a meeting with specified attendees at a given time and date.",
    "parameters": {
        "type": "object",
        "properties": {
            "attendees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of people attending the meeting.",
            },
            "date": {
                "type": "string",
                "description": "Date of the meeting (e.g., '2024-07-29')",
            },
            "time": {
                "type": "string",
                "description": "Time of the meeting (e.g., '15:00')",
            },
            "topic": {
                "type": "string",
                "description": "The subject or topic of the meeting.",
            },
        },
        "required": ["attendees", "date", "time", "topic"],
    },
}

# Init client - Auth to GCP project
client = genai.Client(vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4")

# Chat History. Contains from User and Model contents.
contents = [
    types.Content(
        role="user",
        parts=[types.Part(text="Can You check the weather in New York?")],
    )
]

# Config a model and declare tools(function) it has to process the input
config = types.GenerateContentConfig(
    temperature=0,
    max_output_tokens=500,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    tools=[
        types.Tool(
            function_declarations=[
                get_current_weather_func,
                schedule_meeting_function,
            ]
        ),
    ],
)


# Just a wrapper to send messages and get response
def generate_model_content(
    config: types.GenerateContentConfig, contents: types.ContentListUnionDict
) -> types.GenerateContentResponse:
    return client.models.generate_content(
        model="gemini-2.5-flash-lite", config=config, contents=contents
    )


# Do Innitial Reqeust with a question "Can You check the weather in New York?"
response = generate_model_content(config=config, contents=contents)

# If model decides to use one of the declared tools it will return the func name and args
if not response.candidates[0].content.parts[0].function_call:
    print("No function call found in the response.")
    print(response.text)
    sys.exit(0)


# Map tools name to implemented functions
func_map = {"get_current_weather": get_current_weather, "schedule_meeting": None}


for part in response.candidates[0].content.parts:
    function_call = part.function_call
    _func_to_call = function_call.name
    _args = function_call.args
    print(f"Function to call: {_func_to_call}")  # Function to call: get_current_weather
    print(f"Arguments: {_args}")  # Arguments: {'location': 'New York'}

    # Here We Actually executing the function model suggests
    if func_map.get(_func_to_call):
        function_execution_result = func_map[_func_to_call](**function_call.args)
        # Appening all the contents for the final response:
        # 1. Innitial question

        # 2. model tool suggestion from latest response
        contents.append(response.candidates[0].content)

        function_response_part = types.Part.from_function_response(
            name=_func_to_call, response={"result": function_execution_result}
        )

        # 3. Func output
        contents.append(types.Content(role="user", parts=[function_response_part]))


response = generate_model_content(config=config, contents=contents)
print(
    response.text
)  # The weather in New York is partly cloudy with a temperature of 38 degrees and wind speed of 10 mph from the NW.
