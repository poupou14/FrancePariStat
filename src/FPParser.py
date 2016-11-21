#!/usr/bin/python
from HTMLParser import HTMLParser
import FPDataFormat
import time
import AnnabetParser
import os,string, sys
import urllib
import time
import urllib2
import copy
#import chardet
#### SPECIFIC IMPORT #####
sys.path.append("../Import/xlrd-0.7.1")
sys.path.append("../Import/xlwt-0.7.2")
sys.path.append("../Import/pyexcelerator-0.6.4.1")

from pyExcelerator import *
import xlwt
from xlrd import open_workbook
from xlwt import Workbook,easyxf,Formula,Style
#from lxml import etree
import xlrd

currentGrille = dict()
grilleEmpty = True

def onlyascii(char):
    if ord(char) <= 0 or ord(char) > 127:
        return ''
    else:
        return char

def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

class FPCalendar():
        def __init__(self, jour_p, mois_p, annee_p):
                self.__jourParMois=[31,28,31,30,31,30,31,31,30,31,30,31]
                self.__moisDlAnnee=['janv','fvr','mars','avr','mai','juin','juil','aot','sept','oct','nov','dc']
                self.__jour = jour_p
                self.__mois = mois_p
                self.__annee = annee_p

        def getDateFromName(self, name_p):
                lineName_l = name_p.split()
                while lineName_l[0] != '-':
                        lineName_l.remove(lineName_l[0])
                lineName_l.remove(lineName_l[0])

                jour_l = lineName_l[0]
                if int(jour_l) < 10 :
                        jour_l = ''.join(("0",lineName_l[0]))
                moisTxt_l = lineName_l[1]
                mois_l = "0"
                for index_l in range(0,len(self.__moisDlAnnee)):
                        #print "test : %s" % self.__moisDlAnnee[index_l]
                        if moisTxt_l.find(self.__moisDlAnnee[index_l]) != -1 :
                                #print "OK"
                                if index_l >= 9 :
                                        mois_l = "%d" % (index_l+1)
                                else :
                                        mois_l = "0%d" % (index_l+1)
                                break
                dateFromName_l = ''.join((jour_l, '.'))
                dateFromName_l = ''.join((dateFromName_l, "%s" % mois_l))
                dateFromName_l = ''.join((dateFromName_l, "."))
                if self.__mois == 12 and mois_l == "01" :
                        dateFromName_l = ''.join((dateFromName_l, "%d" % (self.__annee+1)))
                else :
                        dateFromName_l = ''.join((dateFromName_l, "%d" % self.__annee))
                return dateFromName_l

        def isEarlier(self, cmpDate_p):
            maTotalDate_l = self.__annee * 10000 + self.__mois * 100 + self.__jour
            cmpTotalDate_l = cmpDate_p.__annee * 10000 + cmpDate_p.__mois * 100 + cmpDate_p.__jour
            return (maTotalDate_l < cmpTotalDate_l)

        def getDate(self):
                if self.__jour < 10:
                        date = "0%d-" % self.__jour
                else :
                        date = "%d-" % self.__jour

                if self.__mois < 10 :
                        date = ''.join((date, "0%d-" % self.__mois))
                else :
                        date = ''.join((date, "%d-" % self.__mois))

                date = ''.join((date, "%d" % self.__annee))

                return date

        def nextDay(self) :
                if self.__mois < 12 : #pas le denier mois
                        if self.__jour < self.__jourParMois[self.__mois - 1] : # pas le dernier jour du mois
                                self.__jour += 1
                        else :
                                self.__jour = 1
                                self.__mois += 1
                else :
                        if self.__jour < self.__jourParMois[self.__mois - 1] : # pas le dernier jour du mois
                                self.__jour += 1
                        else :
                                self.__jour = 1
                                self.__mois = 1
                                self.__annee += 1


