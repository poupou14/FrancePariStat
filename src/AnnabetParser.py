#!/usr/bin/python 
from HTMLParser import HTMLParser
import os,string, sys
import urllib
import urllib2
import copy

def mycounter():
	if not hasattr(mycounter, "counter"):
		mycounter.counter = 0  # it doesn't exist yet, so initialize it
	mycounter.counter += 1
	return mycounter.counter

def onlyascii(char):
    if ord(char) <= 0 or ord(char) > 127: 
	return ''
    else: 
	return char

class TorNet():

	def __init__(self):
		#self.__browser = "torify lynx -source"
		self.__browser = "torify curl"

	def openUrl(self, url_p, reboot_p):
		counter_l = mycounter()
		print "couter = %d" % counter_l
		if counter_l % 10 == 0 or reboot_p : # on relance tor
			outIO_l = os.popen("sudo /etc/init.d/tor restart")
			outIO_l = os.popen("sudo /etc/init.d/privoxy restart")
			print "redemarrage Tor : %s" % outIO_l
		#cmd = os.popen(". /home/lili//SHELL/browser_proxy.ksh")
		#else :
		#cmd = os.popen(". $HOME/SHELL/browser_noproxy.ksh")
		#print "Browser : %s" % browser_l
		#print "Browser counter : %d" % counter_l
		#print "Ouverture : %s" % self.__gameUrl
		#url = urllib2.urlopen(self.__gameUrl, timeout = 5)
		cmd = os.popen("{!s} {!s}".format(self.__browser, url_p))
		return cmd

