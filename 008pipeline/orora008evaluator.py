#!/usr/bin/python
#-*- coding:utf-8 -*- 


import argparse
import myUtils
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()

parser.add_argument(u'-nfp', u'--normalizedFilePath', type=str, default=u'./006transformed/transformedTest.tsv',
                    help=u'path to the file where the transformed comments of the test are')
parser.add_argument(u'-gsp', u'--goldStandFilePath', type=str, default=u'./002sets/testGS.tsv',
                    help=u'path to the test gold standard')
parser.add_argument(u'-rfp', u'--resultFileFilePath', type=str, default=u'./008result/testResults.tsv',
                    help=u'path to the file where we will dump the results of the evaluation for the test set')
parser.add_argument(u'-np', u'--normalizedPath', type=str, default=u'./006transformed/',
                    help=u'path to the folder where the transformed comments of the test are')
parser.add_argument(u'-gp', u'--goldStandPath', type=str, default=u'./002sets/', # u'./002sets/setForSlidesCrossVal/10percent/',
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


def normalizationEvaluator(normalizedString, goldStandard, evalCount):
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
						evalCount += 1
						return evalCount, evaluation
					##else:
					##	print(1111, u' '.join(copy), goldStandard)
	#if we want to find an exact match 
	elif normalizedString == goldStandard:
		evalCount += 1
		evaluation = 1
	else: 
		#print(2222, normalizedString, goldStandard)
		evaluation = 0
	return evalCount, evaluation


def pppChange(string):
	''' applies the ppp (pas au point pr'es) change in order to 
	measure the quality of the alphanumeric string alone (no symbols) '''
	#replace the web elements
	htmlElementsList = myUtils.getHtmlElement(string)
	for htmlElem in htmlElementsList:
		string = string.replace(htmlElem, u'')
	# delete elements starting with a space
	if string[0] == u' ':
		string = string[1:]
	# delete specific symbols
	for symbol in [u'-', u'_', u'^', u'@', u'[', u']', u'(', u')', u'?', u'!', u'.', u'*', u'/', u'<', u'>', u'&', u'$', u'~', u'"', u"'", u':', u';', u'¤']:
		string = string.replace(symbol, u'')
	# delete repetitive spaces
	for nb in reversed(range(2,21)):
		string = string.replace(u' '*nb, u' ')
	return string


def normalizationPppEvaluator(normalizedString, goldStandard, evalCount):
	''' evaluate if the normalized output corresponds to the gold standard '''
	#find the ppp match
	if pppChange(normalizedString) == pppChange(goldStandard):
		evalCount += 1
		evaluation = 1
	else: 
		evaluation = 0
	return evalCount, evaluation


def applyEvaluator(toBeEvalPath, goldStandPath, resultDfPath=None, verbose=False, spacyModel=None):
	''' '''
	positiveEvalCounter = 0
	positiveEvalCounterPPP = 0
	#open the ororazed test dataframe from the path
	toBeEvalDf = myUtils.getDataFrameFromArgs(toBeEvalPath, header=False)[0]
	#open the goldStandard test dataframe from the path
	goldEvalDf = myUtils.getDataFrameFromArgs(goldStandPath, header=False)[0]
	#make a result df
	resultDf = pd.DataFrame(0, index=np.arange(len(goldEvalDf)), columns=['exactMatch', 'pasAuPointPres'])
	#browse
	for index, goldStandard in goldEvalDf.iteritems():
		toBeEval = toBeEvalDf[index]
		#choose the tokenizer
		goldStandard = u' '.join(myUtils.multTokenizer(goldStandard, whatTokenizer=0, spacyModel=spacyModel))
		#evaluation    if the normalized output corresponds to the gold standard
		positiveEvalCounter, evaluation = normalizationEvaluator(toBeEval, goldStandard, positiveEvalCounter)
		positiveEvalCounterPPP, evaluationPpp = normalizationPppEvaluator(toBeEval, goldStandard, positiveEvalCounterPPP)
		#save in dataframe result df
		resultDf['exactMatch'][index] = evaluation
		resultDf['pasAuPointPres'][index] = evaluationPpp
	#dump result df
	if resultDfPath != None:
		resultDf.to_csv(resultDfPath, sep='\t', index=False)
		#dump result
		with open(u'{0}.results'.format(resultDfPath), u'w', encoding=u'utf8') as resultFile:
			resultFile.write( u'NORMALIZATION RESULTS\nratio\texact positives\ttotal comments\n{0}\t{1}\t{2}'.format( (float(positiveEvalCounter)/float(len(goldEvalDf))), positiveEvalCounter, len(goldEvalDf) ) )
		#dump trash results in a temp file
		trashSeries1 = toBeEvalDf.iloc[resultDf['exactMatch'].values == 0]
		trashSeries2 = goldEvalDf.iloc[resultDf['exactMatch'].values == 0]
		trashDf = pd.DataFrame(dict(SystemOutput=trashSeries1, GoldStandard=trashSeries2))
		trashPath = u'./008result/trash.tsv'
		trashGrepSystOutputPath = u'./008result/trashSystOutput.tsv'
		trashGrepSystGoldStandPath = u'./008result/trashGoldStand.tsv'
		#if it already exists append to it
		if myUtils.theFileExists(trashPath):
			#prepare dump excel readeable
			tempDf = myUtils.getDataFrameFromArgs(trashPath, header=True)
			trashDf = pd.concat([tempDf, trashDf]).drop_duplicates()
		#dump excel readeable
		trashDf.to_csv(trashPath, sep='\t', index=False, header=True)
		#dump grepable files
		trashDf[u'SystemOutput'].to_csv(trashGrepSystOutputPath, sep='\t', index=False, header=False)
		trashDf[u'GoldStandard'].to_csv(trashGrepSystGoldStandPath, sep='\t', index=False, header=False)
	#print if needed
	if verbose != False:
		print(u'EXACT MATCH :')
		print(u'ratio\texact positives\ttotal comments')
		print(float(positiveEvalCounter)/float(len(resultDf)), positiveEvalCounter, len(resultDf))		
		print(u'PAS AU POINT PRES :')
		print(u'ratio\texact positives\ttotal comments')
		print(float(positiveEvalCounterPPP)/float(len(resultDf)), positiveEvalCounterPPP, len(resultDf))
	return resultDf, ( float(positiveEvalCounter)/float(len(resultDf)), positiveEvalCounter, float(positiveEvalCounterPPP)/float(len(resultDf)), positiveEvalCounterPPP, len(resultDf) )


def applyEvaluationCrossVal(toBeEvalPath, goldStandPath, outputResultPath, outputFileName, outputFormat, verbose=True):
	'''  '''
	allResultsExactMatch = []
	allResultsPPP = []
	# spacyModel = myUtils.spacyLoadModel(lang='en')
	spacyModel = None
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
				goldEvalDf, results = applyEvaluator(toBeEvalFilePath, u'./008result/tempGS.tsv', outputFileResultPath, False, spacyModel=spacyModel)
				allResultsExactMatch.append(results[0])
				allResultsPPP.append(results[2])
	allResultsExactMatch.sort()
	print(u'EXACT MATCH :')	
	print(u'min :', allResultsExactMatch[0])
	print(u'max :', allResultsExactMatch[-1])
	print(u'mean :', sum(allResultsExactMatch)/len(allResultsExactMatch))
	allResultsPPP.sort()
	print(u'PAS AU POINT PRES :')
	print(u'min :', allResultsPPP[0])
	print(u'max :', allResultsPPP[-1])
	print(u'mean :', sum(allResultsPPP)/len(allResultsPPP))
	#myUtils.deleteFile(u'./008result/tempGS.tsv')
	return None

#applyEvaluator(toBeEvalPath=u'./002sets/crossValidationOrig0.tsv', goldStandPath=u'./002sets/crossValidationGS0.tsv', resultDfPath=u'./008result/testResults1.tsv', verbose=verbose)
applyEvaluationCrossVal(toBeEvalFolderPath, goldStandFolderPath, outputResultFolderPath, u'testResults', 'tsv', verbose)
print(u'AUTO HUM INTERSECTION DICT : ')
applyEvaluationCrossVal(u'./006transformed/humAutoIntersect/', goldStandFolderPath, u'./008result/humAutoIntersect', u'testResults', 'tsv', verbose)