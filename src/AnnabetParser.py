#!/usr/bin/python 
from HTMLParser import HTMLParser
import os,string, sys
import urllib
import urllib2
import copy
import re

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
                self.__browser = "elinks -source "

        def openUrl(self, url_p):
		cmd = os.popen("{!s} {!s}".format(self.__browser, url_p))
		return cmd

class AnnabetParser(HTMLParser): 

	def __init__(self): 
                self.__betweenTag = False
                self.__oddsFound = -1
		self.__pinnacle = 0 
		self.__bet365 = 0 
		self.__myDate = ""
		self.__team1 = ""
		self.__team2 = ""
		self.__game = ""
                self.__gameInfo = ""
                self.__gameInfoFound = False
                self.__httpAddress = "annabet.com"
		self.__httpRootAddress = "https://annabet.com/en/soccerstats/"
                self.__odds = ["0.0", "0.0", "0.0"]


	def setDate(self, date_p):
		self.__myDate = date_p

	def setTeam1(self, val) :
		self.__team1 = val

	def setTeam2(self, val) :
		self.__team2 = val

        def readGameInfo(self) :
		essai_l = 1
                self.__gameInfoFound = False
                self.__gameInfo = ""
		team1_l = self.__team1
		team2_l = self.__team2
		browser_l = "links"
		pair_l = True
                while (not self.__gameInfoFound):
			query_l = ''.join((self.__httpAddress, ": "))
			query_l = ''.join((query_l, self.__myDate))
			query_l = ''.join((query_l, " "))
			if essai_l == 1 :	# first try with team full name
                                self.__game = ''.join((self.__team1, " "))
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
                                self.__game = ''.join((team1_l, " "))
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
                        query_l = ''.join((query_l, " pinnacle"))
                        self.__url = 'https://www.framabee.org/search?' + urllib.urlencode({'q': query_l })
			pair_l = not pair_l
                        print "recherche : %s" % self.__url
                        browser_l = "lynx -source "
                        commandeLine_l = "{!s} -dump {!s}".format(browser_l,self.__url)
                        cmd = os.popen(commandeLine_l)
                        self.__output = cmd.read()
                        #print "output :\n%s" % self.__output
                        lineResult_l = self.__output.splitlines()
                        #print "line result : %s" % lineResult_l
			cmd.close()
			for line_l in lineResult_l :
				#print "line : %s" % line_l
				wordsResult_l = line_l.split(" ")
				for word_l in wordsResult_l :
                                        self.__gameInfoFound = word_l.find("annabet.com") != -1 and word_l.find("gamereport") != -1
                                        if self.__gameInfoFound :
                                                print "found"
                                                break
                                if self.__gameInfoFound :
					break
			if essai_l == 4 :
                                self.__gameInfoFound = True
			essai_l += 1
                if self.__gameInfo.find("http") == -1 :
                        self.__gameInfo = ''.join(("https://", self.__gameInfo))
                if self.__gameInfo.find("html") == -1 :
                        self.__gameInfo = ''.join((self.__gameInfo, "html"))
                #print "url : %s" % self.__gameInfo
                return essai_l



	def getOdds(self) :
		odds_l = []
		notRead_l = 0
                self.reset()
                essai_l = self.readGameInfo()
		while notRead_l <= 3 :
			try :
                                print "Lecture : %s" % self.__url
                                #print self.__output
                                self.html = self.__output
				#self.html = url.read()
				#url.close()
                                print "Fermeture : %s" % self.__url
				self.html = filter(onlyascii, self.html)
				self.feed(self.html)
                                if self.__odds[2] != "0.0" :
					notRead_l = 4
				else :
					notRead_l += 1
			#except IOError :
			except IOError:
				notRead_l += 1
                                print "pb with : %s" % self.__url
				#exit
                odds_l.append(self.__odds[0])
                odds_l.append(self.__odds[1])
                odds_l.append(self.__odds[2])
                #a = raw_input("...")
		return odds_l

	def handle_starttag(self, tag, attrs):
                if self.__pinnacle == 0 and tag == "p" and len(attrs) == 1 :
                        self.__pinnacle = 1
                #elif tag == "td" and len(attrs) == 1 and self.__bet365 >= 1 :
                        #self.__bet365 += 1
		self.__betweenTag = True




	def handle_data(self, data):
                if self.__pinnacle == 1 and data.find("Pinnacle") :
                        self.__pinnacle = 2
                elif self.__pinnacle == 2  :
                        print "datas = %s" % data
                        odds = data.split(",")
                        i = 0
                        for elt in odds :
                            catchDec = False
                            catchUs = False
                            oddsDec = re.search("\d+\.\d+", elt)
                            oddsUs = re.search("[+-]\d+", elt)
                            if oddsDec :
                                strOdds = oddsDec.group(0)
                                catchDec = True
                                #print "catch :%s" % strOdds
                            elif oddsUs :
                                strOdds = oddsUs.group(0)
                                #print "catch :%s" % strOdds
                                catchUs = True

                            #raw_input("next")
                            if catchDec or catchUs:
                                try :
                                    tmp = float(strOdds)
                                    self.__odds[i] = strOdds
                                    #print "odds%d = " % i
                                    #print "%s" % strOdds
                                    i = i+1
                                except ValueError:
                                    res =  "ko"
                            if i == 3:
                                break
                        #print "Odds1 : %s" % data
                        if i == 3 :
                            self.__pinnacle = -1


	def handle_endtag(self, tag):
                self.__betweenTag = False
                if tag == "p" and self.__pinnacle > 0:
                        self.__pinnacle = 0



