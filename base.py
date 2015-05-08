#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.19.1
# Date:			May 7, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Re-named some functions to be more descriptive, moved some code
		around to improve readability.
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

from gi.repository			import Gtk

# Custom Modules
from credentials 			import USERNAME as credsUSER, PASSWORD as credsPASS

# GUI Code
#-----------------------------------------------------------------------

class FileChooser():
	
	def __init__(self):
	
		self.path = None
		
		w = Gtk.Window()
		
		dia = Gtk.FileChooserDialog("Please choose a file", w,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
		
		self.add_filters(dia)
		
		response = dia.run()
		
		if response == Gtk.ResponseType.OK:
			#print("Open clicked")
			#print("File selected: " + dia.get_filename())
			self.path = dia.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
			#print("Cancel clicked")
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

class YesNoDialog():
	
	def __init__(self):
		
		self.response = None
		
		w = Gtk.Window()
		
		ynAttachment = Gtk.MessageDialog(w, 0,
			Gtk.MessageType.QUESTION,
			(Gtk.STOCK_NO, Gtk.ResponseType.NO,
			Gtk.STOCK_YES, Gtk.ResponseType.YES),
			"Keyboard Mail")
			
		ynAttachment.format_secondary_text(
			'Do you want to add an attachment?')
		
		self.response = ynAttachment.run()
		
		ynAttachment.destroy()

class YesNoDialogAgain():
	
	def __init__(self):
		
		self.response = None
		
		w = Gtk.Window()
		
		ynaAttachment = Gtk.MessageDialog(w, 0,
			Gtk.MessageType.QUESTION,
			(Gtk.STOCK_NO, Gtk.ResponseType.NO,
			Gtk.STOCK_YES, Gtk.ResponseType.YES),
			"Keyboard Mail")
			
		ynaAttachment.format_secondary_text(
			'Do you want to add another attachment?')
		
		self.response = ynaAttachment.run()
		
		ynaAttachment.destroy()
	
# General Code
#-----------------------------------------------------------------------

def prompt(prompt):
	return input(prompt).strip()

#-----------------------------------------------------------------------

def get_message_content():
	
	global recipients
	
	msg['Subject']	= input('Subject: ')	# Subject	
	msg['From']		= credsUSER				# From - set by the credential.py file
	recipients		= input('To: ').split()	# All of the recipients in list form
	
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
	
	while Gtk.events_pending():
		Gtk.main_iteration()
		
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
	
	global attachment, server, msg
	
	attached = False
	
	msg = MIMEMultipart('mixed')	# Initialize overarching message as msg
	content = MIMEMultipart('alternative')	# This takes the text/html and stores it for the email
	
	dialogYN = YesNoDialog()
	
	while dialogYN.response == Gtk.ResponseType.YES:
		
		if dialogYN.response == Gtk.ResponseType.YES:
			path, attachment, attached = setup_attachment()
			msg.attach(attachment)
		else:
			pass
			
		dialogYN = YesNoDialogAgain()
			
	while Gtk.events_pending():
		Gtk.main_iteration()
	
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
	
	logPath = ('data/'+time.strftime("%m-%d-%Y")+'_'+time.strftime("%I-%M-%S %p")+'.log')
	
	logging.basicConfig(
		format='%(asctime)s :: %(levelname)s :: %(message)s', 
		datefmt='%m/%d/%Y %I:%M:%S %p',
		filename=logPath, 
		level=logging.DEBUG)
			
	logging.info('Program Start')
	
	main()
