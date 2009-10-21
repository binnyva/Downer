#!/usr/bin/python
 
import pygtk
pygtk.require('2.0')
import gtk

from action import *

####################################### The GUI Part of the Application ###################################
class App:
	gui = True
	special = ""
	
	def delete_event(self, widget, event, data=None):
		return False

	def destroy(self, widget, data=None):
		gtk.main_quit()
	
	def motion_cb(self, wid, context, x, y, time):
		self.status_bar_message_id = self.status_bar.push(self.status_bar_context_id, "Getting Download Info...")
		# Returning True which means "I accept this data".
		return True
	
	def drop_cb(self, wid, context, x, y, time):
		# Some data was dropped, get the data
		wid.drag_get_data(context, context.targets[-1], time)
		return True
	
	def got_data_cb(self, wid, context, x, y, data, info, time):
		# Got data.
		url = data.get_text()
		self.processUrl(url)
		context.finish(True, False, time)

	def buildGUI(self):
		# create a new window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		self.window.set_geometry_hints(min_width=400, min_height=150)
		
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		
		self.window.drag_dest_set(0, [], 0)
		self.window.connect('drag_motion', self.motion_cb)
		self.window.connect('drag_drop', self.drop_cb)
		self.window.connect('drag_data_received', self.got_data_cb)
		
		self.table = gtk.Table(rows=5, columns=3, homogeneous=False)
		self.window.add(self.table)
		
		self.lab_name = gtk.Label("Name")
		self.ent_name = gtk.Entry()
		self.table.attach(self.lab_name, 0, 1, 0, 1)
		self.table.attach(self.ent_name, 1, 3, 0, 1)
		
		# The secret of the attach coodinates - left_attach, right_attach, top_attach, bottom_attach
		#    0          1          2
		#	0+----------+----------+
		#	 |          |          |
		#	1+----------+----------+
		# 	 |          |          |
		#	2+----------+----------+

		self.lab_url = gtk.Label("URL")
		self.ent_url = gtk.Entry()
		self.table.attach(self.lab_url, 0, 1, 1, 2)
		self.table.attach(self.ent_url, 1, 3, 1, 2)
		
		self.lab_path = gtk.Label("Save To")
		self.ent_path = gtk.Entry()
		self.but_path = gtk.Button("Browse...")
		self.but_path.connect("clicked", self.fileChooser)
		self.table.attach(self.lab_path, 0, 1, 2, 3)
		self.table.attach(self.ent_path, 1, 2, 2, 3)
		self.table.attach(self.but_path, 2, 3, 2, 3)
		
		self.but_save = gtk.Button("Save")
		self.but_save.connect("clicked", self.stageSave)
		self.but_cancel = gtk.Button("Cancel")
		self.but_cancel.connect("clicked", self.destroy)
		self.table.attach(self.but_save, 0, 1, 3, 4)
		self.table.attach(self.but_cancel, 2, 3, 3, 4)
		
		self.status_bar = gtk.Statusbar()      
		self.table.attach(self.status_bar, 0, 3, 4, 5)
		self.status_bar_context_id = self.status_bar.get_context_id("StatusBar Messages")

		self.window.show_all()
	
	# Shows the dialog to choose where the file should be saved to.
	def fileChooser(self, widget):
		file_dialog = gtk.FileChooserDialog("Choose File", None, gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		file_dialog.set_filename(self.ent_path.get_text())
		response = file_dialog.run()
		if response == gtk.RESPONSE_OK:
			filename = file_dialog.get_filename()
			self.ent_path.set_text(filename)
		file_dialog.destroy()
	
	# A drop has happened - now, process the url.
	def processUrl(self, url):
		global action
		print url
		if(self.gui and url != ""): self.ent_url.set_text(url)
		data = action.processUrl(url, True)
		self.url = url
		self.name = data[0]
		self.path = data[1]
		self.special = data[2]
		
		if(self.gui): self.status_bar.remove(self.status_bar_context_id, self.status_bar_message_id)
		
		if(self.gui): self.ent_name.set_text(self.name)
		if(self.gui): self.ent_path.set_text(self.path)
		return [self.name, self.path, self.special]
			
	# Use the values in the GUI and send it to the save function
	def stageSave(self, widget):
		self.save(self.ent_url.get_text(), self.ent_name.get_text(), self.ent_path.get_text(), self.special)
		gtk.main_quit()
	
	# Save the data to the DB.
	def save(self, url, name, path, special):
		global sql
		sql.execute("INSERT INTO Downer(name, url, file_path, special, added_on) VALUES(%s, %s, %s, %s, NOW())", (name, url, path, special))

	# The Constructor. 
	def __init__(self):
		argc = len(sys.argv) - 1
		
		# We have arguments - so GUI not needed.
		if argc:
			self.gui = False
			self.processUrl(sys.argv[1])
			if(argc > 1): 
				self.name = sys.argv[2]
				self.path = action.makePath(self.name)
			
			self.save(self.url, self.name, self.path, self.special)
		
		# No arguments, GUI needed.
		else:
			self.buildGUI()

	# The main function
	def main(self):
		gtk.main()

if __name__ == "__main__":
	app = App()
	if(app.gui): app.main()
