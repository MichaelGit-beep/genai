import os
from google import genai
from google.genai.types import ModelContent, Part, UserContent

client = genai.Client(vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4")

history = [
    {"parts": [{"text": "Hello."}, {"text": "How are you"}], "role": "user"},
    {
        "parts": [{"text": "Great to meet you. What would you like to know?"}],
        "role": "model",
    },
]
history.append(UserContent(parts=[Part(text="what was my first message?")]))
respond = client.models.generate_content(model="gemini-2.5-flash", contents=history)
print(respond.text)
