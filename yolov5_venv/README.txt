FILES

detect.py # original
detectv2.py # edits in run section: window size, img source, weights
detectv3.py # added facial blur
detectv4.py # upload to Azure IoT hub

COMMANDS

# Run this command to
## detect classes from webcam
## use weights in yolov5n.pt
## save cropped images of detected classes

>python detectv3.py --source 0 --weights yolov5n.pt --save-crop
>python detectv4.py --source 0 --weights yolov5n.pt --connection_string "<connection string>" --upload_images
