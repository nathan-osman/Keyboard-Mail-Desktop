#!/usr/bin/python3

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango
from gi.repository import GdkPixbuf

import imaplib
import email
from CREDENTIALS import USERNAME as creds_user, PASSWORD as creds_pass

class Handler():
	"""
	This module takes care of all of the Gtk+ calls made by the GUI.
	"""
	def __init__(self):
		self.state = 0
		# Intiate local objects
		self.builder = Gtk.Builder()
		self.builder.add_from_file('data/main.glade')
		self.w = self.builder.get_object('windowMain')
		self.labelAccount = self.builder.get_object('labelAccount')
		self.imageMail = self.builder.get_object('imageMail')
		self.expanderMailboxes = self.builder.get_object('expanderMailboxes')

	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)

	def test(self, widget, event):
		if self.expanderMailboxes.get_expanded():		# Is it already open?
			self.expanderMailboxes.set_expanded(expanded=False)
		else:
			self.expanderMailboxes.set_expanded(expanded=True)

	def keyHandler(self, widget, event):

		if Gdk.ModifierType.CONTROL_MASK & event.state:
			if Gdk.keyval_name(event.keyval) == 'q':	# Quit the program
				w.destroy()
				Gtk.main_quit()

def get_first_text_block(email_message_instance):
	"""
	Returns the text content of the email message that it's supplied with
	via the email_message_instance variable argument
	"""
	maintype = email_message_instance.get_content_maintype()
	if maintype == 'multipart':
		for part in email_message_instance.get_payload():
			if part.get_content_maintype() == 'text':
				return 'Multipart:\n' + part.get_payload()
	elif maintype == 'text':
		return 'Plaintext:\n' + email_message_instance.get_payload()

def emailStuffs():
	con = imaplib.IMAP4_SSL('imap.gmail.com')

	try:
		con.login_cram_md5(creds_user, creds_pass)
	except Exception as e:
		print (e)
		con.login(creds_user, creds_pass)

	con.select('inbox')
	# Out: list of "folders" aka labels in gmail.
	result, data = con.search(None, "ALL")

	ids = data[0] # data is a list.
	id_list = ids.split() # ids is a space separated string
	latest_email_id = id_list[-1] # get the latest
	check = con.check()

	if result != 'OK':		# Returned code wasn't OK
		print ('Returned:',result)
		quit()

	for num in data[0].split():

		result, data = con.fetch(num, '(RFC822)')

		email_message = email.message_from_string(data[0][1].decode())

		print ('Subject:', email_message['Subject'])

		print ('To:\t',email_message['To'])

		i = 0

		for sendee in email.utils.parseaddr(email_message['From']):
			if i % 2 == 0:			# It's divisible by two, so sendee name
				print ('From:\t',sendee)	# It's the name
			else:
				print ('\t',sendee)				# It's the email address

			i += 1

		print ('Content:')
		print (get_first_text_block(email_message))

	con.close()
	con.logout()

if __name__ == "__main__":

	builder = Gtk.Builder()
	builder.add_from_file('data/main.glade')
	builder.connect_signals(Handler())

	labelAccount = builder.get_object('labelAccount')

	labelAccount.set_text(creds_user.split('@')[0])
	imageMail = builder.get_object('imageMail')
	imageSpam = builder.get_object('imageSpam')

	pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale('data/assets/envelope-grey.svg', 21, 24, False)

	imageMail.set_from_pixbuf(pixbuf)

	pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale('data/assets/mail-spam-grey.svg', 21, 24, False)

	imageSpam.set_from_pixbuf(pixbuf)

	style_provider = Gtk.CssProvider()

	with open('data/gtk.css', 'rb') as css:
		css_data = css.read()

	style_provider.load_from_data(css_data)

	Gtk.StyleContext.add_provider_for_screen(
	    Gdk.Screen.get_default(),
	    style_provider,
	    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
	)

	w = builder.get_object('windowMain')
	w.show_all()
	w.maximize()

	Gtk.main()
