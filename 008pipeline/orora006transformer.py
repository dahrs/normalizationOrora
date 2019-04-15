#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
import pandas as pd



parser = argparse.ArgumentParser()

parser.add_argument(u'-top', u'--testOriginalPath', type=str, default=u'./002sets/testOrig.tsv',
                    help=u'path to the file containing the original comments of the test')
parser.add_argument(u'-ip', u'--inputPath', type=str, default=u'./002sets/', # u'./002sets/setForSlidesCrossVal/10percent/',
                    help=u'path to the folder containing the comments of the test')
parser.add_argument(u'-tfp', u'--transformedFilePath', type=str, default=u'./006transformed/transformedTest.tsv',
                    help=u'path to the file where we will dump the transformed comments of the test')
parser.add_argument(u'-tp', u'--transformedPath', type=str, default=u'./006transformed/',
                    help=u'path to the folder where we will dump the transformed comments of the test files')
parser.add_argument(u'-nfd', u'--normalizationFunctionOrDict', type=str, default=u'./005learnedDict/ororaAbbreviationDict.json', #./005learnedDict/humanMadeDict/humanMadeOroraAbbreviationDict.json
                    help=u'path to the learned dict file')
parser.add_argument(u'-dp', u'--pathToDicts', type=str, default=u'./005learnedDict/',
                    help=u'path to the learned dict files')
args = parser.parse_args()


testOrigFilePath = args.testOriginalPath
normOutFilePath = args.transformedFilePath
normalization = args.normalizationFunctionOrDict #u'./005learnedDict/humanMadeDict/humanMadeOroraAbbreviationDict.json'
inputPath = args.inputPath
dictPath = args.pathToDicts
outputPath = args.transformedPath


def ororaZeAbbreviations(string, abbrDict=None, listTheVariations=False, spacyModel=None):
	''' 
	ABBR --> ABBREVIATION
	'''
	def makeReplacements(token): #replace diacritical characters with non diacritical characters
		replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
		for replaceTuple in replacements:
			for char in replaceTuple[1]:
				token = token.replace(char, replaceTuple[0])
				token = token.replace(char.lower(), replaceTuple[0].lower())
		return token.upper()
	#open the abbreviation dict
	if abbrDict == None:
		abbrDict = myUtils.openJsonFileAsDict(u'./005learnedDict/ororaAbbreviationDict.json')
	#open the abbr dict file if it's a path
	elif type(abbrDict) is str:
		abbrDict = myUtils.openJsonFileAsDict(abbrDict)
	#tokenizing
	stringList = myUtils.multTokenizer(string, whatTokenizer=0, spacyModel=spacyModel)
	#abbreviation replacement
	if type(abbrDict[list(abbrDict.keys())[0]]) is list:
		for index, token in enumerate(stringList):			
			#if the token is in the dict
			if makeReplacements(token) in abbrDict:
				minScore = 0.55
				#if we search only for the first and most common option
				if listTheVariations == False:
					#if the token has a reliable score
					if abbrDict[makeReplacements(token)][0][1] >= minScore:
					 	stringList[index] = abbrDict[makeReplacements(token)][0][0]
					#use only the tokens having only one way of transcribing
					#if len(abbrDict[makeReplacements(token)]) == 1:
					#	stringList[index] = abbrDict[makeReplacements(token)][0][0]
					else:
						stringList[index] = makeReplacements(token)
				#if we want to return a list of all the possibilities in decreasing order
				else:
					variations = [ var[0] for var in abbrDict[makeReplacements(token)] if var[1] >= minScore ]
					stringList[index] = u'¤'.join(variations) if len(variations) != 0 else makeReplacements(token)
		#stringList = [ token if makeReplacements(token) not in abbrDict else abbrDict[makeReplacements(token)][0][0] for token in stringList ]
	else:
		stringList = [ token if makeReplacements(token) not in abbrDict else abbrDict[makeReplacements(token).upper()] for token in stringList ]
	#elimination of the empty elements u'' or u'∅' if they got in (somehow)
	#stringList = [ token for token in stringList if token not in [u'', u'∅'] ]
	string = u' '.join(stringList)
	return string


def applyNormalisation(testOrigPath, normOutPath=None, spacyModel=None, normalization=None, *args):
	''' apply the normalization dict'''
	#if we are given a path to the place where the dict is
	if type(normalization) is str:
		normalization = myUtils.openJsonFileAsDict(normalization)
	#start an empty dejavuDict
	dejavuDict = {}
	#open the test dataframe from the path
	testOrigDf = myUtils.getDataFrameFromArgs(testOrigPath, header=False)[0]
	for index, testComment in testOrigDf.iteritems():
		if normalization == None:
			normOutput = testComment
		#use the dict as a normalization
		elif type(normalization) is dict:
			normOutput = ororaZeAbbreviations(testComment, normalization, listTheVariations=False)
		else:
			#detect french feminin accord and fossilize the word by modifying its structure to something unchanged by the normalization function 
			normOutput = myUtils.frenchFemininAccordsCodification(testComment, isInput=True)
			#apply the spell corrector or other normalization function
			normOutput, dejavuDict = normalization(normOutput.lower(), dejavuDict, *args)
			#reverse back the code for the feminin accord into its original form
			normOutput = myUtils.frenchFemininAccordsCodification(normOutput, isInput=False)
		#save into pandas series
		testOrigDf[index] = normOutput
	#dump normalized output
	if normOutPath != None:
		testOrigDf.to_csv(normOutPath, sep=u'\t', index=False)
	return testOrigDf


