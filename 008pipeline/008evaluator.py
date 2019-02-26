#!/usr/bin/python
#-*- coding:utf-8 -*- 


import argparse
import myUtils
import pandas as pd

parser = argparse.ArgumentParser()

parser.add_argument(u'-nfp', u'--normalizedPath', type=str, default=u'./006transformed/transformedTest.tsv',
                    help=u'path to the file where the transformed comments of the test are')
parser.add_argument(u'-gsp', u'--goldStandPath', type=str, default=u'./002sets/testGS.tsv',
                    help=u'path to the test gold standard')
parser.add_argument(u'-rfp', u'--resultFilePath', type=str, default=u'./008result/testResults.tsv',
                    help=u'path to the file where we will dump the results of the evaluation for the test set')
parser.add_argument(u'-v', u'--verbose', type=bool, default=True,
                    help=u'prints the result on the commande line')
args = parser.parse_args()


toBeEvalPath = args.normalizedPath
goldStandPath = args.goldStandPath
resultDfPath = args.resultFilePath
verbose = args.verbose


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
	#if we want to find an exact match 
	elif normalizedString == goldStandard:
		positiveEvalCounter += 1
		evaluation = 1
	else: evaluation = 0
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
	return goldEvalDf 


applyEvaluator(toBeEvalPath, goldStandPath, resultDfPath, verbose)
