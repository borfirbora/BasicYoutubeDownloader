from keyboardHandler import KeyboardInputGesture
from globalPluginHandler import GlobalPlugin
from scriptHandler import script
from addonHandler import initTranslation
import gui
import tones
import ui
import api
import wx
import os
import sys
parent_dir_name = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(parent_dir_name + "/basic_youtube_downloader")
import pytube

initTranslation()

class GlobalPlugin(GlobalPlugin):
	@script(description=_(
		# Translators: Keystroke detail.
		"Panodaki bağlantıyı inceler, tekil video ya da oynatma listesi olma durumlarına göre iş akışı başlatır. Eğer bağlantı uygun değilse bilgilendirir."
	), category=_(
		# Translators: Must be addon summary in your language.
		"Basit Youtube İndirici"
	), gesture="kb:NVDA+shift+y")
	def script_checkLink(self, gesture):
		try:
			url = api.getClipData()
			self.recogniseLink(url)
			self.askQuality()
		except OSError:
			gui.speech.speakMessage("Panonuz boş")

	def recogniseLink(self, link: str):
		if link.startswith("https://www.youtube.com/watch?"):
			gui.speech.speakMessage("Bu mükemmel bir Youtube linki.")
		elif link.startswith("https://www.youtube.com/playlist?"):
			gui.speech.speakMessage("Bu Mükemmel bir Çalma Listesi linki.")
		else:
			gui.speech.speakMessage("geçerli bir link değil...")

	def askQuality(self):
		def askGUI():
			dialog = wx.SingleChoiceDialog(None,_(
				# Translators: Asking for quality.
			"Video kalitenizi seçin."),_(
				# Translators: The Window title.
			"Kalite seçin"),[_("En yüksek kalite"),_("En düşük kalite")])
			if dialog.ShowModal() == wx.ID_OK:
				self.quality = dialog.GetSelection()
		wx.CallAfter(askGUI)

	def onProgress(self, stream, chunk,bytes_remaining):
		total_size = stream.filesize
		bytes_downloaded = total_size - bytes_remaining
		percent = (bytes_downloaded / total_size) * 100
		self.percent = f"{percent:.0f}% indirildi"

	def onComplete(self, stream, filepath):
		gui.speech.speakMessage(_(f"Dosya, {filepath} konumuna indirildi.."))

	