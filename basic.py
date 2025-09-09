import os

import dotenv
from google import genai

text = "hey, what can I do in Tel Aviv at summer? Use internet to google for possible activities"

# Initialize client for Vertex AI (uses your gcloud auth / service account)
dotenv.load_dotenv()
client = genai.Client(vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4")

# Call Gemini
chat = client.chats.create(
    model="gemini-2.5-flash-lite",
)

response = chat.send_message(text)
print(response.text)
