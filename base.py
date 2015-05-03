#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.17
# Date:			May 2, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Added logging - logs are now stored in the data directory.
		Added a bunch of error handling.
		Moved a bunch of code from the if __name__ == '__main__' statement
		to the main() function which gets called from within the previous
		if statement for easier management.
"""

import smtplib, imaplib, mimetypes
import sys, os, time
import logging

from email					import encoders
from email.mime.multipart 	import MIMEMultipart
from email.mime.text 		import MIMEText
from email.mime.audio		import MIMEAudio
from email.mime.image		import MIMEImage
from email.mime.base		import MIMEBase
from email.utils 			import COMMASPACE, formatdate

# Tkinter GUI imports
import tkinter
from tkinter import filedialog

# Custom Modules
from credentials 			import USERNAME as credsUSER, PASSWORD as credsPASS

#-----------------------------------------------------------------------

def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddr, msg):		# Sends the message, accepts the from address, to address and message as arguments

	try:
		server.send_message(msg, fromaddr, toaddr)	# Send the message.
	except Exception as e:
		logging.error('Message failed to send')
		logging.error('Error:',e.args)
		print(e.args)

def get_message_data():
	
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

def content_setup(text, html):
	
	partPLAINTEXT	= MIMEText(text, 'plain')	# Create MIMEText object for the plaintext version of the body
	partHTML		= MIMEText(html, 'html')	# Create MIMEText object for the HTML version of the body
	
	return partPLAINTEXT, partHTML
	
def setup_attachment():
	
	root = tkinter.Tk()
	root.withdraw()
	
	path = filedialog.askopenfilename()
	
	print (path)
	
	if path == '':		# No attachment chosen - acceptable result
		logging.info('No attachment selected!')
		attached = False
	else:				# Attachment chosen
		logging.info('Attachment ' + path + ' chosen.')
		attached = True
			
	return path, attached
	
def msg_setup(path=''):

	if path != '':		# Attachment given
		
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
		
		logging.info('Message content objects successfully created.')
	
		return partPLAINTEXT, partHTML, attachment
		
	else:				# No attachment provided
		
		logging.info('No attachment')
		
		text, html = get_message_data()		# Get the user's input for the content of the message
		
		partPLAINTEXT, partHTML = content_setup(text, html)	# Get the message parts (plaintext and HTML) for MIME
		
		logging.info('Message content objects successfully created.')
		
		return partPLAINTEXT, partHTML
		
def main():
	
	global attachment, server, msg
	
	msg = MIMEMultipart('mixed')	# Initialize overarching message as msg
	content = MIMEMultipart('alternative')	# This takes the text/html and stores it for the email
	
	path, attached = setup_attachment()
	
	if attached:					# Attachment is there
		partPLAINTEXT, partHTML, attachment = msg_setup(path)
	else:							# No attachment
		partPLAINTEXT, partHTML = msg_setup()
	
	content.attach(partPLAINTEXT)	# Add the MIMEText object for the plaintext to the message
	content.attach(partHTML)		# Add the MIMEText object for the HTML to the message
	
	logging.info('Message length ' +str(len(partPLAINTEXT)))
	
	msg.attach(content)			# Attach the content to the message
	
	if attached:				# Attachment is there
		msg.attach(attachment)		# Attach the attachment to the message
	
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
	
	logPath = ('data/'+time.strftime("%d-%m-%Y")+'_'+time.strftime("%I-%M-%S %p"))
	
	logging.basicConfig(
		format='%(asctime)s :: %(levelname)s :: %(message)s', 
		datefmt='%m/%d/%Y %I:%M:%S %p',
		filename=logPath, 
		level=logging.DEBUG)
			
	logging.info('Program Start')
	
	main()
