#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse, ast
import myUtils


parser = argparse.ArgumentParser()

parser.add_argument(u'-ap', u'--alignedPath', type=str, default=u'./003alignedTrainSet/',
                    help=u'path to the files containing the alignment of the original and gold standard comments')
parser.add_argument(u'-opl', u'--originalAlignedPathOrList', type=str, default=u'./003alignedTrainSet/alignedOrigLists.tsv',
                    help=u'path to the file containing the alignment of the original train comments')
parser.add_argument(u'-gpl', u'--goldAlignedPathOrList', type=str, default=u'./003alignedTrainSet/alignedGSLists.tsv',
                    help=u'path to the file containing the alignment of the gold standard train comments')
parser.add_argument(u'-ofp', u'--outputMatchFilePath', type=str, default=u'./004nonMatchExtracted/matchCounterDict.json',
                    help=u'path to the file containing the matched elements in the train comments')
parser.add_argument(u'-onfp', u'--outputNonMatchFilePath', type=str, default=u'./004nonMatchExtracted/nonMatchCounterDict.json',
                    help=u'path to the file containing the non-matched elements in the train comments')
parser.add_argument(u'-op', u'--outputPath', type=str, default=u'./004nonMatchExtracted/',
                    help=u'path to the folder containing for non-matched and matched elements in the train comments')
args = parser.parse_args()


alignedPath = args.alignedPath
trainOrigPathOrList = args.originalAlignedPathOrList
trainGoldPathOrList = args.goldAlignedPathOrList
outputMatchFilePath = args.outputMatchFilePath
outputNonMatchFilePath = args.outputNonMatchFilePath
outputPath = args.outputPath


def getNonExactMatch(a, b):
	'''return the non identical elements between the original and the gold'''
	if len(a) > len(b):
		b = b + ( [u'∅']*(len(a)-len(b)) )
	elif len(a) < len(b):
		a = a + ( [u'∅']*(len(b)-len(a)) )
	return [ (a[ind], b[ind]) for ind in range(len(a)) if a[ind] != b[ind] ]


def getExactMatch(a, b):
	'''return the non identical elements between the original and the gold'''
	if len(a) > len(b):
		a = a[:len(b)]
	elif len(a) < len(b):
		b = b[:len(a)]
	return [ a[ind] for ind in range(len(a)) if a[ind] == b[ind] ]


def extractNonExactMatch(trainOrigPathOrList, trainGoldPathOrList, 
	outputMatchDictPath=u'./004nonMatchExtracted/matchCounterDict.json', 
	outputNonMatchDictPath=u'./004nonMatchExtracted/nonMatchCounterDict.json', 
	resetMatchingDicts=True):
	''' extracts elements that don't match exaclty between original and gold '''
	nonMatchedList = []
	matchCounterDict, nonMatchCounterDict = {}, {}
	#open the already made dicts if they exist
	if resetMatchingDicts != True:
		matchCounterDict = openJsonFileAsDict(outputMatchDictPath)
		nonMatchCounterDict = openJsonFileAsDict(outputNonMatchDictPath)
	#open as a list
	for index, trainPath in enumerate([trainOrigPathOrList, trainGoldPathOrList]):
		#if we have a path
		if type(trainPath) is str:
			with open(trainPath) as alignedFile:
				trainAlignedList = []
				line = alignedFile.readline()
				while line:
					trainAlignedList.append(ast.literal_eval(line.replace(u', \n', u'').replace(u',\n', u'').replace(u'\n', u'')))
					line = alignedFile.readline()
			#content of the files into the variable trainOrigPathOrList or trainGoldPathOrList, so it's always a list
			if index == 0:
				trainOrigPathOrList = list(trainAlignedList)
			else: 
				trainGoldPathOrList = list(trainAlignedList)
	#get the gold standard data to which compare the training data
	for index, origAlignedList in enumerate(trainOrigPathOrList):
		goldAlignedList = trainGoldPathOrList[index]
		#get the elements not matching exactly
		nonMatchingAlignment = getNonExactMatch(origAlignedList, goldAlignedList)
		#add to the general list
		nonMatchedList.append(nonMatchingAlignment)
		#get the elements matching exactly
		matchingAlignment = getExactMatch(origAlignedList, goldAlignedList)
		#add to the matching dict
		for exactMatch in matchingAlignment:
			matchCounterDict[exactMatch] = matchCounterDict.get(exactMatch, 0) + 1
		#add to the non-matching dict		
		for nonMatch in nonMatchingAlignment:
			if nonMatch[0] not in nonMatchCounterDict:
				nonMatchCounterDict[nonMatch[0]] = {}
			nonMatchCounterDict[nonMatch[0]][nonMatch[1]] = nonMatchCounterDict[nonMatch[0]].get(nonMatch[1], 0) + 1
	#dump the non matching data
	myUtils.dumpRawLines(nonMatchedList, outputNonMatchDictPath.replace(u'nonMatchCounterDict', u'nonMatched').replace(u'.json', u'.tsv'), addNewline=True, rewrite=True)
	#dump the dicts
	myUtils.dumpDictToJsonFile(matchCounterDict, outputMatchDictPath, overwrite=True)
	myUtils.dumpDictToJsonFile(nonMatchCounterDict, outputNonMatchDictPath, overwrite=True)
	return nonMatchedList 



#extractNonExactMatch(trainOrigPathOrList, trainGoldPathOrList, outputMatchFilePath, outputNonMatchFilePath)

myUtils.emptyTheFolder(outputPath, fileExtensionOrListOfExtensions=u'tsv') #empty the non matched tsv files
myUtils.applyFunctCrossVal(alignedPath, outputPath, [u'matchCounterDict', u'nonMatchCounterDict'], u'json', extractNonExactMatch, True)

