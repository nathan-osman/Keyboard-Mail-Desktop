#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.11.1
# Date:			April 27th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Fixed bug where only the first of multiple recipients actually
		recieves the message.
		Still need to figure out how to send the message to multiple
		recipients all at once, instead of the current method of one by
		one.
		Micro-fix (.1): Accidentally removed the COMMASPACE variable
		and so line 39 (now 41) didn't work. That has been fixed.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
				
def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddr, msg):		# Sends the message, accepts the from address, to address and message as arguments

	try:
		s.send_message(msg, fromaddr, toaddr)	# Send the message.
	except Exception as e:
		print(e.args)

if __name__ =='__main__':

	msg = MIMEMultipart('alternative')
	msg['Subject']	= input('Subject: ')	# Subject
	
	msg['From']		= input('From: ')		# From
	fromaddr 		= msg['From']			# From in its own string
	
	recipients		= input('To: ').split()	# All of the recipients in list form
	msg['To'] 		= ', '.join(recipients)	# One long string of recipients, just for MIME standards, not technically needed.
	
	# Enter your email
	print ('Enter message, end with ^D (Unix/Linux) or ^Z (Windows):')
	
	text = ''
	html = '<html><head></head><body>'	# Initialize html variable with initial, default HTML tags
			
	while True:							# Loops, allowing you to input your message
		try:
			line = input()
		except EOFError:
			break
		text = text + '\n' + line	# Basic text of email
		html += '<p>'+line+'</p>'	# HTML version with <p> tags added around line
	
	html += '</body></html>'	# Once loop is complete, close all the tags
	
	partPLAINTEXT	= MIMEText(text, 'plain')	# Create MIMEText object for the plaintext version of the body
	partHTML		= MIMEText(html, 'html')	# Create MIMEText object for the HTML version of the body
	
	msg.attach(partPLAINTEXT)	# Add the MIMEText object for the plaintext to the message
	msg.attach(partHTML)		# Add the MIMEText object for the HTML to the message
	
	# Set up connection to server so we don't have  to do it manually each time...
	
	try:
		s = smtplib.SMTP('smtp.gmail.com:587')	# Connect to the smtp.gmail.com site
		s.set_debuglevel(1)						# Set the debug level so we get verbose feedback from the server
		s.ehlo()								# Say EHLO to the server
		s.starttls()							# Attempt to start TLS
		s.login(credsUSER, credsPASS)			# Log in to the site with the provided username & password (stored in credentials.py)
	except Exception as e:
		print(e.args)
	
	# Need to find a way to set the msg['To'] field to have multiple recipients because it will be faster.
	# Currently, each message is sent individually to each recipient.	
	for recip in recipients:		# Iterate through all of the recipients and ...
		send(fromaddr, recip, msg)	# Call the send function individually for each.
	
	s.quit()						# Done, disconnect from the server
