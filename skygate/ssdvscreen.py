import os, time, glob
from skygate.misc import *
from gi.repository import Gtk, GObject, Pango, GdkPixbuf

class SSDVScreen(object):
	
	def __init__(self, builder):
		self.DisplayedSSDVFileName = ''
		self.SSDVModificationDate = 0
		
		self.frame = builder.get_object("frameSSDV")
		
		self.imageSSDV = builder.get_object("imageSSDV")
		self.boxSSDV = builder.get_object("boxSSDV")
		self.lblSSDVInfo = builder.get_object("lblSSDVInfo")

	def ExtractImageInfoFromFileName(self, FileName):
		print(FileName)
		temp = FileName.split('/')
		temp = temp[1].split('.')
		fields = temp[0].split('_')
		return {'callsign': fields[0], 'imagenumber': fields[1]}

	def GetSSDVFileName(self, SelectedFileIndex=0):
		# Get list of jpg files
		date_file_list = []
		for file in glob.glob('images/*.jpg'):
			stats = os.stat(file)
			lastmod_date = time.localtime(stats[8])
			date_file_tuple = lastmod_date, file
			date_file_list.append(date_file_tuple)

		if len(date_file_list) == 0:
			return ''

		if SelectedFileIndex < 0:
			SelectedFileIndex = 0

		if SelectedFileIndex >= len(date_file_list):
			SelectedFileIndex = len(date_file_list)-1
			
		Index = len(date_file_list) - SelectedFileIndex - 1
			
		selection = sorted(date_file_list)[Index]
		
		return selection[1]

	def ShowFile(self, SelectedFileIndex, Always):
		# 0 means latest file; 1 onwards means 1st file (oldest), etc
		FileName = self.GetSSDVFileName(SelectedFileIndex)
		if FileName != '':
			ModificationDate = time.ctime(os.path.getmtime(FileName))
			if Always or (FileName != self.DisplayedSSDVFileName) or (ModificationDate != self.SSDVModificationDate):
				# self.imageSSDV.set_from_file(FileName)
				pixbuf = GdkPixbuf.Pixbuf.new_from_file(FileName)
				pixbuf = pixbuf.scale_simple(506, 380, GdkPixbuf.InterpType.BILINEAR)
				self.imageSSDV.set_from_pixbuf(pixbuf)

				ImageInfo = self.ExtractImageInfoFromFileName(FileName)
				self.lblSSDVInfo.set_text('Callsign ' + ImageInfo['callsign'] + ', Image ' + ImageInfo['imagenumber'])

			self.DisplayedSSDVFileName = FileName
			self.SSDVModificationDate = ModificationDate
