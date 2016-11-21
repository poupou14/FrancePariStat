#!/usr/bin/python 
import string, sys
from FPParser import FPParser
#from FPWriter import FPWriter

def main():
	jour = 1
	mois = 1
	annee = 2012
	frequenceSvg = 10
	if len(sys.argv) == 2 :
		if sys.argv[1] == "-h" :
			print "user help :"
			print "$ FrancePari.sh [[<jour>] <mois>] <annee>"
			exit()
		else :
			annee = int(sys.argv[1])
	elif len(sys.argv) == 3 :
		mois = int(sys.argv[1])
		annee = int(sys.argv[2])
	elif len(sys.argv) == 4 :
		jour = int(sys.argv[1])
		mois = int(sys.argv[2])
		annee = int(sys.argv[3])
	elif len(sys.argv) == 5 :
		jour = int(sys.argv[1])
		mois = int(sys.argv[2])
		annee = int(sys.argv[3])
		frequenceSvg = int(sys.argv[4])
	else :
		print "user help :"
		print "$ FrancePari.sh [[<jour>] <mois>] <annee>"
		exit()
	myFP = FPParser()
	myFP.readFP(jour,mois,annee, frequenceSvg)
main()
