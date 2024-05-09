import os
from openai import AzureOpenAI

def embed_text(frames):
        client = AzureOpenAI(
            azure_endpoint=os.environ.get("AzureOpenAIEndpoint"),
            api_key=os.environ.get("AzureOpenAIKey"),
            api_version=os.environ.get("AzureOpenAIVersion")
        )

        for frame in frames:
            response = client.embeddings.create(input=frame["description"], model=os.environ.get("EmbeddingModel"))
            frame["embedding"] = response.data[0].embedding

        return frames