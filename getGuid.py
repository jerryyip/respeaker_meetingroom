#coding:utf-8

'''
This is a script to get GUID of notes from your evernote sandbox account.
'''

import evernote.edam.userstore.constants as UserStoreConstants
from evernote.api.client import EvernoteClient
import evernote.edam.notestore.NoteStore as NoteStore

from creds import developer_token


if developer_token == "":
	print "Please fill in your developer token"
	print "To get a developer token, visit " \
			  "https://sandbox.evernote.com/api/DeveloperToken.action"
	exit(1)

client = EvernoteClient(token=developer_token, sandbox=True)

# UserStore是用来获取当前用户的相关信息的对象，用过从EvernoteClient调用get_user_store
# 方法来创建UserStore实例。
user_store = client.get_user_store()

version_ok = user_store.checkVersion(
    "Evernote EDAMTest (Python)",
    UserStoreConstants.EDAM_VERSION_MAJOR,
    UserStoreConstants.EDAM_VERSION_MINOR
)
print "Is my Evernote API version up to date? ", str(version_ok)
print ""
if not version_ok:
    exit(1)

# NoteStore是用来创建更新删除笔记和笔记本，以及查找有关笔记的数据的
note_store = client.get_note_store()

# List all of the notebooks and notes in the user's account
notebooks = note_store.listNotebooks()
print "Found ", len(notebooks), " notebooks:"
for notebook in notebooks:
	print " ├─ ", notebook.name
    # find notes with a notebook guid
	notefilter = NoteStore.NoteFilter()
	notefilter.notebookGuid = notebook.guid
	nmrs = NoteStore.NotesMetadataResultSpec()
	nmrs.includeTitle = True
	for n in note_store.findNotesMetadata(notefilter, 0, 10, nmrs).notes:
		print " │     ", n.title, " GUID:", n.guid

print
print "Please copy the GUID of meetingroom_reservation to worker.py"