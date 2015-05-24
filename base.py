#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.20.3
# Date:			May 17, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Adding basic GUI text editing capabilities
		Sub release of 0.20 (.3) is for working on getting rich text formatting in place
		Converting visual rich text to HTML still isn't working, but you can type in rich text now
		Updated onSendClicked, bold, italic, underline, and keyHandler handlers

"""

import smtplib, mimetypes
import sys, os, time
import logging

from email					import encoders
from email.mime.multipart 	import MIMEMultipart
from email.mime.text 		import MIMEText
from email.mime.audio		import MIMEAudio
from email.mime.image		import MIMEImage
from email.mime.base		import MIMEBase
from email.utils 			import COMMASPACE, formatdate

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

from bs4 import BeautifulSoup

# Custom Modules
from credentials 			import USERNAME as credsUSER, PASSWORD as credsPASS

# GUI Code
#-----------------------------------------------------------------------

class FileChooser():
	
	def __init__(self):
	
		self.path = None
		
		dia = Gtk.FileChooserDialog("Please choose a file", w,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		self.add_filters(dia)
		
		response = dia.run()
		
		if response == Gtk.ResponseType.OK:
			self.path = dia.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
			path = None
			
		dia.destroy()
		
	def add_filters(self, dia):
		filter_any = Gtk.FileFilter()
		filter_any.set_name("All files")
		filter_any.add_pattern("*")
		dia.add_filter(filter_any)
		
		filter_py = Gtk.FileFilter()
		filter_py.set_name("Python files")
		filter_py.add_pattern("*.py")
		filter_py.add_pattern("*.pyc")
		filter_py.add_pattern("*.pyo")
		dia.add_filter(filter_py)
		
		filter_img = Gtk.FileFilter()
		filter_img.set_name('Image files')
		with open('data/imglist', 'r') as imgList:
			for img in imgList:
				img = img.strip('\n')
				pattern = '*.' + img
				filter_img.add_pattern(pattern)
		dia.add_filter(filter_img)
		
		filter_docs = Gtk.FileFilter()
		filter_docs.set_name("Document files")
		with open('data/doclist', 'r') as docList:
			for doc in docList:
				doc = doc.strip('\n')
				pattern = '*.' + doc
				filter_docs.add_pattern(pattern)
		dia.add_filter(filter_docs)
		
		filter_spread = Gtk.FileFilter()
		filter_spread.set_name("Spreadsheet files")
		with open('data/spreadlist', 'r') as spreadList:
			for spread in spreadList:
				spread = spread.strip('\n')
				pattern = '*.' + spread
				filter_spread.add_pattern(pattern)
		dia.add_filter(filter_spread)
		
		filter_present = Gtk.FileFilter()
		filter_present.set_name("Presentation files")
		with open('data/presentlist', 'r') as presentList:
			for present in presentList:
				present = present.strip('\n')
				pattern = '*.' + present
				filter_present.add_pattern(pattern)
		dia.add_filter(filter_present)		

class Handler():
	
	def __init__(self):
		global html
		self.state = 0
	
	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)
	
	def onSendClicked(self, button):
		self.to = entryTo.get_text()
		self.cc = entryCC.get_text()
		self.bcc = entryBCC.get_text()
		self.subject = entrySubject.get_text()
		start, end = textBodyBuffer.get_bounds()
		self.content = textBodyBuffer.get_text(start, end, True)

		# Below is the serialization code for exporting with format tags
		format = textBodyBuffer.register_serialize_tagset()	
		exported = textBodyBuffer.serialize(textBodyBuffer, format, start, end)
		
		exported = exported.decode("latin-1")

		exported = exported.split('<text_view_markup>', 1)
		del exported[0]
		exported[0] = '<text_view_markup>' + str(exported[0])

		exported = exported[0].split('</tags>', 1)
		del exported[0]

		exported = exported[0].split('</text_view_markup>', 1)
		exported = str(exported[0]).replace('\n', ' ')

		soup = BeautifulSoup(exported)

		soupTags = soup.find_all('apply_tag')

		for tag in soupTags:

			if tag['name'] == 'bold':
				tag.name = 'b'
				del tag['name']
			elif tag['name'] == 'italic':
				tag.name = 'em'
				del tag['name']
			elif tag['name'] == 'underline':
				tag.name = 'u'
				del tag['name']

		print (soup)

		setup_server()
		
	def bold(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('bold')
		elif button.get_active() != True:	# Button is "up"/disabled
			del tags_on[tags_on.index('bold')]
			
	def italic(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('italic')
		elif button.get_active() != True:	# Button is "up"/disabled
			print (button.get_name())
			del tags_on[tags_on.index('italic')]
	
	def underline(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('underline')
		elif button.get_active() != True:	# Button is "up"/disabled
			del tags_on[tags_on.index('underline')]
	
	def alignToggled(self, radiobutton):
		if radiobutton.get_active():
			if radiobutton.get_name() == 'alignLeft':
				print ('Left')
			elif radiobutton.get_name() == 'alignCenter':
				print ('Center')
			elif radiobutton.get_name() == 'alignRight':
				print ('Right')
			elif radiobutton.get_name() == 'alignFill':
				print ('FillOff')
		else:
			if radiobutton.get_name() == 'alignLeft':
				print ('LeftOff')
			elif radiobutton.get_name() == 'alignCenter':
				print ('CenterOff')
			elif radiobutton.get_name() == 'alignRight':
				print ('RightOff')
			elif radiobutton.get_name() == 'alignFill':
				print ('FillOff')
	
	def undo(self, button):
		print ('Undo')
		pass
	
	def redo(self, button):
		print ('Redo')
		pass
	
	def addAttach(self, button):
		global attachment
		setup_attachment()
	
	def keyHandler(self, widget, event):
		global html, text
		print (Gdk.keyval_name(event.keyval))
		if Gdk.ModifierType.CONTROL_MASK & event.state:
			if Gdk.keyval_name(event.keyval) == 'q':	# Quit the program
				w.destroy()
				Gtk.main_quit()
			elif Gdk.keyval_name(event.keyval) == 'Down':	# Attachment panel
				if self.state == 0:
					buttonAttach.show()
					labelAttachment.hide()
					self.state = 1
				else:
					buttonAttach.hide()
					labelAttachment.show()
					self.state = 0

		if Gdk.keyval_name(event.keyval) == 'Return' and textBody.is_focus():		# User hit enter
			changeMsgFormat('pc')

		if Gdk.keyval_name(event.keyval) == 'BackSpace' and textBody.is_focus():	# User hit backspace
			html = html[:-1]
			text = text[:-1]
#-----------------------------------------------------------------------
# General Code
#-----------------------------------------------------------------------

def prompt(prompt):
	return input(prompt).strip()

#-----------------------------------------------------------------------
# Message Rich Text Formatting Code
#-----------------------------------------------------------------------

def changeMsgFormat(tag):

	global html

	if tag[1] == 'c':
		if tag[0] == 'b':
			html += '</b>'
		if tag[0] == 'i':
			html += '</em>'
		if tag[0] == 'u':
			html += '</u>'
		if tag[0] == 'p':
			html += '</p><p>'
	else:
		if tag[0] == 'b':
			html += '<b>'
		if tag[0] == 'i':
			html += '<em>'
		if tag[0] == 'u':
			html += '<u>'
		if tag[0] == 'p':
			html += '<p>'

def get_iter_position(buffer):
	return buffer.get_iter_at_mark(buffer.get_insert())

def text_inserted(buffer, iter, char, length):

	global html, text

	text += char
	html += char

	if tags_on:
		iter.backward_chars(length)
		print (tags_on)
		for tag in tags_on:
			if tag == 'bold':
				buffer.apply_tag(tag_bold, get_iter_position(buffer), iter)
			if tag == 'italic':
				buffer.apply_tag(tag_italic, get_iter_position(buffer), iter)
			if tag == 'underline':
				buffer.apply_tag(tag_underline, get_iter_position(buffer), iter)
				w.queue_draw()

#-----------------------------------------------------------------------

def get_message_content():
	
	global recipients
	
	to = entryTo.get_text()
	cc = entryCC.get_text()
	bcc = entryBCC.get_text()
	subject = entrySubject.get_text()

	msg['Subject'] 	= subject				# Subject
	msg['From']		= credsUSER				# From - set by the credential.py file
	recipients		= to.split()			# All of the recipients in list form
	
	if recipients == '':					# Make sure that there is at least one recipient (need email confirmation)
		logging.info('No recipients given')
		print ("At least one recipient is required. Otherwise, you're",
				"simply sending the message off into pixie land and it",
				"then dies.")
		print ('Returning you to the start')
		main()
	
	msg['To'] 		= COMMASPACE.join(recipients)	# One long string of recipients, just for MIME standards, not technically needed.
	msg['Date']		= str(formatdate(localtime=True))
	
	# Enter your email
	print ('Enter message, end with ^D (Unix/Linux) or ^Z (Windows):')
	
	text = ''							# Plain Text storage variable
	html = '<html><head></head><body>'	# Initialize html variable with initial, default HTML tags
			
	while True:							# Loops, allowing you to input your message
		try:
			line = input()
		except EOFError:				# Use error catching to do the dirty work of detecting the end of message
			break						# Get out of the infinite loop
		text = text + '\n' + line	# Basic text of email
		html += '<p>'+line+'</p>'	# HTML version with <p> tags added around line
	
	html += '</body></html>'	# Once loop is complete, close all the tags
	
	return text, html

def body_format(text, html):
	
	partPLAINTEXT	= MIMEText(text, 'plain')	# Create MIMEText object for the plaintext version of the body
	partHTML		= MIMEText(html, 'html')	# Create MIMEText object for the HTML version of the body
	
	return partPLAINTEXT, partHTML
	
def setup_attachment():
	
	dialogFile = FileChooser()
		
	path = dialogFile.path
	
	if path == None:		# No attachment chosen - acceptable result
		logging.info('No attachment selected!')
		attached = False
	else:				# Attachment chosen
		logging.info('Attachment ' + path + ' chosen.')
		attached = True

	if attached:		# Attachment given
		
		ctype, encoding = mimetypes.guess_type(path)
		if ctype is None or encoding is not None:
			ctype = 'application/octet-stream'
		maintype, subtype = ctype.split('/', 1)
		
		if maintype == 'text':
			with open(path) as fp:
				attachment = MIMEText(fp.read(), _subtype=subtype)
		elif maintype == 'image':
			with open(path, 'rb') as fp:
				attachment = MIMEImage(fp.read(), _subtype=subtype)
		elif maintype == 'audio':
			with open(path, 'rb') as fp:
				attachment = MIMEAudio(fp.read(), _subtype=subtype)
		else:
			with open(path, 'rb') as fp:
				attachment = MIMEBase(maintype, subtype)
				attachment.set_payload(fp.read())
		encoders.encode_base64(attachment)
		attachment.add_header('Content-Disposition', 'attachment', filename=os.path.basename(path))

	return path, attachment, attached
	
def msg_setup():				
		
		text, html = get_message_content()		# Get the user's input for the content of the message
		
		partPLAINTEXT, partHTML = body_format(text, html)	# Get the message parts (plaintext and HTML) for MIME
		
		logging.info('Message content objects successfully created.')
	
		return partPLAINTEXT, partHTML
		
def setup_server():
	
	# Set up connection to server so we don't have repeat it each time
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')	# Connect to smtp.gmail.com, port 587
		
		logging.info('Connected to Gmail SMTP server successfully')
		
		server.set_debuglevel(1)					# Set the debug level so we get verbose feedback from the server
		server.ehlo()								# Say EHLO to the server
		server.starttls()							# Attempt to start TLS
		server.login(credsUSER, credsPASS)			# Log in to the site with the provided username & password (stored in credentials.py)
		
		logging.info('User logged in successfully')
		
	except Exception as e:
		logging.error('Error during SMTP')
		logging.error('Error:',e.args)
		print(e.args)
		quit()

def send(fromaddr, toaddr, msg):		# Sends the message, accepts the from address, to address and message as arguments

	try:
		server.send_message(msg, fromaddr, toaddr)	# Send the message.
	except Exception as e:
		logging.error('Message failed to send')
		logging.error('Error:',e.args)
		print(e.args)

def main():

	# Global variables for the email
	global attachment, server, msg, text, html
	# GUI Global Variables - Buttons
	global buttonAttach, buttonSend, w
	# GUI Global Variables - Labels
	global labelAttachment
	# GUI Global Variables - Entries
	global entryTo, entryCC, entryBCC, entrySubject
	# GUI Global Objects - TextViews/TextBuffers
	global textBody, textBodyBuffer
	# Gtk tag globals
	global tag_bold, tag_italic, tag_underline, tags_on

	# Variable setup
	text = ''
	html = '<html><body><p>'
	attached = False
	tags_on = []

	msg = MIMEMultipart('mixed')			# Initialize overarching message as msg
	content = MIMEMultipart('alternative')	# This takes the text/html and stores it for the emai
	
	builder = Gtk.Builder()
	builder.add_from_file('data/editor.glade')
	builder.connect_signals(Handler())
	
	buttonAttach = builder.get_object('buttonAttach')
	buttonSend = builder.get_object('buttonSend')
	
	entryTo = builder.get_object('entryTo')
	entryCC = builder.get_object('entryCC')
	entryBCC = builder.get_object('entryBCC')
	entrySubject = builder.get_object('entrySubject')

	textBody = builder.get_object('textviewBody')
	textBodyBuffer = textBody.get_buffer()
	
	textBodyBuffer.connect_after('insert-text', text_inserted)
	tag_bold = textBodyBuffer.create_tag("bold", weight=Pango.Weight.BOLD)
	tag_italic = textBodyBuffer.create_tag("italic", style=Pango.Style.ITALIC)
	tag_underline = textBodyBuffer.create_tag("underline", underline=Pango.Underline.SINGLE)

	labelAttachment = builder.get_object('labelAttachmentBar')
	labelCC = builder.get_object('labelCC')
	labelFromVar = builder.get_object('labelFromVar')

	labelFromVar.set_text(credsUSER)
	
	w = builder.get_object('window1')
	w.show_all()
	
	buttonAttach.hide()
	
	Gtk.main()

	print (html)
	
	partPLAINTEXT, partHTML = msg_setup()
	
	content.attach(partPLAINTEXT)	# Add the MIMEText object for the plaintext to the message
	content.attach(partHTML)		# Add the MIMEText object for the HTML to the message
	
	logging.info('Message length ' +str(len(partPLAINTEXT)))
	
	msg.attach(content)			# Attach the content to the message
	
	setup_server()
	
	fromaddr = msg['From']		# From in its own string, required as an arg for send()
	
	# Need to find a way to set the msg['To'] field to have multiple recipients because it will be faster
	# Currently, each message is sent individually to each recipient
	for recip in recipients:		# Iterate through all of the recipients and ...
		send(fromaddr, recip, msg)	# Call the send function individually for each
	
	logging.info('Message sent successfully.')
	
	server.quit()						# Done, disconnect from the server
	
	logging.info('Server disconnected')
	
	quit()

if __name__ =='__main__':
	
	global attached
	
	attached = False
	
	logPath = ('data/logs/'+time.strftime("%m-%d-%Y")+'_'+time.strftime("%I-%M-%S %p")+'.log')
	
	logging.basicConfig(
		format='%(asctime)s :: %(levelname)s :: %(message)s', 
		datefmt='%m/%d/%Y %I:%M:%S %p',
		filename=logPath, 
		level=logging.DEBUG)
			
	logging.info('Program Start')
	
	main()
