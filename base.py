#!/usr/bin/python3

# Keyboard Mail Daemon
# Version: 		0.0.8
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Moved formatMessage() into the EMessage class to make it look
		better, re-arraigned the calls to initialize the msg object
		and to format the body of the email to work with the new system.
		
		Added "if __name__ == '__main__':" clause to make sure that
		the main code is only executed if the program is called, not if
		it is imported as a module, something it probably will be in
		the future.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS
#from email.mime.multipart import MIMEMultipart
#from email.mime.text import MIMEText
# Used for next change in which I introduce HTML formatting of the 
# 	message

class EMessage:
	
	def __init__(self, fromaddr, toaddrs, subject):
		self.fromaddr = fromaddr
		self.toaddrs  = toaddrs
		self.subject  = subject
	
	def send(self, content):
		#username 	= input('GMail username: ')
		#pswd		= input('Password: ')
		# Deprecated by credential storage method 
		#(from credentials import USERNAME, PASSWORD)
		try:
			with smtplib.SMTP('smtp.gmail.com:587') as server:
				server.ehlo()
				server.starttls()
				server.login(credsUSER, credsPASS)
				server.set_debuglevel(1)
				server.sendmail(self.fromaddr, self.toaddrs, content)
	
		except Exception as e:
			print(e.args[0])
			if len(e.args) >= 2:
				print(bytes.decode(e.args[1]))
	
	def formatMessage(self, content):
		rtrnMsg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"
				% (self.fromaddr, ", ".join(self.toaddrs), self.subject,
						content))
		return rtrnMsg
		
				
def prompt(prompt):
	return input(prompt).strip()

if __name__ =='__main__':

	fromaddr 	= prompt("From: ")
	toaddrs		= prompt("To: ").split()	# If you hard-program, it must be a list
	subject 	= prompt("Subject: ")
	
	print ("Enter message, end with ^D (Unix/Linux) or ^Z (Windows):")
	
	# Add the From: and To: headers to the start
	content = ""	
			
	while True:
		try:
			line = input()
		except EOFError:
			break
		content = content + '\n' + line
	#print ("Message length is",len(content))
	#print ("Message is:",content)
	
	msg = EMessage(fromaddr, toaddrs, subject)
	#print(msg)
	
	body = msg.formatMessage(content)
	#print (body)
	
	msg.send(body)

