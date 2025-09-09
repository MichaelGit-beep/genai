import os
import sys

import dotenv
from google import genai
from google.genai import types

# Initialize client for Vertex AI (uses your gcloud auth / service account)


def list_pods(namespace: str) -> list[str]:
    """
    Get pods in provided namespace
    Args:
        namespace: kubernetes namespace name
    """

    return [f"{namespace}/podA", f"{namespace}/podB"]


def list_namespaces() -> list[str]:
    """
    Get list of all namespaces
    """

    return ["databases", "services"]


def get_pod_status(podname: str, namespace: str) -> str:
    """
    Return Status Of Selected Pod

    Args:
        podname: pod name
        namespace: kubernetes namespace
    Returns:
        Pod status
    """

    return ["Ready"]

# Init client - Auth to GCP project
dotenv.load_dotenv()
client = genai.Client(
    vertexai=True, project=os.environ["GCP_PROJECT"], location="europe-west4"
)

# Chat History. Contains from User and Model contents.
contents = [
    types.Content(
        role="user",
        parts=[types.Part(text="List all available kubernetes namespaces then check the status for each pod")],
    )
]

# Config a model and declare tools(function) it has to process the input
config = types.GenerateContentConfig(
    temperature=0,
    max_output_tokens=500,
    thinking_config=types.ThinkingConfig(thinking_budget=0),
    tools=[get_pod_status, list_namespaces, list_pods],
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


print(response.text) 
# The status of databases/podA is Ready.
# The status of databases/podB is Ready.
# The status of services/podA is Ready.
# The status of services/podB is Ready.