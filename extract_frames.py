import base64
import os
import cv2

from storagehandler import StorageHandler


def extract_frames(video_blob, video_name):        
    # get just the name of the file in video_path without the extension
    video_just_name = os.path.splitext(os.path.basename(video_name))[0]

    temp_folder = os.environ.get('LocalTempFolder')
    # modify frames_folder to include the video name
    frames_folder = os.path.join(temp_folder, "frames", video_just_name)

    video_path = os.path.join(temp_folder, video_name)

    with open(video_path, "wb") as fh:
        fh.write(video_blob)

    return extract_and_upload_frames(video_path, 1, frames_folder)



def extract_and_upload_frames(video_path, target_interval=60, frames_folder='frames'):
    """
    Extract and save frames from a video file at specified intervals.

    :param video_path: Path to the video file.
    :param target_interval: Interval at which to extract and save frames.
    :param frames_folder: Folder where frame images will be saved.
    :return: A list of base64 encoded frames.
    """

    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, total_frames // target_interval)

    # Create the frames folder if it doesn't exist
    os.makedirs(frames_folder, exist_ok=True)

    base64_frames = []
    frame_count = 0
    frame_mapping = []

    while video.isOpened():
        success, frame = video.read()
        if not success:
            break
        if frame_count % frame_interval == 0:
            # base64_frame = resize_and_encode_image(frame)
            # base64_frames.append(base64_frame)

            print(f"Extracted frame_{frame_count}.jpg")
            # Save the frame as an image file
            frame_filename = os.path.join(frames_folder, f"frame_{frame_count}.jpg")
            cv2.imwrite(frame_filename, frame)

            storageHandler = StorageHandler("frames", os.environ.get('AzureBlobStorageConnectionString'))
            frame_url =  storageHandler.storeFileAndGetURL(frame_filename, frames_folder)

            frame_mapping.append({"frame_filename": frame_filename, "frame_url": frame_url}) # Save the mapping

        frame_count += 1

    video.release()
    return frame_mapping


# DELETE IF NOT NEEDED!
def resize_and_encode_image(frame, resize_width=768, resize_height=440, quality=70):
    """
    Resize and encode a video frame into base64 format.

    :param frame: The video frame to be processed.
    :param resize_width: The target width for resizing the frame.
    :param resize_height: The target height for resizing the frame.
    :param quality: The quality of the encoded image.
    :return: Base64 encoded string of the resized frame.
    """
    resized_frame = cv2.resize(frame, (resize_width, resize_height))
    _, buffer = cv2.imencode(".jpg", resized_frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    return base64.b64encode(buffer).decode("utf-8")