# Keyboard Mail Daemon
# Version: 		0.0.6
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Introduced the eMessage class that allows for reusable message
		code. It currently accepts only sends the message.
		Initial git version, removed private details and replaced with
		input() for anything that should remain private
"""

import smtplib

class eMessage:
	
	def __init__(self, fromaddr, toaddrs, subject, content):
		self.fromaddr = fromaddr
		self.to 	  = toaddrs
		self.subject  = subject
		self.content  = content
	
	def send(self):
		username 	= input('GMail username: ')
		pswd		= input('Password: ')
		try:
			with smtplib.SMTP('smtp.gmail.com:587') as server:
				server.ehlo()
				server.starttls()
				# Make sure to change these if you're testing this code
				# They're your Gmail username & password
				server.login(username, pswd)
				server.set_debuglevel(1)
				server.sendmail(self.fromaddr, self.to, self.content)
	
		except Exception as e:
			print(e.args[0])
			if len(e.args) >= 2:
				print(bytes.decode(e.args[1]))
			
def formatMessage(fromaddr, to, subject, content):
	rtrnMsg = ("From: %s\r\nTo: %s\r\nSubject: %s\r\n\r\n%s"
				% (fromaddr, ", ".join(to), subject, content))
	return (rtrnMsg)
		
def prompt(prompt):
	return input(prompt).strip()

fromaddr 	= prompt("From: ")
toaddrs		= prompt("To: ").split()
subject 	= prompt("Subject: ")
#fromaddr 	= 'YOUREMAIL@SITE.COM'
#toaddrs	= ['RECIPIENT@SITE.COM']
#subject	= 'Subject'

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

body = formatMessage(fromaddr, toaddrs, subject, content)
#print (body)

msg = eMessage(fromaddr, toaddrs, subject, body)
#print(msg)

msg.send()
