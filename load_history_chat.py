import os
from google import genai
from google.genai.types import ModelContent, Part, UserContent

client = genai.Client(vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4")
chat_session = client.chats.create(
    model="gemini-2.5-flash",
    history=[
        {"parts": [{"text": "Hello."}, {"text": "How are you"}], "role": "user"},
        {
            "parts": [{"text": "Great to meet you. What would you like to know?"}],
            "role": "model",
        },
    ],
    # history=[
    #     UserContent(parts=[Part(text="Hello")]),
    #     ModelContent(
    #         parts=[Part(text="Great to meet you. What would you like to know?")],
    #     ),
    # ],
)

chat_session.send_message("what was my first message?")

for history in chat_session.get_history():
    print(history.to_json_dict())
