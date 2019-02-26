#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse, ast
import myUtils


parser = argparse.ArgumentParser()

parser.add_argument(u'-opl', u'--originalAlignedPathOrList', type=str, default=u'./003alignedTrainSet/alignedOrigLists.tsv',
                    help=u'path to the file containing the alignment of the original train comments')
parser.add_argument(u'-gpl', u'--goldAlignedPathOrList', type=str, default=u'./003alignedTrainSet/alignedGoldLists.tsv',
                    help=u'path to the file containing the alignment of the gold standard train comments')
parser.add_argument(u'-op', u'--outputPath', type=str, default=u'./004nonMatchExtracted/nonMatched.tsv',
                    help=u'path to the file containing the non matched elements in the train comments')
args = parser.parse_args()


trainOrigPathOrList = args.originalAlignedPathOrList
trainGoldPathOrList = args.goldAlignedPathOrList
outputPath = args.outputPath


def getNonExactMatch(a, b):
	'''return the non identical elements between the original and the gold'''
	if len(a) > len(b):
		b = b + ( [u'∅']*(len(a)-len(b)) )
	elif len(a) < len(b):
		a = a + ( [u'∅']*(len(b)-len(a)) )
	return [ (a[ind], b[ind]) for ind in range(len(a)) if a[ind] != b[ind] ]


def extractNonExactMatch(trainOrigPathOrList, trainGoldPathOrList, outputPath=u'./004nonMatchExtracted/nonMatched.tsv'):
	''' '''
	nonMatchedList = []
	#open as a list
	for index, trainPath in enumerate([trainOrigPathOrList, trainGoldPathOrList]):
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
	#dump the dict
	myUtils.dumpRawLines(nonMatchedList, outputPath, addNewline=True, rewrite=True)
	return nonMatchedList 


extractNonExactMatch(trainOrigPathOrList, trainGoldPathOrList, outputPath)