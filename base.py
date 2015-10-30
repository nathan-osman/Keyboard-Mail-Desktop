#!/usr/bin/python3

# Keyboard Mail
# Version: 		0.0.21.0
# Date:			June 7, 2015
# Contributors:	RPiAwesomeness

"""Changelog:
		Working on getting the display of multiple attachments beyond a certain number to work properly.
		Currently they are not working in the slightest, and the approach I was coming at it from is
			flawed. This version will not display multiple attachments correctly.
		Main change in this version is the inclusion of Gtk+ CSS theming via the gtk.css file in the data directory
		UI still does not look as I would like it though.

		This is just a generally crappy version/push :P
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

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

from bs4 import BeautifulSoup

# Custom Modules
from CREDENTIALS import USERNAME as creds_user, PASSWORD as creds_pass

#-----------------------------------------------------------------------
# GUI Code
#-----------------------------------------------------------------------

class FileChooser():

	def __init__(self):

		self.path = None

		dia = Gtk.FileChooserDialog("Please choose a file", w,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		self.add_filters(dia)

		response = dia.run()

		if response == Gtk.ResponseType.OK:
			self.path = dia.get_filename()
		elif response == Gtk.ResponseType.CANCEL:
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

class Handler():

	def __init__(self):
		self.state = 0

	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

	def onSendClicked(self, button):

		# Variables for text
		global to, cc, bcc, subject, partPLAINTEXT, partHTML
		# Variables for objects
		global content, msg, server, attached

		to = entryTo.get_text()
		cc = entryCC.get_text()
		bcc = entryBCC.get_text()
		subject = entrySubject.get_text()
		start, end = textBodyBuffer.get_bounds()
		partPLAINTEXT = textBodyBuffer.get_text(start, end, True)

		# Below is the serialization code for exporting with format tags
		format = textBodyBuffer.register_serialize_tagset()
		exported = textBodyBuffer.serialize(textBodyBuffer, format, start, end)

		exported = exported.decode("latin-1")

		exported = exported.split('<text_view_markup>', 1)
		del exported[0]
		exported[0] = '<text_view_markup>' + str(exported[0])

		exported = exported[0].split('</tags>', 1)
		del exported[0]

		exported = exported[0].split('</text_view_markup>', 1)
		exported = str(exported[0]).replace('\n', ' ')

		soup = BeautifulSoup(exported)

		soupRoot = soup.find_all('text')

		for tag in soupRoot:
			tag.name = 'p'

		soupTags = soup.find_all('apply_tag')

		for tag in soupTags:
			if tag['name'] == 'bold':
				tag.name = 'b'
				del tag['name']
			elif tag['name'] == 'italic':
				tag.name = 'em'
				del tag['name']
			elif tag['name'] == 'underline':
				tag.name = 'u'
				del tag['name']
			elif tag.name == 'text':
				del tag

		partHTML = str(soup.contents[0])

		setup_server()

		partPLAINTEXT, partHTML = body_setup(partHTML)

		content.attach(partPLAINTEXT)	# Add the MIMEText object for the plaintext to the message
		content.attach(partHTML)		# Add the MIMEText object for the HTML to the message

		logging.info('Message length ' +str(len(partPLAINTEXT)))
		print (('Message length ' +str(len(partPLAINTEXT))))

		msg.attach(content)			# Attach the content to the message

		for attachment in attachments:	# Iterate through the list of attachments ...
			msg.attach(attachments[attachment])		# and attach them to the message

		fromaddr = msg['From']		# From in its own string, required as an arg for send()

		# Need to find a way to set the msg['To'] field to have multiple recipients because it will be faster
		# Currently, each message is sent individually to each recipient
		for recip in recipients:		# Iterate through all of the recipients and ...
			send(fromaddr, recip, msg)	# Call the send function individually for each

		print ('Message sent successfully')
		logging.info('Message sent successfully')

		server.quit()						# Done, disconnect from the server

		print ('Server disconnected')
		logging.info('Server disconnected')

		quit()

	def bold(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('bold')
		elif button.get_active() != True:	# Button is "up"/disabled
			del tags_on[tags_on.index('bold')]

	def italic(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('italic')
		elif button.get_active() != True:	# Button is "up"/disabled
			print (button.get_name())
			del tags_on[tags_on.index('italic')]

	def underline(self, button):
		global tags_on
		name = button.get_name()
		if button.get_active():				# Button is "down"/enabled
			tags_on.append('underline')
		elif button.get_active() != True:	# Button is "up"/disabled
			del tags_on[tags_on.index('underline')]

	def alignToggled(self, radiobutton):
		if radiobutton.get_active():
			if radiobutton.get_name() == 'alignLeft':
				print ('Left')
			elif radiobutton.get_name() == 'alignCenter':
				print ('Center')
			elif radiobutton.get_name() == 'alignRight':
				print ('Right')
			elif radiobutton.get_name() == 'alignFill':
				print ('FillOff')
		else:
			if radiobutton.get_name() == 'alignLeft':
				print ('LeftOff')
			elif radiobutton.get_name() == 'alignCenter':
				print ('CenterOff')
			elif radiobutton.get_name() == 'alignRight':
				print ('RightOff')
			elif radiobutton.get_name() == 'alignFill':
				print ('FillOff')

	def undo(self, button):
		print ('Undo')
		pass

	def redo(self, button):
		print ('Redo')
		pass

	def addAttach(self, button):
		global attachments
		attachments = setup_attachment()

	def keyHandler(self, widget, event):

		if Gdk.ModifierType.CONTROL_MASK & event.state:
			if Gdk.keyval_name(event.keyval) == 'q':	# Quit the program
				w.destroy()
				Gtk.main_quit()
			elif Gdk.keyval_name(event.keyval) == 'Down':	# Attachment panel
				if self.state == 0:
					buttonAttach.show()
					self.state = 1
				else:
					buttonAttach.hide()
					self.state = 0

#-----------------------------------------------------------------------
# General Code
#-----------------------------------------------------------------------

def prompt(prompt):
	return input(prompt).strip()

#-----------------------------------------------------------------------
# Message Rich Text Formatting Code
#-----------------------------------------------------------------------

def get_iter_position(buffer):
	return buffer.get_iter_at_mark(buffer.get_insert())

def text_inserted(buffer, iter, char, length):

	if tags_on:
		iter.backward_chars(length)
		for tag in tags_on:
			if tag == 'bold':
				buffer.apply_tag(tag_bold, get_iter_position(buffer), iter)
			if tag == 'italic':
				buffer.apply_tag(tag_italic, get_iter_position(buffer), iter)
			if tag == 'underline':
				buffer.apply_tag(tag_underline, get_iter_position(buffer), iter)
				w.queue_draw()

#-----------------------------------------------------------------------

def attachmentInput(widget, event):

	global attachNameNew

	if event.button == 3: # Right click

		text = widget.get_child().get_text()

		menuitemRemoveAttach.connect('button-press-event', removeAttachment, text, menuAttachments, widget)

		menuAttachments.append(menuitemRemoveAttach)
		menuAttachments.show_all()

		menuAttachments.popup(None, None, None, None, 0, Gtk.get_current_event_time())

def removeAttachment(*data):
	global attachments, text
	del attachments[data[2]]
	data[3].popdown()
	data[4].destroy()
	data = []
	text = ''

def get_message_content():

	global recipients

	to = entryTo.get_text()
	cc = entryCC.get_text()
	bcc = entryBCC.get_text()
	text = entrySubject.get_text()

	msg['Subject'] 	= subject				# Subject
	msg['From']		= creds_user				# From - set by the credential.py file
	recipients		= to.split()			# All of the recipients in list form

	if recipients == '':					# Make sure that there is at least one recipient (need email confirmation)
		logging.info('No recipients given')
		print ("At least one recipient is required. Otherwise, you're",
				"simply sending the message off into pixie land and it",
				"then dies.")
		print ('Returning you to the start')
		main()

	msg['To'] 		= COMMASPACE.join(recipients)	# One long string of recipients, just for MIME standards, not technically needed.
	msg['Date']		= str(formatdate(localtime=True))

	return text

def body_format(text, html):

	partPLAINTEXT	= MIMEText(text, 'plain')	# Create MIMEText object for the plaintext version of the body
	partHTML		= MIMEText(html, 'html')	# Create MIMEText object for the HTML version of the body

	return partPLAINTEXT, partHTML

def setup_attachment():

	global attachments, attachNameNew

	dialogFile = FileChooser()

	path = dialogFile.path

	if path == None:		# No attachment chosen - acceptable result
		logging.info('No attachment selected!')
		print ('No attachment selected!')
		attached = False
	else:				# Attachment chosen
		logging.info('Attachment ' + path + ' chosen.')
		print ('Attachment ' + path + ' chosen.')
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

		attachName = os.path.basename(path)
		print ('attachNameNew:',attachName)
		attachment.add_header('Content-Disposition', 'attachment', filename=attachName)

		attachNameNew = attachName

		if len(attachName) >= 8:
			attachNameNew = attachName[0:5] + '...'

		eventBox = Gtk.EventBox()
		eventBox.set_name('eventBox')
		eventBox.add(Gtk.Label(label = attachNameNew))

		if len(attachments) <= 0:
			if attachName not in attachments:
				boxAttachments.add(eventBox)
				print ('Happening!')
				boxAttachments.show_all()
				eventBox.connect('button-press-event', attachmentInput)
				eventBox = None
		else:
			print ('else')
			menuItem = Gtk.MenuItem()
			menuItem.label = attachNameNew
			menuAttachmentsDropdown.append(menuItem)
			menuAttachmentsDropdown.show_all()
			menuAttachmentsDropdown.popup(None, None, None, None, 0, Gtk.get_current_event_time())

		attachments[attachName] = attachment

	return attachments

def body_setup(partHTML):

		text = get_message_content()		# Get the user's input for the content of the message

		partPLAINTEXT, partHTML = body_format(text, partHTML)	# Get the message parts (plaintext and HTML) for MIME

		logging.info('Message content objects successfully created.')
		print ('Message content objects successfully created.')

		return partPLAINTEXT, partHTML

def setup_server():

	global server

	# Set up connection to server so we don't have repeat it each time
	try:
		server = smtplib.SMTP('smtp.gmail.com:587')	# Connect to smtp.gmail.com, port 587

		logging.info('Connected to Gmail SMTP server successfully')

		server.set_debuglevel(1)					# Set the debug level so we get verbose feedback from the server
		server.ehlo()								# Say EHLO to the server
		server.starttls()							# Attempt to start TLS
		server.login(creds_user, creds_pass)			# Log in to the site with the provided username & password (stored in credentials.py)

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

	# Global variables for the email
	global server, msg, text, content
	# GUI Global Variables - Random
	global w, color
	# GUI Global Variables - Buttons
	global buttonAttach, buttonSend
	# GUI Global Variables - Labels
	global labelFromVar
	# GUI Global Variables - Entries
	global entryTo, entryCC, entryBCC, entrySubject
	# GUI Global Objects - TextViews/TextBuffers
	global textBody, textBodyBuffer
	# GUI Global Objects - Tags
	global tag_bold, tag_italic, tag_underline, tags_on
	# GUI Global Objects - Attachment Stuff
	global menuAttachments, toolbutton2, boxAttachments, menuitemRemoveAttach, menubuttonAttachmentsDropdown
	global menuAttachmentsDropdown, menuItemTemplate
	# Global variables for attachments
	global attachments, attachNames

	# Variable setup
	text = ''
	tags_on = []		# For TextBuffer/TextView formatting

	# Attachment variables
	attachments = {}	# For attachments ... DUH
	attachNameNew = ''
	attachNames = []
	attached = False

	msg = MIMEMultipart('mixed')			# Initialize overarching message as msg
	content = MIMEMultipart('alternative')	# This takes the text/html and stores it for the emai

	builder = Gtk.Builder()
	builder.add_from_file('data/editor.glade')
	builder.connect_signals(Handler())

	buttonAttach = builder.get_object('buttonAttach')
	buttonSend = builder.get_object('buttonSend')
	attachmentsBox = builder.get_object('attachmentsBox')

	entryTo = builder.get_object('entryTo')
	entryCC = builder.get_object('entryCC')
	entryBCC = builder.get_object('entryBCC')
	entrySubject = builder.get_object('entrySubject')

	grid1 = builder.get_object('grid1')
	grid1.set_focus_chain([
		entryTo,
		entryCC,
		entryBCC,
		entrySubject,
	])

	textBody = builder.get_object('textviewBody')
	textBodyBuffer = textBody.get_buffer()

	textBodyBuffer.connect_after('insert-text', text_inserted)
	tag_bold = textBodyBuffer.create_tag("bold", weight=Pango.Weight.BOLD)
	tag_italic = textBodyBuffer.create_tag("italic", style=Pango.Style.ITALIC)
	tag_underline = textBodyBuffer.create_tag("underline", underline=Pango.Underline.SINGLE)

	labelFromVar = builder.get_object('labelFromVar')

	labelAttachments = builder.get_object('labelAttachments')
	imageAttachment = builder.get_object('imageAttachment')

	menuAttachments = builder.get_object('menuAttachments')
	toolbutton2 = builder.get_object('toolbutton2')
	boxAttachments = builder.get_object('boxAttachments')
	menuitemRemoveAttach = builder.get_object('menuitemRemoveAttach')
	menuItemTemplate = builder.get_object('menuitemTemplate')
	menubuttonAttachmentsDropdown = builder.get_object('menubuttonAttachmentsDropdown')
	menuAttachmentsDropdown = builder.get_object('menuAttachmentsDropdown')

	labelFromVar.set_text(creds_user)

	style_provider = Gtk.CssProvider()

	with open('data/gtk.css', 'rb') as css:
		css_data = css.read()

	style_provider.load_from_data(css_data)

	Gtk.StyleContext.add_provider_for_screen(
	    Gdk.Screen.get_default(),
	    style_provider,
	    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)

	w = builder.get_object('window1')
	w.show_all()

	buttonAttach.hide()
	menuItemTemplate.hide()

	Gtk.main()

	quit()

if __name__ =='__main__':

	global attached

	attached = False

	logPath = ('data/logs/'+time.strftime("%m-%d-%Y")+'_'+time.strftime("%I-%M-%S %p")+'.log')

	logging.basicConfig(
		format='%(asctime)s :: %(levelname)s :: %(message)s',
		datefmt='%m/%d/%Y %I:%M:%S %p',
		filename=logPath,
		level=logging.DEBUG)

	logging.info('Program Start')

	main()
