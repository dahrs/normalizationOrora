#!/usr/bin/python
#-*- coding:utf-8 -*- 


import argparse
import myUtils
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument(u'-nfp', u'--normalizedFilePath', type=str, default=u'./006transformed/transformedTest.tsv',
                    help=u'path to the file where the transformed comments of the test are')
parser.add_argument(u'-gsp', u'--goldStandFilePath', type=str, default=u'./002sets/testGS.tsv',
                    help=u'path to the test gold standard')
parser.add_argument(u'-rfp', u'--resultFileFilePath', type=str, default=u'./008result/testResults.tsv',
                    help=u'path to the file where we will dump the results of the evaluation for the test set')
parser.add_argument(u'-np', u'--normalizedPath', type=str, default=u'./006transformed/',
                    help=u'path to the folder where the transformed comments of the test are')
parser.add_argument(u'-gp', u'--goldStandPath', type=str, default=u'./002sets/',
                    help=u'path to the test gold standard folder')
parser.add_argument(u'-rp', u'--resultFilePath', type=str, default=u'./008result/',
                    help=u'path to the folder where we will dump the results of the evaluation for the test set')
parser.add_argument(u'-v', u'--verbose', type=bool, default=True,
                    help=u'prints the result on the commande line')
args = parser.parse_args()


toBeEvalPath = args.normalizedFilePath
goldStandPath = args.goldStandFilePath
resultDfPath = args.resultFileFilePath
verbose = args.verbose
toBeEvalFolderPath = args.normalizedPath
goldStandFolderPath = args.goldStandPath
outputResultFolderPath = args.resultFilePath


def normalizationEvaluator(normalizedString, goldStandard, positiveEvalCounter):
	''' evaluate if the normalized output corresponds to the gold standard '''
	#if we have a list of possibilities in which the gold standard can be found
	if u'¤' in normalizedString:
		evaluation = 0
		tokenizedString = normalizedString.split(u' ')
		for index, token in enumerate(tokenizedString):
			if u'¤' in token:
				tokList = token.split(u'¤')
				for tok in tokList:
					copy = list(tokenizedString)
					copy[index] = tok
					if u' '.join(copy) == goldStandard:
						evaluation = 1
						positiveEvalCounter += 1
						return positiveEvalCounter, evaluation
					##else:
					##	print(1111, u' '.join(copy), goldStandard)
	#if we want to find an exact match 
	elif normalizedString == goldStandard:
		positiveEvalCounter += 1
		evaluation = 1
	else: 
		##print(2222, normalizedString, goldStandard)
		evaluation = 0
	return positiveEvalCounter, evaluation


def applyEvaluator(toBeEvalPath, goldStandPath, resultDfPath=None, verbose=False):
	''' '''
	positiveEvalCounter = 0
	#open the ororazed test dataframe from the path
	toBeEvalDf = myUtils.getDataFrameFromArgs(toBeEvalPath, header=False)[0]
	#open the goldStandard test dataframe from the path
	goldEvalDf = myUtils.getDataFrameFromArgs(goldStandPath, header=False)[0]
	#browse
	for index, goldStandard in goldEvalDf.iteritems():
		toBeEval = toBeEvalDf[index]
		#evaluation    if the normalized output corresponds to the gold standard
		positiveEvalCounter, evaluation = normalizationEvaluator(toBeEval, goldStandard, positiveEvalCounter)
		#save in dataframe, the gold standard df is now a result df
		goldEvalDf[index] = evaluation
	#dump result df
	if resultDfPath != None:
		goldEvalDf.to_csv(resultDfPath, sep='\t', index=False)
		#dump result
		with open(u'{0}.results'.format(resultDfPath), u'w', encoding=u'utf8') as resultFile:
			resultFile.write( u'NORMALIZATION RESULTS\nratio\texact positives\ttotal comments\n{0}\t{1}\t{2}'.format( (float(positiveEvalCounter)/float(len(goldEvalDf))), positiveEvalCounter, len(goldEvalDf) ) )
	#print if needed
	if verbose != False:
		print(u'ratio\texact positives\ttotal comments')
		print(float(positiveEvalCounter)/float(len(goldEvalDf)), positiveEvalCounter, len(goldEvalDf))
	return goldEvalDf, (float(positiveEvalCounter)/float(len(goldEvalDf)), positiveEvalCounter, len(goldEvalDf))


def applyEvaluationCrossVal(toBeEvalPath, goldStandPath, outputResultPath, outputFileName, outputFormat, verbose=True):
	'''  '''
	allResults = []
	#make sure the folder paths end in /
	toBeEvalPath = u'{0}/'.format(toBeEvalPath) if toBeEvalPath[-1] != u'/' else toBeEvalPath
	goldStandPath = u'{0}/'.format(goldStandPath) if goldStandPath[-1] != u'/' else goldStandPath
	outputResultPath = u'{0}/'.format(outputResultPath) if outputResultPath[-1] != u'/' else outputResultPath
	#get content of input folder (sets)
	listSetFiles = myUtils.getContentOfFolder(goldStandPath)
	#eliminate all previous outputs from the align folder
	myUtils.emptyTheFolder(outputResultPath, outputFormat)
	myUtils.emptyTheFolder(outputResultPath, u'.results')
	for nb in range(len(listSetFiles)):
		#we verify that the test set (and therefore all subsequent files) exists
		if str(nb) in u' '.join(listSetFiles):
			nbPattern = myUtils.getNbPattern(nb)
			#each cross validation file must have a number, find all non train files not containing said number as the test
			listOfTestFiles = [ file for file in listSetFiles if not nbPattern.search(file) ]
			listOfTestFiles = [ u'{0}{1}'.format(goldStandPath, file) for file in listOfTestFiles if u'GS' in file ] #gold standard files
			#sort the list to get a uniform order of the files (according to the number)
			listOfTestFiles.sort()
			if len(listOfTestFiles) != 0:
				#join all test file names
				myUtils.unifyListOfTestSetsIntoOne(listOfTestFiles, outputUnifiedFilePath=u'./008result/tempGS.tsv')
				#path to the transformed comments to be evaluated
				toBeEvalFilePath = u'{0}transformedTest{1}.{2}'.format(toBeEvalPath, nb, outputFormat)
				#output file path
				outputFileResultPath = u'{0}{1}{2}.{3}'.format(outputResultPath, outputFileName, nb, outputFormat)
				#launch function and dump
				print(u'#########################', toBeEvalFilePath)
				goldEvalDf, results = applyEvaluator(toBeEvalFilePath, u'./008result/tempGS.tsv', outputFileResultPath, verbose)
				allResults.append(results[0])
	allResults.sort()
	print(u'min :', allResults[0])
	print(u'max :', allResults[-1])
	print(u'mean :', sum(allResults)/len(allResults))
	#myUtils.deleteFile(u'./008result/tempGS.tsv')
	return None

#applyEvaluator(u'./006transformed/transformedTest1.tsv', u'./002sets/test1GS.tsv', u'./008result/testResults1.tsv', verbose)
applyEvaluationCrossVal(toBeEvalFolderPath, goldStandFolderPath, outputResultFolderPath, u'testResults', 'tsv', verbose)
