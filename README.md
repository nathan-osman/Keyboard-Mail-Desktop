# Keyboard-Mail-Desktop
Repository for work on my Keyboard Mail project. This is the repository for the desktop application version, hopefully a mobile app version will follow the first stable release of the desktop version.

## Setup

The setup process is fairly simple if you're on Ubuntu. You may need to change the steps as needed for other Linux distros. Windows instructions will not be coming until later in the release cycle - perhaps on the initial beta release.

All that is required is

* Python 3 (3.4 is what I'm developing on, but any 3.x version should (*in theory*) work.
* BeautifulSoup 4 for Python 3.x (BS4 is the Python module)
* Gtk 3 for Python 3.x

Once you've got Python 3.x installed, simply edit the credentials.py.template file to match your personal email credentials and then rename the file to credentials.py.

From there, simply run `python3 base.py`, and it will launch!

## Notes about the gui_master branch
This is a branch off of master so that I can work on getting the GUI in working order and push updates as I figure them out, without messing up the other, stable master code.

Currently, the GUI *does* work, but it's not at release/merge level yet. You can send message with rich text formatting (that's what the biggest bug (bug #2) is in) and you can set multiple recipients. (5/24/15)

You can also add AN attachment, multiple attachments is not yet in working order - though it will be soon. (5/24/15)

CC/BCC (Carbon Copy/Blind Carbon Copy) also do not work. (5/24/15)

There's also Bug #3 where the cursor tabs in a strange order through the message information fields. This is a very low priority bug. (5/24/15)
