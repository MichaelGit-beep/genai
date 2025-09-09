import os

import dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field


class Text(BaseModel):
    type: str
    text: str


class SlackBlockModelResponse(BaseModel):
    type: str
    text: Text


# {
#     "type": "section",
#     "text": {
#         "type": "mrkdwn",
#         "text": f"AI Summary: {ai_summary}",
#     },
# },

text = "hey"

# Initialize client for Vertex AI (uses your gcloud auth / service account)
dotenv.load_dotenv()
client = genai.Client(
    vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4"
)


chat = client.chats.create(
    model="gemini-2.5-flash-lite",
    config=types.GenerateContentConfig(
        temperature=0,  # Disable to make responses more predictable
        max_output_tokens=200,  # https://ai.google.dev/gemini-api/docs/pricing https://ai.google.dev/gemini-api/docs/tokens?lang=python
        thinking_config=types.ThinkingConfig(
            thinking_budget=0  # 0 - dissalbed, -1 auto. When enabled - requires more tokens
        ),  # https://ai.google.dev/gemini-api/docs/thinking
        response_mime_type="application/json",
        response_schema=SlackBlockModelResponse,
    ),
)


while True:
    response = chat.send_message(input(">: "))
    print(response.text)
    print(len(response.text))
