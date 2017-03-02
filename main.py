#coding:utf-8

'''
This is an demo which shows you how to use respeaker with evernote API at meeting room reservation.
'''


import signal
from respeaker import Microphone
from respeaker import Player
from respeaker.bing_speech_api import BingSpeechAPI


from respeaker import pixel_ring

from worker import Worker
import time

try:
    from creds import BING_KEY
except ImportError:
    print('Get a key from https://www.microsoft.com/cognitive-services/en-us/speech-api and create creds.py with the key')
    sys.exit(-1)


bing = BingSpeechAPI(key=BING_KEY)


mic = Microphone()
player = Player(mic.pyaudio_instance)


myworker = Worker()
myworker.set_tts(bing)
myworker.set_player(player)



mission_completed = False
awake = False

def handle_int(sig, frame):
	global mission_completed

	print "terminating..."
	pixel_ring.off()
	mission_completed = True
	mic.close()
	player.close() 
	myworker.stop()


signal.signal(signal.SIGINT, handle_int)

myworker.start()

while not mission_completed:
	print
	print "*********** wake me up with \"respeaker\" ***************"
	if mic.wakeup('respeaker'):
		data = mic.listen()
		time.sleep(0.5)
		if data:
			try:
				pixel_ring.wait()
				text = bing.recognize(data, language='en-US')
				print
				print('BING recognize:', text.encode('utf-8'))
				myworker.push_cmd(text)
				myworker.wait_done()
			except Exception as e:
				print(e.message)
		pixel_ring.off()

time.sleep(2)







