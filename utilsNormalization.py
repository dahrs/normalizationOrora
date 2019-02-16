#!/usr/bin/python
#-*- coding:utf-8 -*- 

import os, codecs, re
import pandas as pd
import multiprocessing as mp

import utilsOs, utilsGraph, utilsString, utilsML


##################################################################################
#ORORA WORD CORRESPONDENCES MAKER
##################################################################################

def makeDictFromTsvTrain(pathToTrainTsv, trainingDataColumnName, goldStandardColumnName, trainedDict=None, outputDictFilePath=None, preOrorazeOrig=False):
	'''
	Given a path to a "train" file, applies a heuristic dict maker
	it opens it, searches for all possible general language spell 
	corrections and chooses the ones reappearing somewhere else 
	in the corpus
	'''
	trainedDict = trainedDict if trainedDict != None else {}
	emptyList = []
	#return the non identical elements between the original and the gold
	def getNonExactMatch(a, b):
		alignListA, alignListB = utilsString.align2SameLangStrings(a, b, windowSize=6, tokenizingFunct=None)
		return [ (alignListA[ind], alignListB[ind]) for ind in range(len(alignListA)) if alignListA[ind] != alignListB[ind] ]
	#open the train dataframe from the path
	trainDf = utilsOs.getDataFrameFromArgs(pathToTrainTsv)
	#get the specific data we want to use as train to populate our dict (original and gold standard)
	trainDataDf = trainDf[ [trainingDataColumnName, goldStandardColumnName] ]
	#get the gold standard data to which compare the training data
	for indexRow, row in trainDataDf.iterrows():
		#get the elements not matching exactly
		if preOrorazeOrig == False:
			nonMatchingAlignment = getNonExactMatch((row[0]), row[1]) 
		#we preororaze if asked to limit the difference in segmentation and orora-syntax-oriented problems
		else:
			nonMatchingAlignment = getNonExactMatch(advancedOroraze(row[0]), row[1])
		#if the list is not empty
		if nonMatchingAlignment:
			for nonMatchTupl in nonMatchingAlignment:
				#use the original token as a key
				trainedDict[nonMatchTupl[0]] = trainedDict.get( nonMatchTupl[0], list() )+[nonMatchTupl[1]]
	#clean the dict
	for origKey, goldValList in dict(trainedDict).items():
		#eliminate all the elements in the dict that have multiple possible outputs or if the value is an empty symbol
		if len(goldValList) != 1 or goldValList[0] == u'∅':
			del trainedDict[origKey]
		else:
			trainedDict[origKey] = goldValList[0]
	#dump the dict
	if outputDictFilePath != None:
		utilsOs.dumpDictToJsonFile(trainedDict, outputDictFilePath, overwrite=True)
	return trainedDict


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
		string = advancedOroraze(string)
	#uppercase it all
	string = string.upper()
	#replace diacritical characters with non diacritical characters
	replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
	for replaceTuple in replacements:
		for char in replaceTuple[1]:
			string = string.replace(char, replaceTuple[0])
	return string


def advancedOroraze(string):
	''' applies orora changes that are supposed to appear in the dict of pair words '''
	#replace the hyphens with 1 space (the only place multiple spaces appear is where there use to be an hyphen sorrounded by spaces) 
	string = string.replace(u'-', u' ')
	#replace symbol chars with their equivalent
	string = string.replace(u'???', u'?').replace(u'. . . .', u'0')
	string = string.replace(u'. .', u'0').replace(u'??', u'?').replace(u'?!?', u'?').replace(u'_____', u' ')
	string = string.replace(u'@', u'A').replace(u'[ ]', u'OK').replace(u'^', u' ').replace(u'_', u' ')
	###string = string.replace(u'<(>&<)>', u'&').replace(u'</>', u'').replace(u'<H>', u'').replace(u'<U>', u'').replace(u'"', u'apostrophe').replace(u'**', u'0')
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
	#open the abbr dict file if it's a path
	elif type(abbrDict) is str:
		abbrDict = utilsOs.openJsonFileAsDict(abbrDict)
	#abbreviation replacement
	stringList = string.split(u' ')
	stringList = [ token if makeReplacements(token).upper() not in abbrDict else abbrDict[makeReplacements(token).upper()] for token in stringList ]
	string = u' '.join(stringList)
	return string