class AnnabetParser(HTMLParser): 

	def __init__(self): 
		self.__betweenTag = False
		self.__pinnacle = 0 
		self.__bet365 = 0 
		self.__myDate = ""
		self.__team1 = ""
		self.__team2 = ""
		self.__game = ""
		self.__gameUrl = ""
		self.__httpAddress = "annabet.com"
		self.__httpRootAddress = "https://annabet.com/en/soccerstats/"
		self.__odds1 = ""
		self.__oddsN = ""
		self.__odds2 = ""


	def setDate(self, date_p):
		self.__myDate = date_p

	def setTeam1(self, val) :
		self.__team1 = val

	def setTeam2(self, val) :
		self.__team2 = val

	def getGameUrl(self) :
		essai_l = 1
		self.__gameUrlFound = False
		self.__gameUrl = ""
		team1_l = self.__team1
		team2_l = self.__team2
		browser_l = "links"
		pair_l = True
		while (not self.__gameUrlFound):
			query_l = ''.join((self.__httpAddress, ": "))
			query_l = ''.join((query_l, self.__myDate))
			query_l = ''.join((query_l, " "))
			if essai_l == 1 :	# first try with team full name
				self.__game = ''.join((self.__team1, " - "))
				self.__game = ''.join((self.__game, self.__team2))
			elif essai_l == 2 :	# not first try
				listTeam1_l = self.__team1.split()
				listTeam2_l = self.__team2.split()
				len1_l = 0
				len2_l = 0
				for i in range(0, len(listTeam1_l)) :
					if len(listTeam1_l[i]) > len1_l :
						len1_l = len(listTeam1_l[i])
						team1_l = listTeam1_l[i]
				for i in range(0, len(listTeam2_l)) :
					if len(listTeam2_l[i]) > len2_l :
						len2_l = len(listTeam2_l[i])
						team2_l = listTeam2_l[i]
				self.__game = ''.join((team1_l, " - "))
				self.__game = ''.join((self.__game, team2_l))
			elif essai_l == 3 :	# not first try
				listTeam1_l = self.__team1.split()
				len1_l = 0
				for i in range(0, len(listTeam1_l)) :
					if len(listTeam1_l[i]) > len1_l :
						len1_l = len(listTeam1_l[i])
						team1_l = listTeam1_l[i]
				self.__game = team1_l
			elif essai_l == 4 :	# not first try
				listTeam2_l = self.__team2.split()
				len2_l = 0
				for i in range(0, len(listTeam2_l)) :
					if len(listTeam2_l[i]) > len2_l :
						len2_l = len(listTeam2_l[i])
						team2_l = listTeam2_l[i]
				self.__game = team2_l
	
			query_l = ''.join((query_l, self.__game))
			filename = 'https://www.google.com/search?' + urllib.urlencode({'q': query_l })
			pair_l = not pair_l
			print "recherche : %s" % filename
			browser_l = "lynx -listonly -width=1000"
			commandeLine_l = "{!s} -dump {!s} | grep annabet.com".format(browser_l,filename)
			cmd = os.popen(commandeLine_l)
			output = cmd.read()
			lineResult_l = output.splitlines()
			#print "line result : %s" % lineResult_l
			cmd.close()
			for line_l in lineResult_l :
				#print "line : %s" % line_l
				wordsResult_l = line_l.split(" ")
				for word_l in wordsResult_l :
					self.__gameUrlFound = word_l.find("annabet.com") != -1 and word_l.find("gamereport") != -1 
					#self.__gameUrlFound = self.__gameUrlFound and word_l.find(team1_l) !=- 1 and word_l.find(team2_l) != -1 
					if self.__gameUrlFound :
						urlTab_l = word_l.split("/")
						#print "res {!s} : {!s}".format(browser_l,urlTab_l[-1:][0])
						#print urlTab_l
						self.__gameUrl = ''.join((self.__httpRootAddress,urlTab_l[-1:][0]))
						break
				if self.__gameUrlFound : 
					break
			if essai_l == 4 :
				self.__gameUrlFound = True
			essai_l += 1
		if self.__gameUrl.find("http") == -1 :
			self.__gameUrl = ''.join(("https://", self.__gameUrl))
		if self.__gameUrl.find("html") == -1 :
			self.__gameUrl = ''.join((self.__gameUrl, "html"))
		#print "url : %s" % self.__gameUrl
		return self.__gameUrl	



	def getOdds(self) :
		odds_l = []
		notRead_l = 0
		reboot_l = False
		self.getGameUrl()
		self.reset()
		while notRead_l <= 3 :
			try :
				myNet_l = TorNet()
				cmd = myNet_l.openUrl(self.__gameUrl, reboot_l)
				print "Lecture : %s" % self.__gameUrl
				self.html = cmd.read()
				#self.html = url.read()
				#url.close()
				print "Fermeture : %s" % self.__gameUrl
				self.html = filter(onlyascii, self.html)
				self.feed(self.html)
				if self.__odds1 != "" :
					notRead_l = 4
					reboot_l = False
				else :
					notRead_l += 1
					reboot_l = True
			#except IOError :
			except IOError:
				notRead_l += 1
				print "pb with : %s" % self.__gameUrl
				#exit
		odds_l.append(self.__odds1)
		odds_l.append(self.__oddsN)
		odds_l.append(self.__odds2)
		return odds_l

	def handle_starttag(self, tag, attrs):
		if tag == "td" and len(attrs) == 1 and self.__pinnacle >= 1 :
			self.__pinnacle += 1
		elif tag == "td" and len(attrs) == 1 and self.__bet365 >= 1 :
			self.__bet365 += 1
		self.__betweenTag = True




	def handle_data(self, data):
		if self.__pinnacle == 0 and self.__betweenTag and data.find("PinnacleSport") != -1 :
			print "Pinnacle Found"
			self.__pinnacle = 1	
		elif self.__pinnacle == 2  :
			self.__odds1 = data
			#print "Odds1 : %s" % data
		elif self.__pinnacle == 3  :
			self.__oddsN = data
			#print "OddsN : %s" % data
		elif self.__pinnacle == 4  :
			self.__odds2 = data
			#print "Odds2 : %s" % data
			self.__pinnacle = -1
		elif self.__bet365 == 0 and self.__pinnacle == 0 and self.__betweenTag and data.find("Bet365") != -1 :
			print "Bet365 Found"
			self.__bet365 = 1	
		elif self.__bet365 == 2  :
			self.__odds1 = data
			#print "Odds1 : %s" % data
		elif self.__bet365 == 3  :
			self.__oddsN = data
			#print "OddsN : %s" % data
		elif self.__bet365 == 4  :
			self.__odds2 = data
			#print "Odds2 : %s" % data
			self.__bet365 = -1


	def handle_endtag(self, tag):
		self.__betweenTag = False



