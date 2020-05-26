# Oculomotor
This repo is a university project of UNSW Master of IT course comp9900 Information Technology Project. The original private repo is https://github.com/comp3300-comp9900-term-3-2019/capstone-project-robotic-men. This repo is for final submission and further use.

##  Introduction
This project is a useful application for Double the robot with panoramic view. A iOS client side application use bluetooth to link robot and waitting operation to contol it. A PCServer to send operation from keyboard, receive the panoramic live streamming sent by Insta360 pro camera and use a machine learning module to do object detection. A frontend brower based webpage to show the parnoramic view and date detection result.

## Overview - Architecture
Because the robotic Double has been provided by UNSW to us, a creative idea had been made that is we want to create a functional robot. The idea is the robot can be controlled remotely and the received data of the environment can be shown on PC by its camera. The basic structure of our idea has been shown in the flowchart below.

![alt text](https://github.com/r0bertLiu/Oculomotor/raw/master/Media/Image/graph.png "flowchart")

From this flowchart, the start is from the PC server application in Desktop, command can be sent by clicking the keyboard, and then iPhone gets the command because iphone can communicate with Double Robot. Once the iPhone got the command from PC, it will tell Double Robot what the robot should do, then Double robot do it. 
The robot moves slowly and carefully, most of what you see is the picture coming from the main camera on top of the robot. The camera on the top of the robot which is used for detecting the data of environment, after several steps the data of the environment will be sent nginx rtmp stream server, then nginx rtmp will send the data to  the PC server. Furthermore, there are some side functions which enhancing our main application. For example, Frontend Web UI is used for showing UI and object detection function. 

As the content mentioned in the proposal, all of the tasks has been achieved without self-driving. The reason for this is because of the failure of applying the SDK of the camera and Double robot itself does not support sensors.

## Demonstration videos
### Object detection: https://youtu.be/4kLJ54I2aV4
### Final works: https://youtu.be/GeYtAcq8QY4

## User documentation/manual

Before running the application please follow the steps below to set up the working environment. Firstly, pip install the requirment.txt under PCServer directory.

1. Set up Double Client by following steps
   1) Download iOS client application from our Github repo
   2) Open the app project file in Xcode11 from you OSX device
   3) Change the apple developer ID from: Xcode -> Preferences -> Account
   4) Change the bundle ID from: Targets -> DoubleClient -> General
   5) Link your iOS devices and build application on it
   6) Trust the developer and application on you device
   
2. Set up Camera and live stream 
   SERVERIP represents the IP address of your server pc<br>
    1) Download the nginx from https://github.com/arut/nginx-rtmp-module, override the configure file using /NginxServer/conf/nginx.conf
    2) Run stream server nginx.exe<br>
      it will open the hls stream server at rtmp://SERVERIP:1936/hls
    3) Make sure Insta360 camera and server pc at the same LAN. Connect to Insta360 camera through smartphone app or pc client. Chose streaming mode as Custom Rtmp Server and Live-stream Format as RTMP. Fill in the stream server address and key rtmp://localhost:1936/hls/test into the Insta360 camera live stream setting.(test is stream key)
    4) The frontend client can access the HLS streaming index file from http://localhost:8081/hls/test.m3u8. Modify the frontend file in our project repository: /PCServer/templates/index.html<br>
    Modify the video element(ElementID: 3DVision) source URL to :http://SERVERIP:8081/hls/test.m3u8 to access the hls index file.

3. Set up YoLo (download weights)

    YOLOv3 is a neural network model for object detection. YOLOv3 Tiny is a simplified version of YOLOv3. It works faster but less           accurate. See https://pjreddie.com/darknet/yolo/ 
    for more information.

    These are YOLOv3 & YOLOv3 Tiny models implemented in Tensorflow acquired from:

    https://github.com/kcosta42/Tensorflow-YOLOv3

    The weights for the model are pre-trained on MS COCO dataset and can be acquired from YOLOv3 original authors' website. To use the        model, please download the weights to the folder: ./PCServer/yolov3/weights

    YOLOv3: https://pjreddie.com/media/files/yolov3.weights

    YOLOv3_tiny: https://pjreddie.com/media/files/yolov3-tiny.weights

    The weights are originally in Darknet format, and need to be transformed into Tensorflow format to fit Tensorflow model. To convert     the weight, run convert_weight.py as follow:

    to convert original YOLOv3: python3 convert_weights.py

    to convert YOLOv3_Tiny: python3 convert_weights.py --tiny

    to print help information and exit: python3 convert_weights.py -h

    It may take awhile to finish the process. You will see some Tensorflow checkpoint files appears in ./yolov3./weights once finish.

    Please see 'obj_detection_sample_usage.py' for sample usage of the model.
    
4. Start application and use
    After setting up all environments we described above, now we can start the application and use it. The application should be run by     following steps.
    1)  Go to PCServer directory
    2)  Start the Application by run: python app.py
    3)  The index page should be automatically loaded, if not, open url with:         	  http://127.0.0.1:5000/
    4)  Turn on your iOS device’s Bluetooth and link to Double (if double is correctly connected the double connection status should             show: on-line)
    5)  Tap icon to start DoubleClient application on your iOS device
    6)  Type correct IP address and Port number in DoubleClient. IP and Port number can be found from frontend page
    7)  Click “connect to remote” button to make TCP connection with PCServer
    8)  Click “play” button on frontend web page to start live streaming (you can drag on screen to see panoramic view)
    9)  Click “Start” button to start object detection function
    10) Use keyboard to control the Double, the keyboard usage are: <br>
            W:    move forward <br>
            S:    move backward <br>
            A:    turn left   <br>
            D:    turn Right  <br>
            P:    Park the robot <br> 
            V: 	Stop all actions <br>
            I:   	Pole Up  <br>
            K:    Pole Down <br>