def frenchFemininAccordsCodification(string, isInput=False):
	''' replaces all possible french feminin accord with a code containing a 
	number, so the normalization function doesn' change it
	if isInput is False, then we transform the code into the original'''
	femAccCorrespondence = [ (u'ée', u'¤0¤ée¤0¤'), (u'ee', u'¤0¤ee¤0¤'), (u'ÉE', u'¤0¤ÉE¤0¤'), (u'EE', u'¤0¤EE¤0¤'), (u'éE', u'¤0¤éE¤0¤'), (u'Ée', u'¤0¤Ée¤0¤'), (u'éé', u'¤0¤éE¤0¤'), (u'ÉÉ', u'¤0¤Ée¤0¤'), (u'eE', u'¤0¤eE¤0¤'), (u'Ee', u'¤0¤Ee¤0¤') ]
	if isInput != False:
		string = u'{0} '.format(string)
		#find every feminin accord
		femininAccords = re.compile(r'[e|é|E|É]{2}[\s|\.|,|?|!|;|:|)|\]|}]+')
		femininAccordsList = re.findall(femininAccords, string)
		for eeSubStr in femininAccordsList:
			string = string.replace(eeSubStr, u'¤0¤{0}¤0¤{1}'.format(eeSubStr[:2], eeSubStr[-1]))
	else:
		string = string.replace(u'¤0¤', u'')
		if string[-1] == u' ':
			string = string[:-1]
	return string


##################################################################################
#RESULTS OF NORMALIZATION
##################################################################################

def normalizationEvaluator(normalizedString, goldStandard, positiveEvalCounter):
	''' evaluate if the normalized output corresponds to the gold standard '''
	if normalizedString == goldStandard:
		positiveEvalCounter += 1
		evaluation = 1
	else: evaluation = 0
	return positiveEvalCounter, evaluation


def applyNormalisationGetResult(testFilePath, normOutPath=None, ororazeOutput=(True, True), useAbbrDict=False, normalizationFunction=None, *args):
	''' 
	if normalizationFunction is none, then it will create the baseline otherwise 
	it will aplly the normalization function, ororaze it and evaluate the output 
	'''
	positiveEvalCounter = 0
	with open(testFilePath, u'r', encoding=u'utf8') as gsFile:
		#get total number of comments
		totalComments = utilsOs.countLines(gsFile)-1
	#create an empty file for the norm
	if normOutPath != None:
		normFile = utilsOs.createEmptyFile(normOutPath, headerLine=u'Id\tEvaluation\tErrorTokens\tOriginal\tOutput\tGoldStandard')
		#create a separate folder for each column
		origFile = utilsOs.createEmptyFile(normOutPath.replace(u'.tsv', u'1Orig.tsv'), headerLine=u'Id\tOriginal')
		outFile = utilsOs.createEmptyFile(normOutPath.replace(u'.tsv', u'2Out.tsv'), headerLine=u'Id\tEvaluation\tOutput')
		goldFile = utilsOs.createEmptyFile(normOutPath.replace(u'.tsv', u'3Gold.tsv'), headerLine=u'Id\tGoldStandard')
	with open(testFilePath, u'r', encoding=u'utf8') as gsFile:
		#dispose of the header line
		header = gsFile.readline()
		#get first line
		line = gsFile.readline()
		#start an empty dejavuDict
		dejavuDict = {}
		#count and populate the norm
		while line:
			#get data
			lineList = (line.replace(u'\n', u'')).split(u'\t')
			commentId, originalComment, goldStandard = lineList
			normOutput = str(originalComment)
			#detect french feminin accord and fossilize the word by modifying its structure to something unchanged by the normalization function 
			normOutput = frenchFemininAccordsCodification(originalComment, isInput=True)
			#apply orora solution to abbreviations
			if useAbbrDict != False:
				if useAbbrDict != True:
					normOutput = ororaZeAbbreviations(normOutput, useAbbrDict)
				else:
					normOutput = ororaZeAbbreviations(normOutput)
			#apply the normalization function
			if normalizationFunction != None:
				normOutput, dejavuDict = normalizationFunction(normOutput.lower(), dejavuDict, *args)
			#reverse back the code for the feminin accord into its original form
			normOutput = frenchFemininAccordsCodification(normOutput, isInput=False)
			#get normalized output
			if ororazeOutput == True:
				normOutput = ororaZe(normOutput, advanced=True)
			elif type(ororazeOutput) is tuple or type(ororazeOutput) is list:
				if ororazeOutput[0] == True:
					normOutput = ororaZe(normOutput, advanced=ororazeOutput[1])
			#evaluation    if the normalized output corresponds to the gold standard
			positiveEvalCounter, evaluation = normalizationEvaluator(normOutput, goldStandard, positiveEvalCounter)
			#get the tokens that do not correspond exactly and their edit distance
			errorTokList = utilsString.getcorrespondingTokensAndEditDist(normOutput, goldStandard) if evaluation == 0 else u'na'
			#dump
			if normOutPath != None:
				normFile.write( u'{0}\t{1}\t{2}\t{3}\t{4}\t{5}\n'.format(commentId, evaluation, errorTokList, originalComment, normOutput, goldStandard) )
				#dump to column separate files
				origFile.write( u'{0}\t{1}\n'.format(commentId, originalComment) )
				outFile.write( u'{0}\t{1}\t{2}\t{3}\n'.format(commentId, evaluation, errorTokList, normOutput) )
				goldFile.write( u'{0}\t{1}\n'.format(commentId, goldStandard) )
			#next line
			line = gsFile.readline()
	#close the norm file
	if normOutPath != None:
		normFile.close()
		#close the other files
		origFile.close()
		outFile.close()
		goldFile.close()
		#dump the results
		resultsPath = u'{0}.results'.format(normOutPath.replace(u'.tsv', u''))
		utilsOs.dumpRawLines([u'NORMALIZATION RESULTS', u'exact positives: {0}/{1}'.format(positiveEvalCounter, totalComments), u'ratio: {0}'.format(float(positiveEvalCounter)/float(totalComments))], resultsPath)
	return { u'exact positives': positiveEvalCounter, u'total comments': totalComments, u'ratio': (float(positiveEvalCounter)/float(totalComments)) }


