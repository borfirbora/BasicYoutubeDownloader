from urllib import parse
import time
import threading
import asyncio
import globalPluginHandler
from scriptHandler import script
from addonHandler import initTranslation
import gui
import tones
import ui
import api
import wx
import os
import sys
from pathlib import Path
parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_name + "/basic_youtube_downloader")
import pytube

initTranslation()

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	vDownload = None
	pDownload = None
	p_percent = _("No downloading")
	p_quality = None
	p_folder = None
	youtube_link = None
	stop = False
	@script(description=_(
		# Translators: Keystroke detail.
		"It analyzes the link you copied to the clipboard. It starts the appropriate workflow whether it is a video or a playlist."
	), category=_(
		# Translators: Must be addon summary in your language.
		"Basic Youtube Downloader"
	), gesture="kb:NVDA+shift+y")
	def script_checkLink(self, gesture):
		self.bindGesture("kb:NVDA+<","sayProgress")
		self.bindGesture("kb:NVDA+shift+<", "cancelDownload")
		try:
			url = str(api.getClipData())
			self.youtube_link = self.recogniseLink(url)
			title = self.youtube_link.title
			if isinstance(self.youtube_link, pytube.YouTube):
				self.selectFolder(_("Select the folder to download the {title} video").format(title=title))
			elif isinstance(self.youtube_link, pytube.Playlist):
				self.selectFolder(_("Select the folder to download the {title} playlist").format(title=title))
		except OSError:
			self.clearGestureBindings()
			self.bindGestures(self._GlobalPlugin__gestures)
			self.terminate()

	def recogniseLink(self, link):
		if "youtube.com/watch?" in link:
			return pytube.YouTube(link)
		elif "youtube.com/playlist?" in link:
			return pytube.Playlist(link)
		elif "youtu.be/" in link:
			return pytube.YouTube("https://www.youtube.com/watch?v={}".format(parse.urlparse(link).path[1::]))
		else:
			gui.speech.speakMessage(_("It is not a valid link"))
			self.terminate()
			self.clearGestureBindings()
			self.bindGestures(self._GlobalPlugin__gestures)

	def askQuality(self):
		def askGUI():
			dialog = wx.SingleChoiceDialog(None,_(
				# Translators: Asking for quality.
			"Choose your video quality."),_(
				# Translators: The Window title.
			"Choose Quality"),[_("Highest Quality"),_("Lowest Quality")])
			if dialog.ShowModal() == wx.ID_OK:
				self.p_quality = dialog.GetSelection()
				if isinstance(self.youtube_link, pytube.YouTube):
					vDownload = threading.Thread(target=self.downloadVideo,args=(self.p_quality, self.youtube_link, self.p_folder))
					self.vDownload = vDownload
					vDownload.start()
				elif isinstance(self.youtube_link, pytube.Playlist):
					pDownload = threading.Thread(target=self.downloadPlaylist,args=(self.p_quality, self.youtube_link, self.p_folder))
					self.pDownload = pDownload
					pDownload.start()
			else:
				self.terminate()
				self.clearGestureBindings()
				self.bindGestures(self._GlobalPlugin__gestures)
			return None
		wx.CallAfter(askGUI)

	def script_cancelDownload(self, gesture):
		self.stop = True

	def script_sayProgress(self, gesture):
		gui.speech.speakMessage(str(self.p_percent))

	def onProgress(self, stream, chunk,bytes_remaining):
		if self.stop:
			file_name = stream.default_filename
			gui.speech.speakMessage(_("Download of file {file_name} has been cancelled").format(file_name=file_name))
			self.stop = False
			self.clearGestureBindings()
			self.bindGestures(self._GlobalPlugin__gestures)
			raise KeyboardInterrupt(_("Cancelled"))
		total_size = stream.filesize
		bytes_downloaded = total_size - bytes_remaining
		percent = (bytes_downloaded / total_size) * 100
		self.p_percent = _("{percent} percent downloaded").format(percent=int(percent))
		tones.beep(int(percent) * 15, 30)
		gui.speech.speakMessage(self.p_percent)

	def onComplete(self, stream, filepath):
		filepath = os.path.dirname(filepath)
		gui.speech.speakMessage(_("The file was downloaded to {filepath}").format(filepath=filepath))

	def downloadVideo(self, quality, video: pytube.YouTube, f_path):
		video.register_on_complete_callback(self.onComplete)
		video.register_on_progress_callback(self.onProgress)
		if quality == 0:
			d = video.streams.get_highest_resolution()
			d.download(f_path)
		elif quality == 1:
			d = video.streams.get_lowest_resolution()
			d.download(f_path)
		self.clearGestureBindings()
		self.bindGestures(self._GlobalPlugin__gestures)


	def downloadPlaylist(self, quality, playlist: pytube.Playlist, g_path):
		for video in playlist.videos:
			video.register_on_progress_callback(self.onProgress)
			video.register_on_complete_callback(self.onComplete)
			if quality == 0:
				video.streams.get_highest_resolution().download(os.path.join(g_path, playlist.title))
			else:
				video.streams.get_lowest_resolution().download(os.path.join(g_path, playlist.title))
		self.clearGestureBindings()
		self.bindGestures(self._GlobalPlugin__gestures)

	def selectFolder(self, video_title):
		def folderDLG():
			folder = wx.DirDialog(None, video_title, str(Path.home()))
			if folder.ShowModal() == wx.ID_OK:
				self.p_folder = folder.GetPath()
				self.askQuality()
				return folder.GetPath()
			else:
				self.terminate()
				self.clearGestureBindings()
				self.bindGestures(self._GlobalPlugin__gestures)
			return None
		wx.CallAfter(folderDLG)
