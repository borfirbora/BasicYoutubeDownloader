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
		gui.speech.speakMessage("deneme mesajıdır bu.")