def applyNormalisationGetResultCrossVal(crossValFolderPath, resultFilePath, ororazeOutput=(True, True), preOrorazeOrig=False, normalizationFunction=None, *args):
	''' applies the applyNormalisationGetResult function once for each file in the cross validation folder 
	and tests it against the remaining N-1 cross validation files '''
	import os
	totalRatioResult, totalNbResults = 0, 0
	learnedAbbrDictPath = u'./007learnedDict/learnedOroraAbbrDict.json'
	#save in a list all the names of the files in the cross validation folder
	listOfCrossValFiles = utilsOs.getContentOfFolder(crossValFolderPath)
	#open the file
	with open(resultFilePath, u'w', encoding=u'utf8') as resultFile:
		#dump the first lines
		resultFile.write(u'NORMALIZATION RESULTS\nRatio\tPositives\tTotal')
	with open(resultFilePath, u'a', encoding=u'utf8') as resultFile:
		#browse each file
		for indexFile, fileName in enumerate(listOfCrossValFiles):
			#make the dict
			makeDictFromTsvTrain(u'{0}{1}'.format(crossValFolderPath, fileName), u'CommentIn', u'CommentOut', outputDictFilePath=learnedAbbrDictPath, preOrorazeOrig=preOrorazeOrig)
			#make a unified file with the rest of the files
			unifiedTestSet = u'./tempUnified.tsv'
			listOfTestFiles = listOfCrossValFiles[:indexFile] + listOfCrossValFiles[indexFile+1:]
			listOfTestFiles = [ u'{0}{1}'.format(crossValFolderPath, filePath) for filePath in listOfTestFiles ]
			utilsML.unifyListOfTestSetsIntoOne(listOfTestFiles, outputUnifiedFilePath=unifiedTestSet)
			#evaluate using the unified file
			resultDict = applyNormalisationGetResult(unifiedTestSet, ororazeOutput=ororazeOutput, useAbbrDict=learnedAbbrDictPath, normalizationFunction=None, *args)
			#delete the temporary test set
			os.remove(unifiedTestSet)
			#dump the individual results
			resultFile.write( u'{0}\t{1}\t{2}\n'.format(resultDict[u'ratio'], resultDict[u'exact positives'], resultDict[u'total comments']) )
			#sum the total of the results
			totalRatioResult += resultDict[u'ratio']
			totalNbResults += resultDict[u'exact positives']
		#dump the conclusion score result		
		resultFile.write(u'AVERAGE RATIO: {0}\nAVERAGE EXACT POSITIVES: {1}'.format( totalRatioResult/len(listOfCrossValFiles), totalNbResults/len(listOfCrossValFiles) ))

