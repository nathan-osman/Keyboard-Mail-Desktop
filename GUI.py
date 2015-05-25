# GUI Code
#-----------------------------------------------------------------------

import gi.repository
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, Pango

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
		global html
		self.state = 0
	
	def onDeleteWindow(self, *args):
		Gtk.main_quit(*args)
	
	def onSendClicked(self, button):
		self.to = entryTo.get_text()
		self.cc = entryCC.get_text()
		self.bcc = entryBCC.get_text()
		self.subject = entrySubject.get_text()
		start, end = textBodyBuffer.get_bounds()
		self.content = textBodyBuffer.get_text(start, end, True)

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

		print (soup)

		setup_server()
		
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
		global attachment
		setup_attachment()
	
	def keyHandler(self, widget, event):
		global html, text
		print (Gdk.keyval_name(event.keyval))
		if Gdk.ModifierType.CONTROL_MASK & event.state:
			if Gdk.keyval_name(event.keyval) == 'q':	# Quit the program
				w.destroy()
				Gtk.main_quit()
			elif Gdk.keyval_name(event.keyval) == 'Down':	# Attachment panel
				if self.state == 0:
					buttonAttach.show()
					labelAttachment.hide()
					self.state = 1
				else:
					buttonAttach.hide()
					labelAttachment.show()
					self.state = 0

#-----------------------------------------------------------------------
# Message Rich Text Formatting Code
#-----------------------------------------------------------------------

def get_iter_position(buffer):
	return buffer.get_iter_at_mark(buffer.get_insert())

def text_inserted(buffer, iter, char, length):

	global html, text

	text += char
	html += char

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

builder = Gtk.Builder()
builder.add_from_file('data/editor.glade')
builder.connect_signals(Handler())

buttonAttach = builder.get_object('buttonAttach')
buttonSend = builder.get_object('buttonSend')

entryTo = builder.get_object('entryTo')
entryCC = builder.get_object('entryCC')
entryBCC = builder.get_object('entryBCC')
entrySubject = builder.get_object('entrySubject')

textBody = builder.get_object('textviewBody')
textBodyBuffer = textBody.get_buffer()

textBodyBuffer.connect_after('insert-text', text_inserted)
tag_bold = textBodyBuffer.create_tag("bold", weight=Pango.Weight.BOLD)
tag_italic = textBodyBuffer.create_tag("italic", style=Pango.Style.ITALIC)
tag_underline = textBodyBuffer.create_tag("underline", underline=Pango.Underline.SINGLE)

labelAttachment = builder.get_object('labelAttachmentBar')
labelCC = builder.get_object('labelCC')
labelFromVar = builder.get_object('labelFromVar')

w = builder.get_object('window1')
