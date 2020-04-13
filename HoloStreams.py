#!/usr/bin/env python

import os 
import sys
import json
import time
import json
import yaml
import json
# Website Parsing
import webbrowser
import requests
import threading
from bs4 import BeautifulSoup

from PyQt5.QtWidgets import QMainWindow, QAction, QLabel, QWidget, QLineEdit, QComboBox, QPushButton, QCheckBox, QApplication, QMessageBox
from PyQt5.QtCore import Qt, QTimer, QProcess
from PyQt5.QtGui import QIcon, QPixmap

class HoloLiveMember():

	branch = "" # main/ID/Stars/CN

	name = ""
	channel_id = ""
	photoPath = ""
	isLive = False

	videoid = set()

	def __init__(self, name, channel_id, devision, isLive,photopath,branch):
		self.devision = devision
		self.channel_id = channel_id
		self.name = name
		self.isLive = isLive
		self.photoPath = photopath
		self.branch = branch
		self.old_video_id_list = []

	def addElements(self, container,x,y, buttontext):
		self.pfplabel = QLabel(container)
		Pixmap = QPixmap(self.photoPath)
		newPixmap = Pixmap.scaled(64, 64, Qt.KeepAspectRatio)
		self.pfplabel.setPixmap(newPixmap)
		self.pfplabel.resize(64,64)
		self.pfplabel.move(x,y)
		
		self.livebutton = QPushButton(container)
		self.livebutton.clicked.connect(self.openLiveStream)
		self.livebutton.setText(buttontext)
		self.livebutton.move(x+84, y+12)
	
	def openLiveStream(self):
		if self.isLive:
			for videos in self.videoid:
				webbrowser.open("https://www.youtube.com/watch?v=" + videos)
		else:
			print("Not live")
	
	def updateLiveStatus(self, offline, live):
		
		if self.isLive:
			self.livebutton.setText(live)
		else:
			self.livebutton.setText(offline)

# --- 	
# Thank you so much for this amazing code pusaitou https://github.com/pusaitou/mikochiku_alarm 
# I only slighty changed it to support the class model

	def check_live(self,sort, offline, live):
		if sort == self.branch:
			buff_video_id_set = self.get_live_video_id(self.channel_id)
			#print("buff_video_id_set", buff_video_id_set)
			#print("self.old_video_id_list", self.old_video_id_list)
			if buff_video_id_set:
				for getting_video_id in buff_video_id_set:
					if not getting_video_id == "" and not getting_video_id is None:
						if not getting_video_id in self.old_video_id_list:
							self.old_video_id_list.append(getting_video_id)
							if len(self.old_video_id_list) > 30:
								self.old_video_id_list = self.old_video_id_list[1:]

							self.isLive = True
							self.updateLiveStatus(offline, live)
							print(self.name + " is online: " + str(self.isLive))
							return
				
			#self.isLive = False
			self.updateLiveStatus(offline, live)
			print(self.name + " is online: " + str(self.isLive))
		else:
			pass
			
	def get_live_video_id(self, search_ch_id):
		dict_str = ""
		video_id_set = set()
		try:
			session = requests.Session()
			headers = {
				'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
			html = session.get("https://www.youtube.com/channel/" +
							   search_ch_id, headers=headers, timeout=10)
			soup = BeautifulSoup(html.text, 'html.parser')
			keyword = 'window["ytInitialData"]'
			for scrp in soup.find_all("script"):
				if keyword in str(scrp):
					dict_str = str(scrp).split(' = ', 1)[1]
			dict_str = dict_str.replace('false', 'False')
			dict_str = dict_str.replace('true', 'True')

			index = dict_str.find("\n")
			dict_str = dict_str[:index-1]
			dics = eval(dict_str)
			for section in dics.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", {})[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", {}):
				for itemsection in section.get("itemSectionRenderer", {}).get("contents", {}):
					items = {}
					if "shelfRenderer" in itemsection:
						for items in itemsection.get("shelfRenderer", {}).get("content", {}).values():
							for item in items.get("items", {}):
								for videoRenderer in item.values():
									for badge in videoRenderer.get("badges", {}):
										if badge.get("metadataBadgeRenderer", {}).get("style", {}) == "BADGE_STYLE_TYPE_LIVE_NOW":
											video_id_set.add(
												videoRenderer.get("videoId", ""))
					elif "channelFeaturedContentRenderer" in itemsection:
						for item in itemsection.get("channelFeaturedContentRenderer", {}).get("items", {}):
							for badge in item.get("videoRenderer", {}).get("badges", {}):
								if badge.get("metadataBadgeRenderer", {}).get("style", "") == "BADGE_STYLE_TYPE_LIVE_NOW":
									video_id_set.add(
										item.get("videoRenderer", {}).get("videoId", ""))
		except:
			return video_id_set
			
		self.videoid = video_id_set
		return video_id_set

