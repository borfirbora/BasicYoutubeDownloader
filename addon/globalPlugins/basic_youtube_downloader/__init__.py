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
	@script(
		# Description
		# TRANSLATORS: Description of the starting script.
		description=_("Panoya kopyalanmış Youtube Bağlantısını algılar."),
		# Category
		# TRANSLATORS: Category name of the script.
		category=_("Basit Youtube İndirici"),
		gesture="kb:NVDA+alt+y"
	)
	def script_startBYD(self, gesture: KeyboardInputGesture):
		gui.speech.speakMessage(_(f"değişik bir eklenti"))
