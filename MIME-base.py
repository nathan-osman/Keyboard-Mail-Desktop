#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.10
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Basic HTML formatting has been successfully added as well as the
		freeze bugs removed.
		As far as I know, the program should work correctly - the only
		thing that hasn't been yet confirmed is if multiple recipients
		are working. However, it is fairly certain that it is, so I'm
		going ahead with the commit.
		I'm also removing any deprecated code, including the entire
		EMessage class (RIP my dear friend, you served me well) and any
		reference to that class or functions within that class.
		If there is any need to reference that code in the future, please
		refer back to the commit history.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
				
def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddrs, msg):

	try:
		with smtplib.SMTP('smtp.gmail.com:587') as server:
			server.set_debuglevel(1)
			server.ehlo()
			server.starttls()
			server.login(credsUSER, credsPASS)
			server.send_message(msg, fromaddr, toaddrs)
	except Exception as e:
		print(e.args[0])
		print(e.args)

if __name__ =='__main__':

	msg = MIMEMultipart('alternative')
	msg['Subject']	= input('Subject: ')
	msg['From']		= input('From: ')
	recipients		= input('To: ').split()
	msg['To']		= ', '.join(recipients)
	
	print ('Enter message, end with ^D (Unix/Linux) or ^Z (Windows):')
	
	text = ''
	html = '<html><head></head><body>'
			
	while True:
		try:
			line = input()
		except EOFError:
			break
		text = text + '\n' + line	# Basic text of email
		html += '<p>'+line+'</p>'	# HTML version with <p> tags added around line
	
	html += '</body></html>'	# Once loop is complete, close all the tags
	
	partPLAINTEXT	= MIMEText(text, 'plain')
	partHTML		= MIMEText(html, 'html')
	
	msg.attach(partPLAINTEXT)
	msg.attach(partHTML)
		
	fromaddr = msg['From']
	toaddrs  = msg['To']
	
	send(fromaddr, toaddrs, msg)

