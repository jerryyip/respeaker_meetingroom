#coding:utf-8

'''
This is the worker thread which handles the STT input(string).
'''

import threading
import Queue
import re


import hashlib
import binascii
from HTMLParser import HTMLParser
import evernote.edam.notestore.NoteStore as NoteStore
from evernote.api.client import EvernoteClient
import evernote.edam.type.ttypes as Types

from functools import wraps
import time

from creds import note_guid, developer_token


if note_guid == '' or developer_token == '':
	print "Please run getGuid.py first to get the note guid and developer token"

###############################################################################

def log(func):
	@wraps(func)
	def wrapper(*args, **kwargs):
		t0 = time.time()
		result = func(*args, **kwargs)
		t1 = time.time()
		print "[%s] time running: %fs" % (func.__name__, t1-t0)
		return result
	return wrapper

###############################################################################

class Worker(threading.Thread):
	# 
	def __init__(self, queue_len = 10):
		threading.Thread.__init__(self)
		self.q = Queue.Queue(queue_len)
		self.client = EvernoteClient(token=developer_token, sandbox=True)
		self.note_store = self.client.get_note_store()
		self.mynote = Types.Note()

		self.thread_stop = False
		self.meetingroom_state = []
		self.last_time_get_state = 0
	# 
	def set_tts(self, tts):
		self.tts = tts
    # 
	def set_player(self, ply):
		self.player = ply
    # 
	def push_cmd(self, cmd):
		print "push_cmd"
		self.q.put(cmd)
    # 
	def wait_done(self):
		self.q.join()
 	# 
	@log
	def play_text(self, text):
		try:
			self.player.play_raw(self.tts.synthesize(text))
		except Exception as e:
			print(e.message)
    # get meetingroom state per 30s
	def get_meetingroom_state(self):
		now = time.time()
		if (now - self.last_time_get_state) > 30:
			self.last_time_get_state = now

			self.mynote = self.note_store.getNote(note_guid, True, False, False, False)
			# 用htmlparser处理note
			hp = myHTML()
			hp.feed(self.mynote.content)
			self.meetingroom_state = hp.data
			print self.meetingroom_state
			hp.close()
    #
	@log
	def reserve_meetingroom(self):
		reserve_lock = 0
		new_note_content = '<?xml version="1.0" encoding="UTF-8"?>'
		new_note_content += '<!DOCTYPE en-note SYSTEM "http://xml.evernote.com/pub/enml2.dtd">'
		new_note_content += '<en-note>'

		for e in self.meetingroom_state:
			if len(e) > 10:
				new_note_content += '<div>'
				new_note_content += e
				new_note_content += '</div>'
			else:
				new_note_content += '<div>'
				new_note_content += e
				if reserve_lock == 0:
					new_note_content += ' stu'
					reserve_lock = 1
					string = "Reserving " + e + " for stu department"
					print(string)
					self.play_text(string)
				new_note_content += '</div>'
		if reserve_lock == 1:
			try:
				new_note_content += '</en-note>'
				self.mynote.content = new_note_content
				self.mynote.updated = 1000 * time.time()
				self.note_store.updateNote(self.mynote)
				print "Successful"
				self.play_text("Successful")
			except Exception as e:
				print(e.message)
				print "failed to upload evernote"
				self.play_text("failed to upload evernote")
		else:
			print "There is no emtry time segment."
			self.play_text("There is no emtry time segment.")
    #
	def run(self):
		# keep running and get cmd from queue 
		while not self.thread_stop:
			self.get_meetingroom_state()
			cmd = ''
			try:
				cmd = self.q.get(timeout=1)
			except:
				continue
			print("worker gets cmd: %s" % cmd)
			self._parse_cmd(cmd)
			self.q.task_done()
			q_len = self.q.qsize()
			if q_len > 0:
				print("still got %d commands to execute." % (q_len,))
    #you could deal with the speech commands in this method
	def _parse_cmd(self, cmd):
		if "meeting room" in cmd:
			self.reserve_meetingroom()
		else:
			self.play_text("I don't know you command.")
	#
	def stop(self):
		self.thread_stop = True
		self.wait_done()

###############################################################################

class myHTML(HTMLParser):
	def __init__(self):
		HTMLParser.__init__(self)
		self.flag = 0
		self.data = []

	def handle_starttag(self, tag, attr):
		if tag == 'div':
			self.flag = 1

	def handle_endtag(self, tag):
		if tag == 'div':
			self.flag = 0

	def handle_data(self, data):
		if self.flag == 1:
			self.data.append(data)



###############################################################################

if __name__ == '__main__':
	pass