class FPParser():

        def __init__(self):
                self.__status = False
                self.__pageNext = True
                #self.__prePage = "https://www.france-pari.fr/sportif/grille/resultat/dtGrille/"
                self.__prePage = "https://feelingbet.fr/grille/resultat/dtGrille/"
                self.__nbGames = 0
                self.__jour = 1
                self.__mois = 1
                self.__annee = 2012
                self.__workbook1 = Workbook()
                self.__grilleSheet = self.__workbook1.add_sheet("Grilles", cell_overwrite_ok=True)
                self.__oddsSheet = self.__workbook1.add_sheet("Cotes", cell_overwrite_ok=True)
                self.__outPutFileName = "FP.xls"
                self.__annee = ""
                self.__grilleCounter = 0
                self.__fileGrilleCounter = 0

        def readFP(self, jour_p, mois_p, annee_p, frequenceSvg_p):
                global currentGrille
                # On lit la premiere page puis les suivantes jusqu'a la page vide
                notRead_l = True
                self.__outPutFileName = "FPScan.xls"
                self.__myDate = FPCalendar(jour_p, mois_p, annee_p)
                ticks = time.localtime(time.time())
                self.__today = FPCalendar(ticks.tm_mday, ticks.tm_mon, ticks.tm_year)
                #print self.__myDate

#		self.findRootPage()

                #while (False) :
                while (self.__pageNext and self.__myDate.isEarlier(self.__today)) :
                        myPronoParser = FPPronoParser()
                        myPronoParser.setDate(self.__myDate)
                        fpUrl_l = ''.join((self.__prePage, self.__myDate.getDate()))
                        myPronoParser.reset()
                        currentGrille =  FPDataFormat.emptyGrille.copy()
                        myPronoParser.reset()
                        notRead_l = True
                        try :
                                while notRead_l :
                                        try :
                                                #print "Ouverture : %s" % fpUrl_l
                                                url = urllib2.urlopen(fpUrl_l, timeout = 5)
                                                print "Lecture : %s" % fpUrl_l
                                                myPronoParser.html = url.read()
                                                notRead_l = False
                                        #except IOError :
                                        except IOError:
                                                notRead_l = True
                                                print "pb with : %s" % fpUrl_l
                                                print "url read issue"
                                url.close()
                                #print "Fermeture : %s" % fpUrl_l
                                myPronoParser.html = filter(onlyascii, myPronoParser.html)
                                myPronoParser.feed(myPronoParser.html)
                                self.__grilleCounter += 1
                        except IOError:
                                print "problem while reading %s" % fpUrl_l
                                self.__pageNext = False

                        self.__pageNext = self.__pageNext and not myPronoParser.getLastPage()
                        if self.__grilleCounter % frequenceSvg_p == 0 :
                                print "grille %d, save xls file" % self.__grilleCounter
                                keylist_l = FPDataFormat.listGrille.keys()
                                self.updateOdds()
                                self.writeOuput()
                                #self.__pageNext = False
                                #time.sleep(182)
                        self.__myDate.nextDay()
                self.updateOdds()
                self.writeOuput()


        def updateOdds(self):
                keylist_l = FPDataFormat.listGrille.keys()
                for key_l in keylist_l :
                        grille_l = FPDataFormat.listGrille[key_l]
                        if len (grille_l['cote1']) == 0 : # recuperer les cotes
                                len_l = len(grille_l['team1'])
                                for indexGame_l in range(0, len_l):
                                        myAnnabetParser = AnnabetParser.AnnabetParser()
                                        team1_l = grille_l['team1'][indexGame_l]
                                        team2_l = grille_l['team2'][indexGame_l]
                                        myAnnabetParser.setTeam1(team1_l)
                                        myAnnabetParser.setTeam2(team2_l)
                                        myAnnabetParser.setDate(grille_l['date'])
                                        odds_l = myAnnabetParser.getOdds()
                                        try:
                                            tmpOdds_l = float(odds_l[0])
                                            if (abs(tmpOdds_l) >= 100): # US odds
                                                for i in range(0,3):
                                                    tmpOdds_l = float(odds_l[i])

                                                    if tmpOdds_l > 0 :
                                                        tmpOdds_l = (tmpOdds_l + 100)/100
                                                    elif tmpOdds_l < 0 :
                                                        tmpOdds_l = (-100)/tmpOdds_l + 1
                                                    odds_l[i] = "%3f" % tmpOdds_l
                                            elif float(odds_l[0]) < 0 or float(odds_l[1]) < 0 or float(odds_l[2]) < 0:
                                                odds_l = ["","",""]


                                        except ValueError:
                                            odds_l = ["","",""]

                                        grille_l['cote1'].append(odds_l[0])
                                        grille_l['coteN'].append(odds_l[1])
                                        grille_l['cote2'].append(odds_l[2])
                                        print "{!s} vs {!s}".format(team1_l, team2_l)
                                        print "odds1 : %s" % odds_l[0]
                                        print "oddsN : %s" % odds_l[1]
                                        print "odds2 : %s" % odds_l[2]


        def writeOuput(self):
