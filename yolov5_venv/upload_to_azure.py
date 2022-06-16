import os
import sys
from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient

# CONNECTION_STRING = "HostName=roboiothub.azure-devices.net;DeviceId=dell_webcam;SharedAccessKey=9MFtrUUDjis+hvJ4RAz1cbOC1HwWHS7mkAd7gwXYUm8="

class Upload_to_Azure:
    def __init__(self,connectionString):
        self.__iot_client = IoTHubDeviceClient.create_from_connection_string(connectionString)  

    def store_blob(self, blob_info, file_name):
        try:
            sas_url = "https://{}/{}/{}{}".format(
                blob_info["hostName"],
                blob_info["containerName"],
                blob_info["blobName"],
                blob_info["sasToken"]
            )

            print("\nUploading file: {} to Azure Storage as blob: {} in container {}\n".format(file_name, blob_info["blobName"], blob_info["containerName"]))

            # Upload the specified file
            with BlobClient.from_blob_url(sas_url) as blob_client:
                with open(file_name, "rb") as f:
                    result = blob_client.upload_blob(f, overwrite=True)
                    return (True, result)

        except FileNotFoundError as ex:
            # catch file not found and add an HTTP status code to return in notification to IoT Hub
            ex.status_code = 404
            return (False, ex)

        except AzureError as ex:
            # catch Azure errors that might result from the upload operation
            return (False, ex)

    def upload_img(self, file_name):
        # Connect the client
        self.__iot_client.connect()

        # Get the storage info for the blob
        blob_name = os.path.basename(file_name)
        storage_info = self.__iot_client.get_storage_info_for_blob(blob_name)

        # Upload to blob
        success, result = self.store_blob(storage_info, file_name)

        if success == True:
            print("Upload succeeded. Result is: \n") 
            print(result)
            print()

            self.__iot_client.notify_blob_upload_status(
                storage_info["correlationId"], True, 200, "OK: {}".format(file_name)
            )

        else :
            # If the upload was not successful, the result is the exception object
            print("Upload failed. Exception is: \n") 
            print(result)
            print()

            self.__iot_client.notify_blob_upload_status(
                storage_info["correlationId"], False, result.status_code, str(result)
            )

def main(args):
    
    thisObj=Upload_to_Azure(args[0])

    try:
        print ("IoT Hub file upload sample, press Ctrl-C to exit")
        thisObj.upload_img(args[1])
    except KeyboardInterrupt:
        print ("IoTHubDeviceClient sample stopped")
    finally:
        # Graceful exit
        thisObj.__iot_client.shutdown()


if __name__ == "__main__":
    main()