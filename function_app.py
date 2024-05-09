import os
import azure.functions as func
import datetime
import json
import logging
from analyze_frames import analyze_frames
from embedding import embed_text
from extract_frames import extract_frames
from index_frames import index_frames
from index_video import index_video
from storagehandler import StorageHandler

app = func.FunctionApp()


@app.blob_trigger(arg_name="myblob", path="videofiles",
                               connection="AzureBlobStorageConnectionString") 
def VideoIndexer(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")
    
    conn_string = os.environ.get('AzureBlobStorageConnectionString')

    # remove the path from the blob name
    blobname = myblob.name.split('/')[1]
    
    storage_handler = StorageHandler("videofiles", conn_string)
    filebytes = storage_handler.download_file(blobname)

    frames = extract_frames(filebytes, blobname)

    analyze_frames(frames)

    embed_text(frames)

    index_frames(frames, blobname)