#		Book to read xls file (output of main_CSVtoXLS)

                index_l = 0
                keylist_l = FPDataFormat.listGrille.keys()
                keylist_l.sort()
                for key_l in keylist_l :
                        grille_l = FPDataFormat.listGrille[key_l]
#			annabet.com
#			if grille
                        self.addGrille(grille_l, index_l)
                        index_l += 1
                self.__workbook1.save(self.__outPutFileName)

        def addGames(self) :
                indexClmnGrille_l = 0
                self.__grilleSheet.write(0, 0, grille['Titre'])
                #for line_l in range(0, len(grille['match'])-1) :
                for line_l in range(0, len(grille['match'])) :
                        value_l = filter(onlyascii, grille['match'][line_l])
                        self.__grilleSheet.write(0, line_l + 1, value_l)

        def addGrille(self, grille_p, index_p):
                indexClmnGrille_l = 0
                value_l = filter(onlyascii, grille_p['grille'])
                self.__grilleSheet.write(index_p, 0, value_l)
                indexClmnGrille_l += 1
                keylist_l = grille_p.keys()
                #style = easyxf('font: underline single')
#		for key in player.keys() :
                for key_l in keylist_l :
                #for indexClmnGrille_l in range(0, len(player_p['prono'])-1) :
                        if key_l == 'team1' :
                                indexClmnOdds_l = 0
                                len_l = len(grille_p['team1'])
                                self.__oddsSheet.write(index_p, indexClmnOdds_l, grille_p['date'])
                                indexClmnOdds_l+=1
                                #print "Taille grille : %d" % len_l
                                print "grille : %s" % grille_p
                                for indexGame_l in range(0, len_l):
                                        value_l = grille_p['team1'][indexGame_l]
                                        value_l = ''.join((value_l, '/'))
                                        value_l = ''.join((value_l, grille_p['team2'][indexGame_l]))
                                        #print "Game : %s" % value_l
                                        self.__oddsSheet.write(index_p, indexClmnOdds_l, value_l)
                                        indexClmnOdds_l += 1
                        elif key_l.find('cote') != -1 :
                                indexClmnOdds_l = 6
                                delta_l = 0
                                if key_l == 'cote1' :
                                        delta_l = 0
                                elif key_l == 'coteN' :
                                        delta_l = 1
                                elif key_l == 'cote2' :
                                        delta_l = 2
                                len_l = len(grille_p['cote1'])
                                #print "Taille grille : %d" % len_l
                                #print "grille : %s" % grille_p
                                for indexGame_l in range(0, len_l):
                                        value_l = grille_p[key_l][indexGame_l]
                                        #print "Game : %s" % value_l
                                        self.__oddsSheet.write(index_p, indexClmnOdds_l+delta_l+3*indexGame_l, value_l)
                        elif key_l != 'grille' and key_l != 'team2' :
                                value_l = grille_p[key_l]
                                self.__grilleSheet.write(index_p, indexClmnGrille_l, value_l)
                                indexClmnGrille_l += 1
                indexClmnGrille_l = 8
                results_l = grille_p['resultat'].split('/')
                print "results :"
                print results_l
                for i in range(1,6) :
                        try :
                                if results_l[i] == '1' :
                                        cote_l = grille_p['cote1'][i-1]
                                elif results_l[i] == 'N' :
                                        cote_l = grille_p['coteN'][i-1]
                                elif results_l[i] == '2' :
                                        cote_l = grille_p['cote2'][i-1]
                                else :
                                        cote_l = "N/A"
                        except IndexError :
                                cote_l = 0
                        self.__grilleSheet.write(index_p, indexClmnGrille_l+i, cote_l)



