#!/usr/bin/python
#-*- coding:utf-8 -*- 

import os, codecs
import pandas as pd

import utilsOs, utilsGraph, utilsString


##################################################################################
#ORORA SYNTAXER
##################################################################################

def ororaZe(string):
	''' 
	' --> ''
	a --> A
	à --» A
	'''
	replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
	string = string.replace(u"'", u"''")
	string = string.upper()
	for replaceTuple in replacements:
		for char in replaceTuple[1]:
			string = string.replace(char, replaceTuple[0])
	return string


##################################################################################
#GOLD STANDARD
##################################################################################

def makeGoldStandardOrora(inputPath, outputPath, goldStandardPath):
	'''
	opens the input and output file and makes one input with corresponding output file
	'''
	#INCLUDING the information block columns
	###headerLine = u'Id\tCommentIn\tCommentOut\tInformation blocks\tCoded information block\tBlock type'
	#EXCLUSING the information block columns
	headerLine = u'Id\tCommentIn\tCommentOut'
	#create empty gold standard file
	gsFile = utilsOs.createEmptyFile(goldStandardPath, headerLine)
	#browse the output file line by line
	with open(outputPath, u'r', encoding=u'utf8') as outFile:
		#header line
		headerList = (outFile.readline().replace(u'\n', u'')).split(u'\t')
		idCodeColName, commentColName = headerList[1], headerList[2]
		#dataframe
		inputDf = utilsGraph.getDataFrameFromArgs(inputPath)
		line = outFile.readline()
		#populate edge list
		while line:
			#get data
			lineList = (line.replace(u'\n', u'')).split(u'\t')
			idCode, commentOutLabel, theRest = lineList[1], lineList[2], lineList[3:]
			#select
			selectInputDf = inputDf.loc[ inputDf[u'Id'] == int(idCode) ]
			#get the input comment
			commentInLabel = ( selectInputDf.loc[ selectInputDf[idCodeColName] == int(idCode) ] )[u'Comment'].tolist()
			if len(commentInLabel) == 1:
				commentInLabel = commentInLabel[0]
			else:
				print(44444444444444, idCode, commentInLabel)
			#write the line INCLUDING the information block columns
			###gsFile.write( u'{0}\t{1}\t{2}\t{3}\n'.format(idCode, commentInLabel, commentOutLabel, u'\t'.join(theRest)) )
			#write the line EXCLUDING the information block columns
			gsFile.write( u'{0}\t{1}\t{2}\n'.format(idCode, commentInLabel, commentOutLabel) )
			#next line
			line = outFile.readline()
	#close the file
	gsFile.close()
	#remove the row doubles
	gsDf = utilsGraph.getDataFrameFromArgs(goldStandardPath)
	gsDf = gsDf.drop_duplicates()
	gsDf.to_csv(goldStandardPath, sep='\t', index=False)
	return gsDf


##################################################################################
#RESULTS
##################################################################################

def applyNormalisationGetResult(goldStandardPath, normPath, normalizationFunction=None, lang=u'fr'):
	''' 
	if normalizationFunction is none, then it will create the baseline otherwise 
	it will aplly the normalization function, ororaze it and evaluate the output 
	'''
	positiveEvalCounter = 0
	with open(goldStandardPath, u'r', encoding=u'utf8') as gsFile:
		#get total number of comments
		totalComments = utilsOs.countLines(gsFile)-1
	#create an empty file for the norm
	normFile = utilsOs.createEmptyFile(normPath, headerLine=u'Id\tEvaluation\tOriginal\tOutput\tGoldStandard')
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
			#apply the normalization function
			if normalizationFunction != None:
				normOutput = normalizationFunction(originalComment, lang)
			else: 
				normOutput = originalComment
			#get normalized output
			normOutput = ororaZe(normOutput)
			#evaluate if the normalized output corresponds to the gold standard
			if normOutput == goldStandard:
				positiveEvalCounter += 1
				evaluation = 1
			else:
				evaluation = 0
			#dump
			normFile.write( u'{0}\t{1}\t{2}\t{3}\t{4}\n'.format(commentId, evaluation, originalComment, normOutput, goldStandard) )
			#next line
			line = gsFile.readline()
	#close the norm file
	normFile.close()
	#dump the results
	resultsPath = u'{0}.results'.format(normPath.replace(u'.tsv', u''))
	utilsOs.dumpRawLines([u'NORMALIZATION RESULTS', u'exact positives: {0}/{1}'.format(positiveEvalCounter, totalComments), u'ratio: {0}'.format(float(positiveEvalCounter)/float(totalComments))], resultsPath)


##################################################################################
#NAIVE SPELL CHECKER (CORRECTOR)
##################################################################################

def makeNaiveSpellCorrection(goldStandardPath, naiveSpellCheckPath):
	''' uses a naive statistic spell corrector on the input, then ororazes it '''
	positiveEvalCounter = 0
	with open(goldStandardPath, u'r', encoding=u'utf8') as gsFile:
		#get total number of comments
		totalComments = utilsOs.countLines(gsFile)-1
	#create an empty file
	naiveSpellCheckFile = utilsOs.createEmptyFile(naiveSpellCheckPath, headerLine=u'Id\tEvaluation\tOriginal\tstatSpellChecherOutput\tGoldStandard')
	with open(goldStandardPath, u'r', encoding=u'utf8') as gsFile:
		#dispose of the header line
		header = gsFile.readline()
		#get first line
		line = gsFile.readline()
		#count and populate
		while line:
			#get data
			lineList = (line.replace(u'\n', u'')).split(u'\t')
			commentId, originalComment, goldStandard = lineList
			#get naiveSpellCheck output
			naiveSpellCheckOutput = utilsString.naiveSpellChecker(originalComment, lang=u'fr')
			naiveSpellCheckOutput = ororaZe(naiveSpellCheckOutput)
			#evaluate if the naiveSpellCheck output corresponds to the gold standard
			if naiveSpellCheckOutput == goldStandard:
				positiveEvalCounter += 1
				evaluation = 1
			else:
				evaluation = 0
			#dump
			naiveSpellCheckFile.write( u'{0}\t{1}\t{2}\t{3}\t{4}\n'.format(commentId, evaluation, originalComment, naiveSpellCheckOutput, goldStandard) )
			#next line
			line = gsFile.readline()
	#close the file
	naiveSpellCheckFile.close()
	#dump the results
	resultsPath = u'{0}.results'.format(naiveSpellCheckPath.replace(u'.tsv', u''))
	utilsOs.dumpRawLines([u'NAIVE STATISTIC SPELL CHECKER RESULTS', u'exact positives: {0}/{1}'.format(positiveEvalCounter, totalComments), u'ratio: {0}'.format(float(positiveEvalCounter)/float(totalComments))], resultsPath)