# ---

# Config class the can be used in any future projects
class Config:

	def __init__(self, path, listOfOptions, name):

		self.name = name

		self.configData = ""

		file = open(path,"r")

		self.configData = json.load(file)

		file.close()

		print("Inputed path" + str(path))
		print("Inputed options" + str(listOfOptions))
		print("Retrevied Data" + str(self.configData))

		# for option in listOfOptions:

		# 	self.configs[option].append(self.configData[option])

		# 	print("Added option " + str(option) + " with value " + str(self.configs[option]) + " to " + self.name)

		# print("New Data: " + str(self.configs))

	def getOption(self, option):

		return self.configData[option]


	def setOption(self, option, value):

		#print("Setting option " + self.configData[option] + " to value " + value)
		self.configData[option] = value
		#print("New Data: " + self.configData)

	def saveConfig(self,path):

		file = open(path,"w")

		#print("Saving Data: " + str(self.configData))

		json.dump(self.configData,file,ensure_ascii = False, indent=4)

		file.close()

class HoloStream(QMainWindow):

	members = []

	def __init__(self):
		super().__init__()

		self.memberpath = self.resource_path("members.json")
		self.configpath = self.resource_path("config.json")
		self.languagepath = self.resource_path("lang/")

		self.mainConfigOptions = [
			'sort',
			'updates',
			'language'
		]

		self.textLanguageOptions = [
			'title',
			'menuOption1',
			'menuOption1Selector1',
			'menuOption2',
			'menuOption2Selector1',
			'menuOption2Selector2',
			'menuOption2Selector3',
			'menuOption3',
			'buttonOfflineMessage',
			'buttonliveMessage',
			'ErrorMessageTitle',
			'RestartMessage'
		]
		
		self.initConfig()

		self.initLocalization()

		print("Mainconfig: " + str(self.Mainconfig.configData))
		print("LanguageConfig: " + str(self.languageData.configData))

		self.loadMembers()

		self.initUI()

	def initUI(self):
		
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.updateLiveStatus)
		self.timer.setInterval(self.Mainconfig.getOption('updates'))
		self.timer.start()

		quitAction = QAction(self.languageData.getOption(self.textLanguageOptions[2]), self)   
		quitAction.setShortcut("Ctrl+q")  
		quitAction.setStatusTip("Quit Application")
		quitAction.triggered.connect(self.exit)

		menubar = self.menuBar()
		filemenu = menubar.addMenu(self.languageData.getOption(self.textLanguageOptions[1]))
		filemenu.addAction(quitAction)
		
		mainbranchAction = QAction(self.languageData.getOption(self.textLanguageOptions[4]),self)
		mainbranchAction.setShortcut("Ctrl+m")
		mainbranchAction.triggered.connect(self.setSortToMain)
		
		IDbranchAction = QAction(self.languageData.getOption(self.textLanguageOptions[5]),self)
		IDbranchAction.setShortcut("Ctrl+i")
		IDbranchAction.triggered.connect(self.setSortToID)
		
		holoStarsbranchAction = QAction(self.languageData.getOption(self.textLanguageOptions[6]),self)
		holoStarsbranchAction.setShortcut("Ctrl+s")
		holoStarsbranchAction.triggered.connect(self.setSortToStars)
		
		# Will turn into china but I have no way of chekcing the live status yet
		#mainbranchAction = QAction("Main",self) 
		#mainbranchAction.setShortcut("Ctrl-m")
		#mainbranchAction.triggered.connect(self.setSortToMain)
		
		holomenu = menubar.addMenu(self.languageData.getOption(self.textLanguageOptions[0]))
		holomenu.addAction(mainbranchAction)
		holomenu.addAction(IDbranchAction)
		holomenu.addAction(holoStarsbranchAction)

		englishAction = QAction("English",self)
		englishAction.setShortcut("Ctrl-e")
		englishAction.triggered.connect(self.setLanguageToEnglish)
		
		japaneseAction = QAction("日本語",self)
		japaneseAction.setShortcut("Ctrl-e")
		japaneseAction.triggered.connect(self.setLanguageToJapanese)

		languageMenu = menubar.addMenu(self.languageData.getOption(self.textLanguageOptions[7]))
		languageMenu.addAction(englishAction)
		languageMenu.addAction(japaneseAction)

		self.setGeometry(640, 640, 820, 560)
		self.setWindowTitle(self.languageData.getOption(self.textLanguageOptions[0]))    

		# Why did this take take so long to make?
		# But for the waifus at homolive it's worth it... (21:43)
		# Risu's stream was so cute and the korone callab was amazing too. Also I missed Artia's Streams Im so sorry -_- 5am was to early for me :( (23:18)

		self.displayMembers()
		
		self.show()
		
		self.updateLiveStatus()

	def setLanguageToJapanese(self):

		self.Mainconfig.setOption('language','ja_JP')
		self.Mainconfig.saveConfig(self.configpath)

		self.displayMessage(QMessageBox.Warning,self.languageData.getOption(self.textLanguageOptions[11]),"","Info","")

	def setLanguageToEnglish(self):

		self.Mainconfig.setOption('language','en_US')
		self.Mainconfig.saveConfig(self.configpath)
		
		self.displayMessage(QMessageBox.Warning,self.languageData.getOption(self.textLanguageOptions[11]),"","Info","")

	def displayMembers(self):
		left_margin = 20
		top_margin = 20

		max_per_column = 6
		row = 0

		print("Sorting by:" + self.Mainconfig.getOption('sort'))

		for i in range(len(self.members)):
			if self.members[i].branch == self.Mainconfig.getOption('sort'):
				
				if row > max_per_column:
					row = 0
					left_margin = left_margin + 200
					top_margin  = 20
					
				self.members[i].addElements(self,left_margin,top_margin,self.languageData.getOption(self.textLanguageOptions[8]))
				
				top_margin = top_margin  + 80
				
				row = row + 1
					
			else:
				pass	
	
	def setSortToMain(self):
		
		#self.config['sort'] = "main"

		self.Mainconfig.setOption('sort','main')
		
		self.saveConfig()
		
		self.displayMessage(QMessageBox.Warning,self.languageData.getOption(self.textLanguageOptions[11]),"","Info","")
		
	def setSortToID(self):
		
		self.Mainconfig.setOption('sort','ID')
		
		self.saveConfig()
		
		self.displayMessage(QMessageBox.Warning,self.languageData.getOption(self.textLanguageOptions[11]),"","Info","")
		
	def setSortToStars(self):
		
		self.Mainconfig.setOption('sort','Stars')
		
		self.saveConfig()
		
		self.displayMessage(QMessageBox.Warning,self.languageData.getOption(self.textLanguageOptions[11]),"","Info","")
		
	def displayMessage(self,icon,text,informative_text,title,detailed_text):
		
		msg = QMessageBox()
		msg.setIcon(icon)
		msg.setText(text)
		msg.setInformativeText(informative_text)
		msg.setWindowTitle(title)
		msg.setDetailedText(detailed_text)
		
		retval = msg.exec_()

	def updateLiveStatus(self):
		for i in range(len(self.members)):
			
			t = threading.Thread(target=self.members[i].check_live, args=(self.Mainconfig.getOption('sort'),self.languageData.getOption(self.textLanguageOptions[8]),self.languageData.getOption(self.textLanguageOptions[9])))
			t.start()

	def loadMembers(self):

		membersfile = open(self.memberpath,"r")

		members = json.load(membersfile)

		membersfile.close()

		for i in range(len(members)):
			self.members.append(HoloLiveMember(members[i]['name'],members[i]['id'],"main",False,self.resource_path("images/" + members[i]['name'] + ".jpg"),members[i]["branch"]))

	def initConfig(self):
		
		self.Mainconfig = Config(self.configpath,self.mainConfigOptions,"Mainconfig")

		print("Loaded Config")


	def initLocalization(self):

		self.languageData = Config(self.languagepath + str(self.Mainconfig.getOption('language')) + ".json", self.textLanguageOptions, "LanguageConfig")

		#self.languageData.getOption('title')

	def saveConfig(self):

		self.Mainconfig.saveConfig(self.resource_path("config.json"))
		
		print("Saved Config")

	def resource_path(self,relative_path):
		if hasattr(sys, '_MEIPASS'):
			return os.path.join(sys._MEIPASS, relative_path)
		return os.path.join(os.path.abspath("."), relative_path)

	def exit(self):
		quit()

if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	ex = HoloStream()
	sys.exit(app.exec_())
