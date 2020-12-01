import json
from channels.generic.websocket import WebsocketConsumer
import base64
from pyzbar import pyzbar as pb
from io import BytesIO
from PIL import Image
from django.shortcuts import redirect

from datetime import datetime

from entry.models import Visitor
from entry import views

class Streamer(WebsocketConsumer):
	def connect(self):
		self.accept()

	def disconnect(self, code):
		if code == 0:
			print(code)

	def receive(self, text_data):
		text_data_json = json.loads(text_data)
		imgframe = text_data_json['data']
		value = text_data_json['code']
		data = imgframe.split(',')[1]
		# async_to_sync(self.channel_layer.send)({'type': 'modify_picture', 'ext': ext, 'data': data})
		# image = ext + self.modify_picture(data)
		img = base64.b64decode(data)
		img = BytesIO(img)
		img = Image.open(img)
		if value != 'scan':
			visitor = Visitor.objects.get(id=int(value))
		
		Read = pb.decode(img)
		for ob in Read:
			readData = str(ob.data.rstrip().decode('utf-8'))
			print('readData',readData)
			if value == 'scan':
				visitor = Visitor.objects.filter(token=readData).order_by('-id').first()
				if visitor:
					value = visitor.id
			elif visitor.visit_token:
				if readData == visitor.visit_token:
					visit_time = (datetime.combine(datetime.utcnow().date(), datetime.utcnow().time()) - datetime.combine(visitor.in_time.date(), visitor.in_time.time())).total_seconds()
					print(visit_time)
					if visit_time < 60:
						break
					visitor.out_time = datetime.now()
					visitor.save()
					views.send_normal_email(visitor)
					value = 0
			else:
				visitor.visit_token = readData
				visitor.in_time = datetime.now()
				visitor.save()
				views.send_normal_email(visitor)
				value = 0
		
		dump = json.dumps({'data': imgframe, 'code': value})
		self.send(text_data=dump)