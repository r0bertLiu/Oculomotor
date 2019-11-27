from flask import Flask, jsonify, render_template, request
from flask import Flask,request,render_template
import json
import numpy as np
import base64
import re
import cv2
import obj_detect
from db2_communication import Db2RemoteController
import webbrowser
import threading


# initialize the application, item detectorm and remote control server
app = Flask(__name__)
detector = obj_detect.Detector(model="yolov3")
controllor = Db2RemoteController()
threading.Thread(target=controllor.db2_remote_controller).start()


# endpoint for index
@app.route('/')
def index():
	_ip = str(controllor.ip_addr)
	_port = str(controllor.port)
	return render_template("index.html", ip=_ip, port=_port)

# endpoint for item detection
@app.route('/screenshot', methods=['POST'])
def get_image():
	# get image data from frontend and transfer it into numpy array
	image_b64 = request.values['imageBase64']
	image_b64 = re.sub('^data:image/.+;base64,', '', image_b64)
	image_data = base64.b64decode(str(image_b64))
	nparr = np.frombuffer(image_data, np.uint8)
	image_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

	# do item detection, jsonify the result and send it back to frontend
	global detector
	result = detector.detect_img(image_np)
	for line in result:
		for i in range(1, len(line)):
			line[i] = int(line[i])

	response = {}
	response['result'] = result
	return jsonify(response)

# endpoint for update robot's status
@app.route('/status', methods=['GET'])
def update_status():

	response = {}
	response['conn'] = controllor.conn_flag
	response['pole'] = controllor.poll_height
	response['park'] = controllor.park_state
	response['battery'] = controllor.battery

	return jsonify(response)

# function for open brower by defualt
def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

# main function
if __name__ == '__main__':
	threading.Timer(1, open_browser).start()
	app.run(debug = True, use_reloader=False)
