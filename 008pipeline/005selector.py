#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse, ast
import myUtils


parser = argparse.ArgumentParser()

parser.add_argument(u'-pn', u'--pathNonMatch', type=str, default=u'./004nonMatchExtracted/nonMatched.tsv',
                    help=u'path to the file containing the alignment of the original train comments')
parser.add_argument(u'-gpl', u'--existingDict', type=dict, default={},
                    help=u'path to an existing learned dict to be enriched')
parser.add_argument(u'-op', u'--outputPathToDict', type=str, default=u'./005learnedDict/ororaAbbreviationDict.json',
                    help=u'path to the output file for the newly learned dict')
args = parser.parse_args()


pathNonMatch = args.pathNonMatch
trainedDict = args.existingDict
outputDictFilePath = args.outputPathToDict


def makeDictFromTsvTrain(pathNonMatch, trainedDict={}, outputDictFilePath=False):
	'''	'''
	#open the dict
	if type(trainedDict) == str:
		trainedDict = myUtils.openJsonFileAsDict(trainedDict)
	#open as a list the non identical elements between the original and the gold
	if type(pathNonMatch) is str:
		with open(pathNonMatch) as nonMatchFile:
			nonMatchList = []
			line = nonMatchFile.readline()
			while line:
				nonMatchList.append(ast.literal_eval(line.replace(u', \n', u'').replace(u',\n', u'').replace(u'\n', u'')))
				line = nonMatchFile.readline()
	#get the gold standard data to which compare the training data
	for nonMatchingAlignment in nonMatchList:
		#if the list is not empty
		if nonMatchingAlignment:
			for nonMatchTupl in nonMatchingAlignment:
				#use the original token as a key
				trainedDict[nonMatchTupl[0]] = trainedDict.get( nonMatchTupl[0], list() )+[nonMatchTupl[1]]
	#clean the dict
	for origKey, goldValList in dict(trainedDict).items():
		#eliminate all the elements in the dict that have an empty symbol as a value
		if set(goldValList) == {u'∅'}:
			del trainedDict[origKey]
		#########elif len(goldValList) != 1:
		#########	del trainedDict[origKey]
		#eliminate the elements containing a number character
		elif myUtils.detectNbChar(origKey) == True:
			del trainedDict[origKey]
		else:
			#change the goldValList into a sorted list with a count of the recurrences
			goldValSortedList = []
			#eliminate the empty symbol from the list
			goldValList = [ elem for elem in goldValList if elem not in [u'∅', u''] ]
			for goldVal in set(goldValList):
				#count their instances
				counter = 0
				for gv in goldValList:
					if goldVal == gv:
						counter += 1
				#add the token and the normalized score
				goldValSortedList.append( (goldVal, float(counter)/float(len(goldValList))) )
			#sort the list
			goldValSortedList.sort(reverse=True, key=lambda x: x[1])
			trainedDict[origKey] = goldValSortedList 
		
		
		'''
		#eliminate all the elements in the dict that have multiple possible outputs or if the value is an empty symbol
		if len(goldValList) != 1 or set(goldValList) == {u'∅'}:
			del trainedDict[origKey]
		#eleiminate the elements containing a number character
		elif myUtils.detectNbChar(origKey) == True:
			del trainedDict[origKey]
		else:
			trainedDict[origKey] = goldValList[0]
		'''
		'''
		#eliminate all the elements in the dict that have multiple possible outputs or if the value is an empty symbol
		if len(goldValList) != 1 or set(goldValList) == {u'∅'}:
			del trainedDict[origKey]
		#eleiminate the elements containing a number character
		elif myUtils.detectNbChar(origKey) == True:
			del trainedDict[origKey]
		else:
			trainedDict[origKey] = goldValList[0]
		'''
	print(len(trainedDict))
	#dump the dict
	if outputDictFilePath != False:
		myUtils.dumpDictToJsonFile(trainedDict, outputDictFilePath, overwrite=True)
	return trainedDict


makeDictFromTsvTrain(pathNonMatch, trainedDict, outputDictFilePath)