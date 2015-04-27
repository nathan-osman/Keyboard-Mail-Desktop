#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.9
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Started work on HTML formatting of messages.
		Still trying to resolve why the server.send_message() function
		is sending QUIT prior to actually sending the message body.
		Also, this commit is to close issue #1, should have been
		"closed" last commit.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# EMessage class deprecated by use of email.mime module
"""class EMessage:
	
	def __init__(self, fromaddr, toaddrs, subject):
		self.fromaddr = fromaddr
		self.toaddrs  = toaddrs
		self.subject  = subject
	
	def send(self, msg):
		#username 	= input('GMail username: ')
		#pswd		= input('Password: ')
		# Deprecated by credential storage method 
		#(from credentials import USERNAME, PASSWORD)
		#try:
			#with smtplib.SMTP('smtp.gmail.com:587') as server:
				#server.ehlo()
				#server.starttls()
				#server.login(credsUSER, credsPASS)
				#server.set_debuglevel(1)
				#server.sendmail(self.fromaddr, self.toaddrs, content)
	
		#except Exception as e:
			#print(e.args[0])
			#if len(e.args) >= 2:
				#print(bytes.decode(e.args[1]))
		quit
	
	def formatMessage(self, content):
		return 'From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s' % (self.fromaddr, 
				', '.join(self.toaddrs), self.subject, content)"""
				
def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddrs, msg):
	# Currently debugging a bug caused by server.sendmail()
	# Disabled the try/except statements so I can get debugging information
	#try:
	with smtplib.SMTP('smtp.gmail.com:587') as server:
		server.set_debuglevel(1)
		server.ehlo()
		server.starttls()
		server.login(credsUSER, credsPASS)
		server.send_message(fromaddr, toaddrs, msg)
	#except Exception as e:
	#	print('except')
	#	print(e.args[0])
	#	print(e.args)

if __name__ =='__main__':

	msg = MIMEMultipart('alternative')
	msg['Subject']	= input("Subject: ")
	msg['From']		= input("From: ")
	msg['To']		= input("To: ").split()
	#fromaddr 	= prompt("From: ")
	#toaddrs	= prompt("To: ").split()	# If you hard-program, it must be a list
	#subject 	= prompt("Subject: ")
	#Deprecated with introduction of MIME
	
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
	
	# Deprecated by use of email.mime module	
	#msg = EMessage(fromaddr, toaddrs, subject)
	#print(msg)	
	#body = msg.formatMessage(content)
	#print (body)
		
	fromaddr = msg['From']
	toaddrs  = msg['To']
	
	send(fromaddr, toaddrs, msg)

