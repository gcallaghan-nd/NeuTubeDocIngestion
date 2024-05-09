import datetime
import os
import uuid
from azure.storage.blob import BlobServiceClient, BlobBlock, generate_account_sas, ResourceTypes, AccountSasPermissions

# Constants
CONTAINER_NAME = os.environ.get('CONTAINER_NAME')
CONNECTION_STRING = os.environ.get('AzureBlobStorageConnectionString')

# The StorageHandler class contains methods to store files in Azure Blob Storage
# Note: I wrote this in less than an hour using CoPilot and ChatGPT. 

class StorageHandler: 
    # Initialize the StorageHandler class with the connection string and container name
    def __init__(self, container_name, connection_string):
        self.connection_string = connection_string
        self.container_name = container_name

    def storeFiles(self, path, foldername):
        """
        Stores files in the specified path.

        Parameters:
        path (str): The path to the directory where the files will be stored.
        """
        # loop through the files in the directory named path
        for filename in os.listdir(path):
            # get the full path of the file
            file_path = os.path.join(path, filename)
            # check if the file is a file
            if os.path.isfile(file_path):
                # open the file in read mode
                print("Uploading file: ", file_path)
                self.storeFileInBlobContainer(file_path, foldername)

    def storeFileInBlobContainer(self, local_file_path, foldername):
        """
        Stores a file in the specified Azure Blob Storage container.

        Parameters:
        file_path (str): The path to the file to be stored.
        container_name (str): The name of the Azure Blob Storage container.
        """

        # code to store the file in the specified Azure Blob Storage container
        # Get a reference to the container where you want to upload the file
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Get the file name from the local file path
        file_name = local_file_path.split("\\")[-1]

        blob_client = container_client.get_blob_client(f"{foldername}\\{file_name}")

        # Set the chunk size to 4MB
        chunk_size = 4 * 1024 * 1024

        # Open the local file in read-binary mode
        with open(local_file_path, "rb") as file_stream:
            block_id_list = []

            while True:
                buffer = file_stream.read(chunk_size)
                if not buffer:
                    break

                block_id = uuid.uuid4().hex
                block_id_list.append(BlobBlock(block_id=block_id))
                print("Uploading block with ID:", block_id)
                blob_client.stage_block(block_id=block_id, data=buffer, length=len(buffer))

        blob_client.commit_block_list(block_id_list)

        # # Open the local file and read its contents
        # with open(local_file_path, "rb") as data:
        # # Upload the file to the container
        #     container_client.upload_blob(name=file_name, data=data)

    def storeVideoAndGetURL(self, local_file_path, foldername):
        """
        Stores a video file in the specified Azure Blob Storage container and returns the blob URL.
        This function uploads the video file in chunks and returns the URL for accessing the uploaded video.

        Parameters:
        local_file_path (str): The path to the video file to be stored.
        foldername (str): The name of the folder inside the container.

        Returns:
        str: URL of the uploaded video in the Azure Blob Storage.
        """
        print("Initializing Blob Service Client...")
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        print("local_file_path: ", local_file_path)
        print("foldername: ", foldername)

        # Check if the file exists
        if not os.path.isfile(local_file_path):
            print(f"File not found: {local_file_path}")
            return None

        file_name = os.path.basename(local_file_path)
        # Use forward slash for blob paths
        blob_client = container_client.get_blob_client(f"{foldername}/{file_name}")

        print(f"Preparing to upload video: {file_name} to Azure Blob Storage...")

        # Define the chunk size for upload
        chunk_size = 4 * 1024 * 1024  # 4MB chunk size

        with open(local_file_path, "rb") as file_stream:
            block_id_list = []

            while True:
                buffer = file_stream.read(chunk_size)
                if not buffer:
                    break

                block_id = uuid.uuid4().hex
                block_id_list.append(BlobBlock(block_id=block_id))

                print(f"Uploading block with ID: {block_id}")
                blob_client.stage_block(block_id=block_id, data=buffer, length=len(buffer))

        print("Committing uploaded blocks to create final blob...")
        blob_client.commit_block_list(block_id_list)

        blob_url = blob_client.url
        print(f"Upload completed. Blob URL: {blob_url}")

        # Generate SAS token for the blob
        sas_token = generate_account_sas(
            account_name=blob_service_client.account_name,
            account_key=blob_service_client.credential.account_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.datetime.utcnow() + datetime.timedelta(days=30)
        )

        blob_url_with_sas = f"{blob_url}?{sas_token}"

        return blob_url_with_sas

    def storeFileAndGetURL(self, local_file_path, foldername):
        """
        Stores a file (video or image) in the specified Azure Blob Storage container and returns the blob URL and SAS token.
        """
        print("Initializing Blob Service Client...")
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(self.container_name)

        print("local_file_path: ", local_file_path)
        print("foldername: ", foldername)

        # Check if the file exists
        if not os.path.isfile(local_file_path):
            print(f"File not found: {local_file_path}")
            return None

        file_name = os.path.basename(local_file_path)
        blob_client = container_client.get_blob_client(f"{foldername}/{file_name}")

        print(f"Preparing to upload file: {file_name} to Azure Blob Storage...")

        # Define the chunk size for upload
        chunk_size = 4 * 1024 * 1024  # 4MB chunk size
        block_id_list = []

        with open(local_file_path, "rb") as file_stream:
            while True:
                buffer = file_stream.read(chunk_size)
                if not buffer:
                    break

                block_id = uuid.uuid4().hex
                block_id_list.append(BlobBlock(block_id=block_id))
                blob_client.stage_block(block_id=block_id, data=buffer, length=len(buffer))

        print("Committing uploaded blocks to create final blob...")
        blob_client.commit_block_list(block_id_list)

        blob_url = blob_client.url
        print(f"Upload completed. Blob URL: {blob_url}")

        # Generate SAS token
        sas_token = generate_account_sas(
            account_name=blob_service_client.account_name,
            account_key=blob_service_client.credential.account_key,
            resource_types=ResourceTypes(object=True),
            permission=AccountSasPermissions(read=True),
            expiry=datetime.datetime.utcnow() + datetime.timedelta(days=1)
        )

        blob_url_with_sas = f"{blob_url}?{sas_token}"
        print(f"blob_url: {blob_url}")
        print(f"sas_token: {sas_token}")
        print(f"blob_url_with_sas: {blob_url_with_sas}")

        return blob_url_with_sas
    
# create a method that will download a file from the blob storage and return it as a byte array
    def download_file(self, file_path):
        """
        Downloads a file from Azure Blob Storage and returns it as a byte array.

        Parameters:
        file_path (str): The path to the file in Azure Blob Storage.

        Returns:
        bytes: The file content as a byte array.
        """
        # Initialize the Blob Service Client
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(self.container_name)

        # Get the blob client for the specified file
        blob_client = container_client.get_blob_client(file_path)

        # Download the file as a byte array
        file_bytes = blob_client.download_blob().readall()

        return file_bytes
    
    def upload_blob(self, blob, blob_name):
        """
        Uploads a blob to the Azure Blob Storage container.

        Parameters:
        blob (Blob): The blob object to be uploaded.
        """
        blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
        container_client = blob_service_client.get_container_client(self.container_name)

        blob_client = container_client.get_blob_client(blob_name)

        blob_client.upload_blob(blob.data, overwrite=True)