#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.13
# Date:			April 29th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Added attachment capabilties (still under work):
		> Added file chooser dialog (still needs work with the GUI)
		> Added ability to send any form of file (complete)
"""

import smtplib, mimetypes, sys, os

from email					import encoders
from email.mime.multipart 	import MIMEMultipart
from email.mime.text 		import MIMEText
from email.mime.audio		import MIMEAudio
from email.mime.image		import MIMEImage
from email.mime.base		import MIMEBase
from email.utils 			import COMMASPACE, formatdate

from gi.repository			import Gtk

# Custom Modules
from credentials 			import USERNAME as credsUSER, PASSWORD as credsPASS

#-----------------------------------------------------------------------

class FileChooserWindow(Gtk.Window):
	
	def __init__(self):
		Gtk.Window.__init__(self, title="Keyboard Mail - Select Attachment")
		
		box = Gtk.Box(spacing=6)
		self.add(box)
		
		button1 = Gtk.Button("Select File")
		button1.connect("clicked", self.on_file_clicked)
		box.add(button1)
	
	def on_file_clicked(self, widget):
		
		global path
		
		dialog = Gtk.FileChooserDialog("Please choose a file", self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		self.add_filters(dialog)
	
		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			print("Open clicked")
			print("File selected: " + dialog.get_filename())
			path = dialog.get_filename()
			dialog.destroy()
		elif response == Gtk.ResponseType.CANCEL:
			print("Cancel clicked")
			dialog.destroy()		
	
	def add_filters(self, dialog):
		filter_any = Gtk.FileFilter()
		filter_any.set_name("Any files")
		filter_any.add_pattern("*")
		dialog.add_filter(filter_any)
		
		filter_text = Gtk.FileFilter()
		filter_text.set_name('Text files')
		filter_text.add_mime_type('text/plain')
		dialog.add_filter(filter_text)
		
		filter_py = Gtk.FileFilter()
		filter_py.set_name('Python files')
		filter_py.add_mime_type('text/x-python')
		dialog.add_filter(filter_py)
		
		filter_png = Gtk.FileFilter()
		filter_png.set_name('PNG images')
		filter_png.add_mime_type('image/png')
		dialog.add_filter(filter_png)
		
		filter_bmp = Gtk.FileFilter()
		filter_bmp.set_name('BMP images')
		filter_bmp.add_mime_type('image/bmp')
		dialog.add_filter(filter_bmp)
		
		filter_img = Gtk.FileFilter()
		filter_img.set_name('Image')
		filter_img.add_mime_type('image/*')
		dialog.add_filter(filter_img)
		
def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddr, msg):		# Sends the message, accepts the from address, to address and message as arguments

	try:
		server.send_message(msg, fromaddr, toaddr)	# Send the message.
	except Exception as e:
		print(e.args)

def get_message_data():
	
	global recipients
	
	msg['Subject']	= input('Subject: ')	# Subject	
	msg['From']		= input('From: ')		# From	
	recipients		= input('To: ').split()	# All of the recipients in list form
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

def content_setup(text, html):
	
	partPLAINTEXT	= MIMEText(text, 'plain')	# Create MIMEText object for the plaintext version of the body
	partHTML		= MIMEText(html, 'html')	# Create MIMEText object for the HTML version of the body
	
	return partPLAINTEXT, partHTML

if __name__ =='__main__':
	
	global attachment, server
	
	win = FileChooserWindow()
	win.connect("delete-event", Gtk.main_quit)
	win.show_all()
	Gtk.main()
	
	msg = MIMEMultipart('mixed')	# Initialize overarching message as msg
	content = MIMEMultipart('alternative')	# This takes the text/html and stores it for the email
	
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
	
	text, html = get_message_data()		# Get the user's input for the content of the message
	
	partPLAINTEXT, partHTML = content_setup(text, html)	# Get the message parts (plaintext and HTML) for MIME
	
	content.attach(partPLAINTEXT)	# Add the MIMEText object for the plaintext to the message
	content.attach(partHTML)		# Add the MIMEText object for the HTML to the message
	
	msg.attach(content)			# Attach the content to the message
	msg.attach(attachment)		# Attach the attachment to the message
	
	# Set up connection to server so we don't have repeat it each time
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')	# Connect to smtp.gmail.com, port 587
		server.set_debuglevel(1)					# Set the debug level so we get verbose feedback from the server
		server.ehlo()								# Say EHLO to the server
		server.starttls()							# Attempt to start TLS
		server.login(credsUSER, credsPASS)			# Log in to the site with the provided username & password (stored in credentials.py)
	except Exception as e:
		print(e.args)
		quit()
	
	fromaddr = msg['From']		# From in its own string, required as an arg for send()
	
	# Need to find a way to set the msg['To'] field to have multiple recipients because it will be faster
	# Currently, each message is sent individually to each recipient
	for recip in recipients:		# Iterate through all of the recipients and ...
		send(fromaddr, recip, msg)	# Call the send function individually for each
	
	server.quit()						# Done, disconnect from the server