def applyLearnedDictPlusHumanDict(testOrigPath, 
								normOutPath=None, 
								learnedDictPath=u'./005learnedDict/ororaAbbreviationDict.json', 
								humanDictPath=u'./005learnedDict/humanMadeDict/humanMadeOroraAbbreviationDict.json'):
	''' apply the normalization dict'''
	#open the dicts
	learnedDict = myUtils.openJsonFileAsDict(learnedDictPath)
	humanDict = myUtils.openJsonFileAsDict(humanDictPath)
	#open the test dataframe from the path
	testOrigDf = myUtils.getDataFrameFromArgs(testOrigPath, header=False)[0]
	for index, testComment in testOrigDf.iteritems():
		#use the human dict FIRST (priority to the human-made dicts)
		normOutput = ororaZeAbbreviations(testComment, learnedDict, listTheVariations=False)
		#use the learned dict
		normOutput = ororaZeAbbreviations(normOutput, humanDict, listTheVariations=False)
		#save into pandas series
		testOrigDf[index] = normOutput
	#dump normalized output
	if normOutPath != None:
		testOrigDf.to_csv(normOutPath, sep=u'\t', index=False)
	return testOrigDf


def applyNormalizationCrossVal(inputFolderPath, outputFolderPath, outputFileName, outputFormat, dictFolderPath):
	''' applies the normalization dict over cross-validation data '''	
	# spacyModel = myUtils.spacyLoadModel(lang='en')
	spacyModel = None
	#make sure the folder paths end in /
	inputFolderPath = u'{0}/'.format(inputFolderPath) if inputFolderPath[-1] != u'/' else inputFolderPath
	outputFolderPath = u'{0}/'.format(outputFolderPath) if outputFolderPath[-1] != u'/' else outputFolderPath
	#get content of input folder (sets)
	listSetFiles = myUtils.getContentOfFolder(inputFolderPath)
	#eliminate all previous outputs from the align folder
	myUtils.emptyTheFolder(outputFolderPath, outputFormat)
	for nb in range(len(listSetFiles)):
		#we verify that the test set (and therefore all subsequent files) exists
		if str(nb) in u' '.join(listSetFiles):
			nbPattern = myUtils.getNbPattern(nb)
			#each cross validation file must have a number, find all non train files not containing said number as the test
			listOfTestFiles = [ file for file in listSetFiles if not nbPattern.search(file) ]
			listOfTestFiles = [ u'{0}{1}'.format(inputFolderPath, file) for file in listOfTestFiles if u'Orig' in file ]
			#sort the list to get a uniform order of the files (according to the number)
			listOfTestFiles.sort()
			if len(listOfTestFiles) != 0:
				#join all test file names
				myUtils.unifyListOfTestSetsIntoOne(listOfTestFiles, outputUnifiedFilePath=u'./006transformed/temp.tsv')
				#output file path
				outputFilePath = u'{0}{1}{2}.{3}'.format(outputFolderPath, outputFileName, nb, outputFormat)
				#get the right dict file paths
				dictFilePath = u'{0}ororaAbbreviationDict{1}.json'.format(dictFolderPath, nb)
				#launch function and dump
				applyNormalisation(u'./006transformed/temp.tsv', outputFilePath, spacyModel, dictFilePath) #u'./005learnedDict/humanMadeDict/humanMadeOroraAbbreviationDict.json' )
	myUtils.deleteFile(u'./006transformed/temp.tsv')
	return None


#spell checker
#wordCountDict = myUtils.openJsonFileAsDict(u'../utilsString/tokDict/frTokReducedLessThan1000Instances.json')
#applyNormalisation(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv', myUtils.naiveSpellCheckerOrora, u'fr', wordCountDict, False) ###spell checker

#auto and human dict
#applyNormalisation(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv', normalization) #auto dict normalization
#applyLearnedDictPlusHumanDict(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv') #auto+human dict normalization

#auto dict cross val
applyNormalizationCrossVal(inputPath, outputPath, u'transformedTest', u'tsv', dictPath)

#apply it too using the human-auto intersection dict
applyNormalizationCrossVal(inputPath, u'./006transformed/humAutoIntersect/', u'transformedTest', u'tsv', u'./005learnedDict/intersectionHumanAutoDict/')
