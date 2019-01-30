#!/usr/bin/python
#-*- coding:utf-8 -*- 

import os, codecs, re
import pandas as pd
import multiprocessing as mp

import utilsOs, utilsGraph, utilsString


##################################################################################
#ORORA SYNTAXER
##################################################################################

def ororaZe(string, advanced=False):
	''' 
	' --> ''
	\s\s --> \s
	a --> A
	à --» A
	###########
	the "plus" option:	
	- --> \s
	'''
	#replace simple apostrophe with 2 apostrophes
	string = string.replace(u"'", u"''")
	#replace multiple spaces with 1 space
	string = re.sub(r'(\s)+', ' ', string)
	#advanced ororazation
	if advanced != False:
		#replace the hyphens with 1 space (the only place multiple spaces appear is where there use to be an hyphen sorrounded by spaces) 
		string = string.replace(u'-', u' ')
		#replace symbol chars with their equivalent
		string = string.replace(u'???', u'?').replace(u'. . . .', u'0')
		string = string.replace(u'. .', u'0').replace(u'??', u'?').replace(u'?!?', u'?').replace(u'_____', u' ')
		string = string.replace(u'@', u'A').replace(u'[ ]', u'OK').replace(u'^', u' ').replace(u'_', u' ')
		###string = string.replace(u'<(>&<)>', u'&').replace(u'</>', u'').replace(u'<H>', u'').replace(u'<U>', u'').replace(u'"', u'apostrophe').replace(u'**', u'0')
	#uppercase it all
	string = string.upper()
	#replace diacritical characters with non diacritical characters
	replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
	for replaceTuple in replacements:
		for char in replaceTuple[1]:
			string = string.replace(char, replaceTuple[0])
	return string


def ororaZeAbbreviations(string, abbrDict=None):
	''' 
	ABBR --> ABBREVIATION
	'''
	def makeReplacements(token): #replace diacritical characters with non diacritical characters
		replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
		for replaceTuple in replacements:
			for char in replaceTuple[1]:
				token = token.replace(char, replaceTuple[0])
				token = token.replace(char.lower(), replaceTuple[0].lower())
		return token
	#open the abbreviation dict
	if abbrDict == None:
		abbrDict = utilsOs.openJsonFileAsDict(u'./ororaAbbreviationDict.json')
	#abbreviation replacement
	stringList = string.split(u' ')
	stringList = [ token if makeReplacements(token).upper() not in abbrDict else abbrDict[makeReplacements(token).upper()] for token in stringList ]
	string = u' '.join(stringList)
	return string


##################################################################################
#RESULTS OF NORMALIZATION
##################################################################################

def applyNormalisationGetResult(goldStandardPath, normPath, normalizationFunction=None, *args):
	''' 
	if normalizationFunction is none, then it will create the baseline otherwise 
	it will aplly the normalization function, ororaze it and evaluate the output 
	'''
	positiveEvalCounter = 0
	with open(goldStandardPath, u'r', encoding=u'utf8') as gsFile:
		#get total number of comments
		totalComments = utilsOs.countLines(gsFile)-1
	#create an empty file for the norm
	normFile = utilsOs.createEmptyFile(normPath, headerLine=u'Id\tEvaluation\tErrorTokens\tOriginal\tOutput\tGoldStandard')
	#create a separate folder for each column
	origFile = utilsOs.createEmptyFile(normPath.replace(u'.tsv', u'1Orig.tsv'), headerLine=u'Id\tOriginal')
	outFile = utilsOs.createEmptyFile(normPath.replace(u'.tsv', u'2Out.tsv'), headerLine=u'Id\tEvaluation\tOutput')
	goldFile = utilsOs.createEmptyFile(normPath.replace(u'.tsv', u'3Gold.tsv'), headerLine=u'Id\tGoldStandard')
	with open(goldStandardPath, u'r', encoding=u'utf8') as gsFile:
		#dispose of the header line
		header = gsFile.readline()
		#get first line
		line = gsFile.readline()
		#count and populate the norm
		while line:
			#get data
			lineList = (line.replace(u'\n', u'')).split(u'\t')
			commentId, originalComment, goldStandard = lineList
			normOutput = str(originalComment)
			#apply orora solution to abbreviations
			###normOutput = ororaZeAbbreviations(normOutput) ########################
			#apply the normalization function
			if normalizationFunction != None:
				normOutput = normalizationFunction(normOutput.lower(), *args) #normOutput = normalizationFunction(normOutput, *args) 
			#get normalized output
			normOutput = ororaZe(normOutput, advanced=True)
			#evaluate if the normalized output corresponds to the gold standard
			if normOutput == goldStandard:
				positiveEvalCounter += 1
				evaluation = 1
				#there are no tokens that cause error
				errorTokList = u'na'
			else:
				evaluation = 0
				#get the tokens that do not correspond exactly and their edit distance
				errorTokList = utilsString.getcorrespondingTokensAndEditDist(normOutput, goldStandard)
			#dump
			normFile.write( u'{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(commentId, evaluation, errorTokList, originalComment, normOutput, goldStandard) )
			#dump to column separate files
			origFile.write( u'{0}\t{1}\n'.format(commentId, originalComment) )
			outFile.write( u'{0}\t{1}\t{2}\t{3}\n'.format(commentId, evaluation, errorTokList, normOutput) )
			goldFile.write( u'{0}\t{1}\n'.format(commentId, goldStandard) )
			#next line
			line = gsFile.readline()
	#close the norm file
	normFile.close()
	#close the other files
	origFile.close()
	outFile.close()
	goldFile.close()
	#dump the results
	resultsPath = u'{0}.results'.format(normPath.replace(u'.tsv', u''))
	utilsOs.dumpRawLines([u'NORMALIZATION RESULTS', u'exact positives: {0}/{1}'.format(positiveEvalCounter, totalComments), u'ratio: {0}'.format(float(positiveEvalCounter)/float(totalComments))], resultsPath)
	

