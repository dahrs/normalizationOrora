#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
import pandas as pd



parser = argparse.ArgumentParser()

parser.add_argument(u'-top', u'--testOriginalPath', type=str, default=u'./002sets/testOrig.tsv',
                    help=u'path to the file containing the original comments of the test')
parser.add_argument(u'-trp', u'--transformedPath', type=str, default=u'./006transformed/transformedTest.tsv',
                    help=u'path to the file where we will dump the transformed comments of the test')
parser.add_argument(u'-nfd', u'--normalizationFunctionOrDict', type=str, default=u'./005learnedDict/ororaAbbreviationDict.json', #humanMadeOroraAbbreviationDict.json
                    help=u'path to the learned dict file')
args = parser.parse_args()



testOrigPath = args.testOriginalPath
normOutPath = args.transformedPath
normalization = args.normalizationFunctionOrDict

def ororaZeAbbreviations(string, abbrDict=None, listTheVariations=False):
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
		abbrDict = myUtils.openJsonFileAsDict(u'./005learnedDict/ororaAbbreviationDict.json')
	#open the abbr dict file if it's a path
	elif type(abbrDict) is str:
		abbrDict = myUtils.openJsonFileAsDict(abbrDict)
	#abbreviation replacement
	stringList = string.split(u' ')	
	if type(abbrDict[list(abbrDict.keys())[0]]) is list:
		for index, token in enumerate(stringList):
			#if the token is in the dict
			if makeReplacements(token).upper() in abbrDict:
				minScore = 0.55
				#if we search only for the first and most common option
				if listTheVariations == False:
					#if the token has a reliable score
					###if abbrDict[makeReplacements(token).upper()][0][1] >= minScore:
					###	stringList[index] = abbrDict[makeReplacements(token).upper()][0][0]
					#use only the tokens having only one way of transcribing
					if len(abbrDict[makeReplacements(token).upper()]) == 1:
						stringList[index] = abbrDict[makeReplacements(token).upper()][0][0]
					else:
						stringList[index] = makeReplacements(token).upper()
				#if we want to return a list of all the possibilities in decreasing order
				else:
					variations = [ var[0] for var in abbrDict[makeReplacements(token).upper()] if var[1] >= minScore ]
					stringList[index] = u'¤'.join(variations) if len(variations) != 0 else makeReplacements(token).upper()
		#stringList = [ token if makeReplacements(token).upper() not in abbrDict else abbrDict[makeReplacements(token).upper()][0][0] for token in stringList ]
	else:
		stringList = [ token if makeReplacements(token).upper() not in abbrDict else abbrDict[makeReplacements(token).upper()] for token in stringList ]
	#elimination of the empty elements u'' or u'∅' if they got in (somehow)
	#stringList = [ token for token in stringList if token not in [u'', u'∅'] ]
	string = u' '.join(stringList)
	return string


def applyNormalisation(testOrigPath, normOutPath=None, normalization=None, *args):
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
								humanDictPath=u'./005learnedDict/humanMadeOroraAbbreviationDict.json'):
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



#wordCountDict = myUtils.openJsonFileAsDict(u'../utilsString/tokDict/frTokReducedLessThan1000Instances.json')
#applyNormalisation(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv', myUtils.naiveSpellCheckerOrora, u'fr', wordCountDict, False ###spell checker

applyNormalisation(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv', normalization)
applyNormalisation(u'./002sets/test2Orig.tsv', u'./006transformed/transformedTest2.tsv', normalization)
applyNormalisation(u'./002sets/test3Orig.tsv', u'./006transformed/transformedTest3.tsv', normalization)

#applyLearnedDictPlusHumanDict(u'./002sets/test1Orig.tsv', u'./006transformed/transformedTest1.tsv')
#applyLearnedDictPlusHumanDict(u'./002sets/test2Orig.tsv', u'./006transformed/transformedTest2.tsv')
#applyLearnedDictPlusHumanDict(u'./002sets/test3Orig.tsv', u'./006transformed/transformedTest3.tsv')