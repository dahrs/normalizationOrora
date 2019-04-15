#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
from tabulate import tabulate

parser = argparse.ArgumentParser()

parser.add_argument(u'-pt', u'--pathToTsvFolder', type=str, default=u'./003alignedTrainSet/',
                    help=u'path to the tsv file to be pretty printed')
args = parser.parse_args()


pathToTsvFolder = args.pathToTsvFolder


def prettyPrintTsv(pathToTsv, printMisalignedOnly=False):
	with open(pathToTsv) as openedTsv :
		counter = 1
		line = openedTsv.readline()
		while line:
			#get original alignment
			orig = line.replace(u'\n', u'').split(u'\t')
			#get gold alignment
			line = openedTsv.readline()			
			gold = line.replace(u'\n', u'').split(u'\t')
			#color in red the non exact match elements
			for index, origElem in enumerate(orig):
				goldElem = gold[index]
				if origElem != goldElem:
					orig[index] = u'\033[1;31m{0}\033[0m'.format(origElem)
					gold[index] = u'\033[1;31m{0}\033[0m'.format(goldElem)
			if printMisalignedOnly != False and u'[1;31m' in u' '.join(orig[1:]):
				print(u'#####################################{0}##########################################'.format(counter))
			elif printMisalignedOnly != False and u'[1;31m' not in u' '.join(orig[1:]):
				pass
			else: print(u'#####################################{0}##########################################'.format(counter))
			#divide the table in 12 elements for it to be printable in the terminal
			for startIndex in range(1, len(orig), 11):
				endIndex = startIndex+11 if startIndex+11 < len(orig) else len(orig)
				#get table to prettyprint
				table = [ [orig[0]]+orig[startIndex:endIndex] , [gold[0]]+gold[startIndex:endIndex] ]
				if printMisalignedOnly == False:
					print( tabulate(table, tablefmt='psql') )
				else:
					if u'[1;31m' in u' '.join(orig[1:]):
						print( tabulate(table, tablefmt='psql') )
			#print page return
			if printMisalignedOnly != False and u'[1;31m' in u' '.join(orig[1:]):
				print()
				print()
			elif printMisalignedOnly != False and u'[1;31m' not in u' '.join(orig[1:]):
				pass
			else:
				print()
				print()
			#get next orig line
			line = openedTsv.readline()
			counter += 1


def launchPrettyPrintTsv(pathToTsvFolder):
	''''''
	folderContent = [ file for file in myUtils.getContentOfFolder(pathToTsvFolder) if u'.tsv' in file ]
	if len(folderContent) == 1:
		prettyPrintTsv(folderContent[0])
	else:
		tempFilePath = u'{0}temp.tsv'.format(pathToTsvFolder)
		#delete the previous file if it exists
		try:
			myUtils.deleteFile(tempFilePath)
		except FileNotFoundError: pass
		with open(tempFilePath, 'w') as tempFile:
			#look up each original-gold standard file association
			for n in range(len(folderContent)):
				origList = [ file for file in folderContent if u'Orig' in file ]
				origList = [ file for file in origList if u'Lists{0}.'.format(n) in file ]
				goldList = [ file for file in folderContent if u'GS' in file ]
				goldList = [ file for file in goldList if u'Lists{0}.'.format(n) in file ]
				if len(origList) != 0:
					with open(u'{0}{1}'.format(pathToTsvFolder, origList[0])) as origFile:
						origLine = origFile.readline()
						with open(u'{0}{1}'.format(pathToTsvFolder, goldList[0])) as goldFile:
							goldLine = goldFile.readline()
							while origLine:
								origLine = u'{0}\n'.format(origLine) if u'\n' not in origLine else origLine
								goldLine = u'{0}\n'.format(goldLine) if u'\n' not in goldLine else goldLine
								#change it from the list form into a tsv form
								if origLine[0] == u'[':
									origLine = origLine.replace(u"['", u'orig:\t').replace(u"', '", u'\t').replace(u"']", u'')
									goldLine = goldLine.replace(u"['", u'gold:\t').replace(u"', '", u'\t').replace(u"']", u'')
								#dump into temp file
								tempFile.write(origLine)
								tempFile.write(goldLine)
								#get next Line
								origLine = origFile.readline()
								goldLine = goldFile.readline()
		prettyPrintTsv(tempFilePath, True)
		myUtils.deleteFile(tempFilePath)


launchPrettyPrintTsv(pathToTsvFolder)