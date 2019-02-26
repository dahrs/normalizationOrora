#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse, functools
import myUtils
import pandas as pd


parser = argparse.ArgumentParser()

parser.add_argument(u'-ipp', u'--inputPath', type=str, default=u'./000corpus/inputOutputGsCleaned.tsv', #default=u'./000corpus/nonExactMatchCleaned.tsv', 
                    help=u'path to the file where the string comments to be ororized are')
parser.add_argument(u'-orp', u'--ororazedPath', type=str, default=u'./001ororazed/ororized.tsv',
                    help=u'path to the file where we will dump the ororized comments of the test')
parser.add_argument(u'-aor', u'--advancedOrorization', type=bool, default=True,
                    help=u'indicator if we must apply an advanced or simple ororization')
args = parser.parse_args()


transformedFilePath = args.inputPath
ororazedPath = args.ororazedPath
advanced = args.advancedOrorization


def applyOroraze(transformedFilePath, ororazedPath=None, advanced=False):
	''' '''
	#open the transformed test dataframe from the path
	transformedFileDf = myUtils.getDataFrameFromArgs(transformedFilePath)
	#treat differently if it's a dataframe and if it's a pandas series
	if len(list(transformedFileDf)) == 1: #if it's a pandas series object
		transformedFileDf = transformedFileDf[0]
		for index, transformedComment in transformedFileDf.iteritems():
			ororOutput = myUtils.ororaZe(transformedComment, advanced=advanced)
			#save to df
			transformedFileDf[index] = ororOutput
	else: #if it's a dataframe
		#ororaze the original comments
		ororazePartial = functools.partial(myUtils.ororaZe, advanced=advanced)
		transformedFileDf[u'CommentIn'] = transformedFileDf[u'CommentIn'].apply(ororazePartial)
		#get rid of tabs in the column content
		transformedFileDf = transformedFileDf.applymap(myUtils.replaceTabs)
		#get rid of multiple spaces in both the original and the gold standard
		transformedFileDf = transformedFileDf.applymap(myUtils.eliminateMultipleSpaces)
	#dump normalized output
	if ororazedPath != None:
		transformedFileDf.to_csv(ororazedPath, sep='\t', index=False)
	return transformedFileDf 


applyOroraze(transformedFilePath, ororazedPath, advanced)
