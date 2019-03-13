#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
import pandas as pd


parser = argparse.ArgumentParser()

parser.add_argument(u'-ocp', u'--originalCorpusPath', type=str, default=u'./001ororazed/ororized.tsv',
                    help=u'path to the folder there the corpus is')
parser.add_argument(u'-rsl', u'--ratioSizeList', type=list, default=list([0.05, 0.316, 0.316, 0.316]),
                    help=u'list of the ratio size for the train and the test, default is [0.1, 0.3, 0.3, 0.3]')
parser.add_argument(u'-ttp', u'--trainAndTestPath', type=str, default=u'./002sets/',
                    help=u'path to the folder where the train set and test set files should be saved')
args = parser.parse_args()


origDf = args.originalCorpusPath
ratioSizes = args.ratioSizeList
outputFolderPath = args.trainAndTestPath



def makeTrainTestValidSetsFromTsv(origDf=u'./001corpus/inputOutputGs.tsv', ratioSizes=[0.2, 0.8], outputFolderPath=u'./002sets/'):
	''' given the dataframe with the whole original input, returns 2 or 3 distinct
	dataframes containing a randomly selected elements corresponding to the given 
	ratio sizes. The ratioSizes order must be: TRAIN - TEST - VALIDATION'''
	if outputFolderPath != None:
		outputFolderPath = u'{0}/'.format(outputFolderPath) if outputFolderPath[-1] != u'/' else outputFolderPath
	#get the data frame
	origDf = myUtils.getDataFrameFromArgs(origDf)
	#get rid of tabs in the column content
	origDf = origDf.applymap(myUtils.replaceTabs)
	#get the actual sizes from the ratios
	nSizes = [ int(r*len(origDf)) for r in ratioSizes ] #we avoid using the argument "frac" from "pd.sample" function
	#train-test set
	trainDf = origDf.sample(n=nSizes[0], replace=False) #train set
	print(1111, 'train: ', len(trainDf))
	remainingDf = origDf.iloc[~origDf.index.isin(trainDf.index)]
	testDf = remainingDf.sample(n=nSizes[1], replace=False) #test set
	#determine if it must return a train-test set or a train-validation-test set
	if len(nSizes) == 2:
		#dumping
		if outputFolderPath != None:
			trainDf[u'CommentIn'].to_csv(u'{0}trainOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			trainDf[u'CommentOut'].to_csv(u'{0}trainGS.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentIn'].to_csv(u'{0}testOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentOut'].to_csv(u'{0}testGS.tsv'.format(outputFolderPath), sep='\t', index=False)
		return trainDf, testDf
	#train-validation-test set
	elif len(nSizes) == 3: 
		remainingDf = remainingDf.iloc[~remainingDf.index.isin(testDf.index)]
		validDf = remainingDf.sample(n=nSizes[2], replace=False)
		#dumping
		if outputFolderPath != None:
			trainDf[u'CommentIn'].to_csv(u'{0}trainOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			trainDf[u'CommentOut'].to_csv(u'{0}trainGS.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentIn'].to_csv(u'{0}testOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentOut'].to_csv(u'{0}testGS.tsv'.format(outputFolderPath), sep='\t', index=False)
			validDf[u'CommentIn'].to_csv(u'{0}validationOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			validDf[u'CommentOut'].to_csv(u'{0}validationGS.tsv'.format(outputFolderPath), sep='\t', index=False)
		return trainDf, testDf, validDf#train-validation-test set
	#1 train and 3 test sets
	elif len(nSizes) == 4: 
		remainingDf = remainingDf.iloc[~remainingDf.index.isin(testDf.index)]
		test2Df = remainingDf.sample(n=nSizes[2], replace=False)		
		remainingDf = remainingDf.iloc[~remainingDf.index.isin(test2Df.index)]
		test3Df = remainingDf.sample(n=nSizes[3], replace=False)
		#dumping
		if outputFolderPath != None:
			trainDf[u'CommentIn'].to_csv(u'{0}trainOrig.tsv'.format(outputFolderPath), sep='\t', index=False)
			trainDf[u'CommentOut'].to_csv(u'{0}trainGS.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentIn'].to_csv(u'{0}test1Orig.tsv'.format(outputFolderPath), sep='\t', index=False)
			testDf[u'CommentOut'].to_csv(u'{0}test1GS.tsv'.format(outputFolderPath), sep='\t', index=False)
			test2Df[u'CommentIn'].to_csv(u'{0}test2Orig.tsv'.format(outputFolderPath), sep='\t', index=False)
			test2Df[u'CommentOut'].to_csv(u'{0}test2GS.tsv'.format(outputFolderPath), sep='\t', index=False)
			test3Df[u'CommentIn'].to_csv(u'{0}test3Orig.tsv'.format(outputFolderPath), sep='\t', index=False)
			test3Df[u'CommentOut'].to_csv(u'{0}test3GS.tsv'.format(outputFolderPath), sep='\t', index=False)
		return trainDf, testDf, test2Df, test3Df
	raise IndexError('The number of ratio sizes is neither 2, 3 nor 4. We require 2 ratio sizes to return a train and test set and 3 to return a train, test and validation sets.')



makeTrainTestValidSetsFromTsv(origDf, ratioSizes, outputFolderPath)