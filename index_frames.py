import os
import uuid
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


def index_frames(frames, video_filename):
    # create a client for Azure AI Search
    search_client = SearchClient(os.environ.get("AzureSearchIndexEndpoint"), os.environ.get("IndexName"), AzureKeyCredential(os.environ.get("AzureSearchIndexKey")))
    index_frames = []
    for frame in frames:

        id = str(uuid.uuid4())

        index_frames.append({
            "id": id,
            "frame_url": frame["frame_url"],
            "description": frame["description"],
            "embedding": frame["embedding"],
            "frame_filename": frame["frame_filename"],
            "video_filename": video_filename
        })


    search_client.upload_documents(documents=index_frames)
    