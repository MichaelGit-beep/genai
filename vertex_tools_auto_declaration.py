import os

from google import genai
from google.genai import types


def multiply(a: float, b: float):
    """Returns a * b."""
    print("Calling multiply")
    return a * b


def divide(a: float, b: float):
    """Returns a / b."""
    print("Calling divide")
    return a / b


def call(func_name, args):
    return functions_map[func_name](**args)


def process_response_with_tools_calling(resp):
    if not resp.candidates[0].content.parts[0].function_call:
        result = []
        for candidate in resp.candidates:
            result = [part.text.strip() for part in candidate.content.parts]
        return ".".join(result)

    for part in resp.candidates[0].content.parts:
        result = call(part.function_call.name, part.function_call.args)
        resp = chat.send_message(str(result))
        return process_response_with_tools_calling(resp)


client = genai.Client(
    vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4"
)

multiply_declaration = types.FunctionDeclaration.from_callable(
    callable=multiply, client=client
)
divide_declaration = types.FunctionDeclaration.from_callable(
    callable=divide, client=client
)

tools = types.Tool(function_declarations=[multiply_declaration, divide_declaration])

chat = client.chats.create(
    model="gemini-2.5-flash",
    config=types.GenerateContentConfig(
        tools=[tools],
        temperature=0,
        candidate_count=1,
        thinking_config=types.ThinkingConfig(thinking_budget=-1),
    ),
)


resp = chat.send_message("Can you multiply 2*2 and then divide result by 2?")


functions_map = {"multiply": multiply, "divide": divide}


response = process_response_with_tools_calling(resp)
print(response)
