# Keyboard Mail Daemon
# Version: 		0.0.7
# Date:			April 26th, 2015
# Contributors:	RPiAwesomeness
"""Changelog:
		Introduced credential storage method of credentials.py variables
		being imported and used.
		
		Username/password are now stored in credentials.py and are
		accessible via credsUSER and credsPASS respectively.
"""

import smtplib
from credentials import USERNAME as credsUSER, PASSWORD as credsPASS

class eMessage:
	
	def __init__(self, fromaddr, toaddrs, subject, content):
		self.fromaddr = fromaddr
		self.to 	  = toaddrs
		self.subject  = subject
		self.content  = content
	
	def send(self):
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

body = formatMessage(fromaddr, toaddrs, subject, content)
#print (body)

msg = eMessage(fromaddr, toaddrs, subject, body)
#print(msg)

msg.send()
