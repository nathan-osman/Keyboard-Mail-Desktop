#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.9
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Started work on HTML formatting of messages.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EMessage:
	
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
				', '.join(self.toaddrs), self.subject, content)
				
def prompt(prompt):
	return input(prompt).strip()

def send(fromaddr, toaddrs, msg):
	
	print('Send reached')
	print(fromaddr, toaddrs)
	
	try:
		print('try')
		with smtplib.SMTP("mail.google.com:587") as server:
			server.ehlo()
			print("ehlo()")
			server.starttls()
			print("tls")
			server.login(credsUSER, credsPASS)
			print("login")
			server.set_debuglevel(1)
			print("Debug Level")
			server.sendmail(fromaddr, toaddrs, msg.as_string())
	except Exception as e:
		print('except')
		print(e.args[0])
		print(e.args)
		if len(e.args) >= 2:
			print(bytes.decode(e.args[1]))

if __name__ =='__main__':

	msg = MIMEMultipart('alternative')
	msg['Subject']	= prompt("Subject: ")
	msg['From']		= prompt("From: ")
	msg['To']		= prompt("To: ").split()
	#fromaddr 	= prompt("From: ")
	#toaddrs		= prompt("To: ").split()	# If you hard-program, it must be a list
	#subject 	= prompt("Subject: ")
	#Deprecated with introduction of MIME
	
	print ('Enter message, end with ^D (Unix/Linux) or ^Z (Windows):')
	
	text = ''
	html = '<html><head></head><body><p>'
			
	while True:
		try:
			line = input()
		except EOFError:
			break
		text = text + '\n' + line
		html += text+'</p>'
	#print ("Message length is",len(text))
	#print ("Message is:",text)
	
	html += '</body></html>'
	
	partPLAINTEXT	= MIMEText(text, 'plain')
	partHTML		= MIMEText(html, 'html')
	
	msg.attach(partPLAINTEXT)
	msg.attach(partHTML)
	
	#msg = EMessage(fromaddr, toaddrs, subject)
	#print(msg)
	
	#body = msg.formatMessage(content)
	#print (body)
	
	fromaddr = msg['From']
	toaddrs  = msg['To']
	
	send(fromaddr, toaddrs, msg)

