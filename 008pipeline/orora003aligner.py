#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
import pandas as pd


parser = argparse.ArgumentParser()

parser.add_argument(u'-sfp', u'--setFolderPath', type=str, default=u'./002sets/',
                    help=u'path to the file containing the original comments of the train')
parser.add_argument(u'-otr', u'--originalTrainFilePath', type=str, default=u'./002sets/trainOrig.tsv',
                    help=u'path to the file containing the original comments of the train')
parser.add_argument(u'-gtr', u'--goldStandardTrainFilePath', type=str, default=u'./002sets/trainGS.tsv',
                    help=u'path to the file containing the gold standard comments of the train')
parser.add_argument(u'-nma', u'--nonExactMatchAligner', type=bool, default=False,
                    help=u'heuristic to align the elements that are not an exact match')
parser.add_argument(u'-afp', u'--alignFolderPath', type=str, default=u'./003alignedTrainSet/',
                    help=u'path to the output folder for the lists of the original and gold alignations')
parser.add_argument(u'-oap', u'--origAlignPath', type=str, default=u'./003alignedTrainSet/alignedOrigLists.tsv',
                    help=u'path to the output file for the list of the original comment"s tokens aligned with the gold')
parser.add_argument(u'-gap', u'--goldAlignPath', type=str, default=u'./003alignedTrainSet/alignedGSLists.tsv',
                    help=u'path to the output file for the list of the gold comment"s tokens aligned with the original')
args = parser.parse_args()


setFolderPath = args.setFolderPath
alignFolderPath = args.alignFolderPath

alignMostSimilar = args.nonExactMatchAligner

pathToTrainOrigTsv = args.originalTrainFilePath
pathToTrainGoldTsv = args.goldStandardTrainFilePath
origAlignPath = args.origAlignPath
goldAlignPath = args.goldAlignPath


def makeAlignLists(pathToTrainOrigTsv, pathToTrainGoldTsv, origAlignPath=u'./003alignedTrainSet/alignedOrigLists.tsv', goldAlignPath=u'./003alignedTrainSet/alignedGoldLists.tsv', alignMostSimilar=False, dumpBoth=False):
	'''	'''
	trainOrigAlignedList = []
	trainGoldAlignedList = []	
	#open the train dataframe from the path
	trainOrigDf = myUtils.getDataFrameFromArgs(pathToTrainOrigTsv, header=False)[0]
	trainGoldDf = myUtils.getDataFrameFromArgs(pathToTrainGoldTsv, header=False)[0]
	#get the gold standard data to which compare the training data
	for index, origComment in enumerate(trainOrigDf):
		goldComment = trainGoldDf[index]
		#align the 2
		alignedListOrig, alignedListGold = myUtils.align2SameLangStrings(origComment, goldComment, windowSize=3, alignMostSimilar=alignMostSimilar)
		#add to the lists of aligned elements
		trainOrigAlignedList.append(alignedListOrig)
		trainGoldAlignedList.append(alignedListGold)
	#dump the lists
	myUtils.dumpRawLines(trainOrigAlignedList, origAlignPath, addNewline=True, rewrite=True)
	myUtils.dumpRawLines(trainGoldAlignedList, goldAlignPath, addNewline=True, rewrite=True)
	#in tab separated form
	def dumpStringTsv(alignedList, filePath):
		openFile = myUtils.createEmptyFile(filePath)
		for index, aligned in enumerate(alignedList):
			alignString = u''			
			for ind, elem in enumerate(aligned):
				alignString = u'{0}\t{1}'.format(alignString, elem) if ind != 0 else elem
			#dump
			if index != (len(alignedList)-1):
				openFile.write(u'{0}\n'.format(alignString))
			else:
				openFile.write(alignString)
		openFile.close()
	def dumpBothTsv(origAlign, goldAlign, filePath):
		openFile = myUtils.createEmptyFile(filePath)
		for index, origAligned in enumerate(origAlign):
			goldAligned = goldAlign[index]
			origAlignString = u''
			goldAlignString = u''
			for ind, origElem in enumerate(origAligned):
				goldElem = goldAligned[ind]
				origAlignString = u'{0}\t{1}'.format(origAlignString, origElem) if ind != 0 else origElem
				goldAlignString = u'{0}\t{1}'.format(goldAlignString, goldElem) if ind != 0 else goldElem
			#dump
			if index != (len(origAlign)-1):
				openFile.write(u'orig:\t{0}\ngold:\t{1}\n'.format(origAlignString, goldAlignString))
			else:
				openFile.write(u'orig:\t{0}\ngold:\t{1}'.format(origAlignString, goldAlignString))
		openFile.close()
	#get the right path to dump the grepable alignments
	origPathList = (origAlignPath.replace(u'Lists', u'')).split(u'/')
	goldPathList = (origAlignPath.replace(u'Lists', u'')).split(u'/')
	#dump
	dumpStringTsv(trainOrigAlignedList, u'{0}/grepable/{1}'.format(u'/'.join(origPathList[:-1]), origPathList[-1]) )
	dumpStringTsv(trainGoldAlignedList, u'{0}/grepable/{1}'.format(u'/'.join(goldPathList[:-1]), goldPathList[-1]))
	if dumpBoth != False:
		dumpBothTsv(trainOrigAlignedList, trainGoldAlignedList, u'./003alignedTrainSet/alignment.tsv')
	return trainOrigAlignedList, trainGoldAlignedList



#makeAlignLists(pathToTrainOrigTsv, pathToTrainGoldTsv, origAlignPath, goldAlignPath, alignMostSimilar)

myUtils.emptyTheFolder(u'{0}/grepable/'.format(alignFolderPath), fileExtensionOrListOfExtensions=u'tsv') #delete old files
myUtils.applyFunctCrossVal(setFolderPath, alignFolderPath, [u'alignOrigLists', u'alignGSLists'], u'tsv', makeAlignLists, alignMostSimilar, False)

