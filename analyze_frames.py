import os
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
import requests

def analyze_frames(frames):
    # Create a client for Azure Computer Vision
    credential = CognitiveServicesCredentials(os.environ.get('AzureComputerVisionKey'))
    client = ComputerVisionClient(os.environ.get("AzureComputerVisionEndpoint"), credential)
    # analyzed_frames = []
    for frame in frames:        
        description =  analyze_frame_with_azure_computer_vision(client, frame['frame_url'])
        frame['description'] = description
        # analyzed_frames.append({"frame_url": frame_url,"description": description})
    return frames

def analyze_frame_with_azure_computer_vision(client, frame_url):
    """
    Analyze a video frame using Azure Computer Vision API.

    :param frame: The base64 encoded frame to be analyzed.
    :return: A formatted description of detected objects in the frame.
    """
 


    # Analyze the frame using Azure Computer Vision FROM BLOB STORAGE
    endpoint = os.environ.get("AzureComputerVisionEndpoint")
    subscription_key = os.environ.get('AzureComputerVisionKey')
    headers = {
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscription_key
    }
    params = {
        'features': 'denseCaptions',
        'api-version':'2023-10-01'
    }
    

    
    response = requests.post(endpoint + 'computervision/imageanalysis:analyze?', headers=headers, params=params, json={'url': frame_url})
    response.raise_for_status()
    jsonResult = response.json()

    # Combine the captions with a confidence level greater than 80%
    description = ""
    for caption in jsonResult['denseCaptionsResult']['values']:
        if (caption['confidence'] > .8):
            description += f"{caption['text']}.\n"
    return description