class FPPronoParser(HTMLParser):

        def __init__(self):
                self.__readOK = False
                self.__getTitle = False
                self.__betweenTag = False
                self.__title = False
                self.__nextType = False
                self.__nextTitle = 0
                self.__nextJackpot = 0
                self.__nextId = 0
                self.__nextExacts = 0
                self.__nextRes = 0
                self.__nextTeam = 0
                self.__nbGames = 0
                self.__nbProno = 0
                self.__nextProno = 1
                self.__lastPage = False
                self.__teamId = 0


        def setDate(self, date_p):
                self.__myDate = date_p

        def setReadNext(self, val) :
                self.__readNext = val

        def setNbGames(self, val) :
                self.__nbGames = val

        def readNext(self) :
                return self.__readNext

        def getLastPage(self) :
                return self.__lastPage

        def handle_starttag(self, tag, attrs):
                global currentGrille
                if tag == "li" and len(attrs) == 1 and self.__nextTitle == 0 :
                        if attrs[0][0] == "class" and attrs[0][1] == "titre-lc ombrage" :
                                self.__nextType = True
                elif tag == "li" and len(attrs) == 1 and self.__nextTitle == 1 :
                        if attrs[0][0] == "class" and attrs[0][1] == "epreuve-lc" :
                                self.__nextTitle = 2
                if tag == "li" and len(attrs) == 1 and self.__nextJackpot == 1 :
                        if attrs[0][0] == "class" and attrs[0][1] == "bg-jackpot-lc" :
                                #print "nextJackpot = 2"
                                self.__nextJackpot = 2
                if tag == "table" and len(attrs) == 2 and self.__nextId == 1 :
                        self.__nextId = 2
                        currentGrille['grille'] = attrs[0][1]
                        #print "grille : %s" % attrs[0][1]
                if tag == "td" and len(attrs) == 0 and self.__nextTeam == 1 :
                        self.__nextTeam = 2
                elif tag == "td" and len(attrs) == 0 and self.__nextTeam == 2 :
                        self.__nextTeam = 3
                elif tag == "td" and len(attrs) == 0 and self.__nextTeam == 4 :
                        self.__nextTeam = 5
                elif tag == "td" and len(attrs) == 0 and self.__nextTeam == 5 :
                        self.__nextTeam = 6
                if tag == "img" and len(attrs) == 3 and self.__nextRes == 1 :
                        if self.__nextProno == 1 :
                                currentGrille['resultat'] = ''.join((currentGrille['resultat'], "/"))
                        if attrs[0][0] == "src" and self.__nextProno == 1:
                                if attrs[0][1].find("checkbox-vide-vert") != -1 :
                                        currentGrille['resultat'] = ''.join((currentGrille['resultat'], "1"))
                                        #print "pari 1"
                                self.__nextProno = 2
                        elif attrs[0][0] == "src" and self.__nextProno == 2:
                                if attrs[0][1].find("checkbox-vide-vert") != -1 :
                                        currentGrille['resultat'] = ''.join((currentGrille['resultat'], "N"))
                                        #print "pari N"
                                self.__nextProno = 3
                        elif attrs[0][0] == "src" and self.__nextProno == 3:
                                if attrs[0][1].find("checkbox-vide-vert") != -1 :
                                        currentGrille['resultat'] = ''.join((currentGrille['resultat'], "2"))
                                        #print "pari 2"
                                self.__nextProno = 1
                self.__betweenTag = True

        def handle_data(self, data):
                global currentGrille
                global grilleEmpty
                global grille
                if self.__nextType and data.find("Mini Feeling") != -1 :
                        self.__teamId = 0
                        print "MINI 5 :"
                        self.__nextType = False
                        self.__nextTitle = 1
                        currentGrille['jackpot'] = 0
                else :
                        self.__nextType = False

                if self.__nextTitle == 2 :
                        data_l = data.replace("\n","").replace("\t", "")
                        len_l = len(data_l)
                        while True :
                                data_l = data_l.replace("  ", " ")
                                if len_l == len(data_l) :
                                        break
                                else:
                                        len_l = len(data_l)
                        while len_l != 0 :
                                if data_l[0] == " " :
                                        data_l = data_l[1:]
                                        len_l = len(data_l)
                                else :
                                        break
                        len_l = len(data_l)
                        currentGrille['name'] = data_l
                        currentGrille['date']=self.__myDate.getDateFromName(data_l)
                        print "date : %s" % currentGrille['date']
                        #print "name : %s" % data_l
                        self.__nextTitle = 0
                        self.__nextJackpot = 1
                elif self.__nextJackpot == 2 :
                        cleandata_l = filter(onlyascii, data)
                        cleandata_l = cleandata_l.replace(" ","")
                        #print "cleandata : %s" % cleandata_l
                        try :
                                #jackpot = int(cleandata_l)
                                jackpot = currentGrille['jackpot'] * 10 + int(data)
                        except ValueError :
                                jackpot = currentGrille['jackpot']
                        currentGrille['jackpot'] = jackpot
                        #print "jackpot : %d" % jackpot
                elif self.__nextId == 2 :
                        self.__nextId = 0
                        self.__nextTeam = 1
                        #print "next game : %s" % self.__nextGame
                elif self.__nextTeam == 3 :
                        cleandata_l = filter(onlyascii, data)
                        cleandata_l = cleandata_l.replace("\n","").replace("\t", "")
                        if len(currentGrille['team1']) > self.__teamId :
                                currentGrille['team1'][self.__teamId] = cleandata_l
                        else :
                                currentGrille['team1'].append(cleandata_l)
                        #print "Team ID : %d" % self.__teamId
                        print "Team1 : %s" % cleandata_l
                        self.__nextTeam = 4
                elif self.__nextTeam == 6 :
                        cleandata_l = filter(onlyascii, data)
                        cleandata_l = cleandata_l.replace("\n","").replace("\t", "")
                        if len(currentGrille['team2']) > self.__teamId :
                                currentGrille['team2'][self.__teamId] = cleandata_l
                        else :
                                currentGrille['team2'].append(cleandata_l)
                        print "Team2 : %s" % cleandata_l
                        self.__nextTeam = 1
                        self.__teamId += 1
                        self.__nextRes = 1
                if data == "Pronostics exacts" and self.__nextRes == 1 :
                        self.__nextExacts = 1
                        self.__nextRes = 0
                        self.__nextTeam = 0
                elif data.find("gagnants") != -1 and self.__nextExacts == 1 :
                        self.__nextExacts = 2
                elif data.find("Gain") != -1 and self.__nextExacts == 2 :
                        self.__nextExacts = 3
                elif self.__nextExacts == 3 :
                        print "Prono exacts : %s" % data
                        try :
                                currentGrille['exacts'] = int(data)
                                self.__nextExacts = 4
                        except ValueError :
                                self.__nextExacts = 3
                                print "pas pronos exacts"
                elif self.__nextExacts == 4 :
                        try :
                                currentGrille['nbGagnants'] = int(data)
                                self.__nextExacts = 5
                                print "Nb Gagnants : %d" % currentGrille['nbGagnants']
                        except ValueError:
                                currentGrille['nbGagnants'] = 0
                elif self.__nextExacts == 5 :
                        if currentGrille['nbGagnants'] != 0 :
                                try :
                                        currentGrille['gains'] = float(data.replace(",", "."))
                                        self.__nextExacts = 0
                                except ValueError:
                                        currentGrille['gains'] = 0.0
                                print "Gains : %f" % currentGrille['gains']
                        else:
                                self.__nextExacts = 0

                        if self.__nextExacts == 0 :
                                if not FPDataFormat.listGrille.has_key(currentGrille['grille']) :
                                        FPDataFormat.listGrille[currentGrille['grille']] = copy.deepcopy(currentGrille)
                                        currentGrille = FPDataFormat.emptyGrille.copy()
                                else:
                                        currentGrille = FPDataFormat.emptyGrille.copy()



        def handle_endtag(self, tag):
                if self.__nextJackpot == 2 and tag == "ul" :
                        self.__nextJackpot = 0
                        self.__nextId = 1

                self.__betweenTag = False
                #if self.__nbProno == 3 :
                        #self.__gameId += 1
                        #self.__nbProno = 0
                        #self.__nextGame.append(1)



def open_excel_sheet():
    """ Opens a reference to an Excel WorkBook and Worksheet objects """
    workbook = Workbook()
    worksheet = workbook.add_sheet("Sheet 1")
    return workbook, worksheet

def write_excel_header(worksheet, title_cols):
    """ Write the header line into the worksheet """
    cno = 0
    for title_col in title_cols:
        worksheet.write(0, cno, title_col)
        cno = cno + 1
    return

def write_excel_row(worksheet, rowNumber, columnNumber):
    """ Write a non-header row into the worksheet """
    cno = 0
    for column in columns:
        worksheet.write(lno, cno, column)
        cno = cno + 1
    return

def save_excel_sheet(workbook, output_file_name):
    """ Saves the in-memory WorkBook object into the specified file """
    workbook.save(output_file_name)
    return

