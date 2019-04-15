#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse, ast
import myUtils


parser = argparse.ArgumentParser()

parser.add_argument(u'-ip', u'--inputPath', type=str, default=u'./004nonMatchExtracted/',
                    help=u'path to the folder containing the alignment files')
parser.add_argument(u'-pnl', u'--pathNonMatchList', type=str, default=u'./004nonMatchExtracted/nonMatched.tsv',
                    help=u'path to the file containing the alignment of the original train comments')
parser.add_argument(u'-pm', u'--pathMatch', type=str, default=u'./004nonMatchExtracted/matchCounterDict.json',
                    help=u'path to where the dicts containing the count of the matching tokens are')
parser.add_argument(u'-pnm', u'--pathNonMatch', type=str, default=u'./004nonMatchExtracted/nonMatchCounterDict.json',
                    help=u'path to where the dicts containing the count of the non-matching tokens are')
parser.add_argument(u'-gpl', u'--existingDict', type=dict, default={},
                    help=u'path to an existing learned dict to be enriched')
parser.add_argument(u'-opd', u'--outputPathToDict', type=str, default=u'./005learnedDict/ororaAbbreviationDict.json', 
                    help=u'path to the output file for the newly learned dict')
parser.add_argument(u'-op', u'--outputPath', type=str, default=u'./005learnedDict/', 
                    help=u'path to the folder for the output file')
parser.add_argument(u'-lng', u'--languageCode', type=str, default=u'fr',
                    help=u'language code of the comments')
args = parser.parse_args()

pathNonMatchList = args.pathNonMatchList
pathNonMatch = args.pathNonMatch
pathMatch = args.pathMatch
startDict = args.existingDict
outputDictFilePath = args.outputPathToDict
language = args.languageCode
inputPath = args.inputPath
outputPath = args.outputPath


def undesireableKey(keyString):
	''' analyzes the key and value string and if it detects an undesireable property it returns true '''
	# encoding problems
	# with web-like elements
	if len(myUtils.getHtmlElement(keyString)) != 0:
		return True
	# if there is a punctuation symbol
	for symbol in [u'-', u'_', u'^', u'@', u'[', u']', u'(', u')', u'?', u'!', u'.', u'*', u'/', u'<', u'>', u'&', u'$', u'~', u'"', u"'", u':', u';', u'¤']:
		if symbol in keyString:
			return True
	return False


def undesireableVal(keyString, valString):
	''' analyzes the key and value string and if it detects an undesireable property it returns true '''
	# encoding problems
	if u'�' in valString:
		return True
	# truncated value
	elif myUtils.isStringTruncated(keyString, valString, caseSensitive=True)[0] == True:
		return True
	elif len(myUtils.getHtmlElement(valString)) != 0:
		return True
	# if there is a punctuation symbol
	for symbol in [u'-', u'_', u'^', u'@', u'[', u']', u'(', u')', u'?', u'!', u'.', u'*', u'/', u'<', u'>', u'&', u'$', u'~', u'"', u"'", u':', u';', u'¤']:
		if symbol in valString:
			return True
	return False


def makeDictFromTsvTrain(pathNonMatchList, existingDict={}, pathMatch=None, pathNonMatch=None, language=u'fr', outputDictFilePath=False):
	'''	'''
	#open the trained dict
	if type(existingDict) == str:
		trainedDict = myUtils.openJsonFileAsDict(trainedDict)
	else: trainedDict = dict(existingDict)
	#open the matching dicts
	if pathMatch != None:
		matchCounterDict = myUtils.openJsonFileAsDict(pathMatch)
		nonMatchCounterDict = myUtils.openJsonFileAsDict(pathNonMatch)
	#open as a list the non identical elements between the original and the gold
	if type(pathNonMatchList) is str:
		with open(pathNonMatchList) as nonMatchFile:
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
	#first cleaning: eliminate the elements that appear a lot less than the unchanged variant
	if pathMatch != None:
		for origKey, goldValList in dict(trainedDict).items():
			try:
				nbMatch = matchCounterDict[origKey]
				nbNonMatch = 0
				for indexGold, goldVal in enumerate(goldValList):
					nbNonMatch = nonMatchCounterDict[origKey][goldVal]
					###trainedDict[origKey] = goldValList #don't remove anything, no matter how uncommon
					#remove the gold value if it's not a very common unmatching replacement
					if float(nbMatch)/float(nbMatch+nbNonMatch) >= 0.55:
						del goldValList[indexGold]
						#if the list is empty delete it
						if len(goldValList) == 0:
							del trainedDict[origKey]
						else:
							trainedDict[origKey] = goldValList
					elif nbNonMatch < 10:
						del goldValList[indexGold]
						#if the list is empty delete it
						if len(goldValList) == 0:
							del trainedDict[origKey]
			except KeyError:
				pass
	#second cleaning, get rid of the empty element
	if u'' in trainedDict: del trainedDict[u'']
	#third cleaning, eliminate the elements whose value is way smaller than its key and
	#of the entries whose key have empirically shown to induce errors and delete them
	for origKey, goldValList in dict(trainedDict).items():
		# if the key is undesireable
		if undesireableKey(origKey) == True:
			del trainedDict[origKey]
		else:
			indexesToDel = []
			for indexVal, goldVal in enumerate(list(goldValList)):
				# if the val is much smaller than the key
				if float(len(goldVal))/float(len(origKey)) <= 0.4:
					indexesToDel.append(indexVal)
				# if the val is undesireable
				elif undesireableVal(origKey, goldVal) == True:
					indexesToDel.append(indexVal)
			#we delete the indexes we detected as causing problems
			for indexVal in reversed(indexesToDel):
				del goldValList[indexVal]
			#if we have not produced an empty list, assign it to the trained dict		
			if len(goldValList) == 0:
				del trainedDict[origKey]
			else:
				trainedDict[origKey] = goldValList
	#fourth cleaning, ruled based cleaning
	for origKey, goldValList in dict(trainedDict).items():
		#eliminate all the elements in the dict that have an empty symbol as a value
		if set(goldValList) == {u'∅'} or origKey == u'∅':
			del trainedDict[origKey]
		#eliminate all ambiguous entries
		###elif len(goldValList) != 1:
		###	del trainedDict[origKey]
		#eliminate the elements containing a number character
		elif myUtils.detectNbChar(origKey) == True:
			del trainedDict[origKey]
		#eliminate the elements whose key is a stop-word
		elif myUtils.isTokenStopWord(origKey, language) == True:
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
				goldValSortedList.append( (goldVal, float(counter)/float(len(goldValList)) ) )
			#sort the list and add to the dict
			if len(goldValSortedList) != 0:
				goldValSortedList.sort(reverse=True, key=lambda x: x[1])
				trainedDict[origKey] = goldValSortedList		
	#dump the dict
	if outputDictFilePath != False:
		myUtils.dumpDictToJsonFile(trainedDict, outputDictFilePath, overwrite=True)
	return trainedDict


def dumpDictIntersectAutoAndHuman(autoDict, humanDict=None, outputPath=None):
	''' given 2 dicts makes the intersection of the 2 (keys in common in both of them), then returns and dumps it '''
	newDict = {}
	nonIntersectAutoDict = {}
	#get the dicts if they are not given directly as dicts
	if humanDict == None:
		humanDict = myUtils.openJsonFileAsDict(u'./005learnedDict/humanMadeDict/humanMadeOroraAbbreviationDict.json')
	elif type(humanDict) is str:
		humanDict = myUtils.openJsonFileAsDict(humanDict)
	if type(autoDict) is str:
		autoDict = myUtils.openJsonFileAsDict(autoDict)
	# get the intersection of keys in both dicts
	intersection = set(autoDict.keys()) & set(humanDict.keys())
	for key in intersection:
		newDict[key] = autoDict[key]
	# get the auto keys not appearing in the intersection
	for key, val in autoDict.items():
		if key not in intersection:
			nonIntersectAutoDict[key] = val
	#dump it
	if outputPath == None:
		outputPath = u'./005learnedDict/intersectionHumanAutoDict/humanAutoDict.json'
	myUtils.dumpDictToJsonFile(newDict, pathOutputFile=outputPath, overwrite=True)
	myUtils.dumpDictToJsonFile(nonIntersectAutoDict, pathOutputFile=outputPath.replace(u'HumanAutoDict/', u'HumanAutoDict/nonIntersect/').replace(u'.json', u'NonIntersect.json'), overwrite=True)
	return newDict, nonIntersectAutoDict


def makeDictCrossVal(inputFolderPath, outputFolderPath, startDict):
	'''  '''
	lenFinalDicts = []
	ratioIntersectDicts = []
	myUtils.emptyTheFolder(u'./005learnedDict/intersectionHumanAutoDict/', fileExtensionOrListOfExtensions=u'json')
	myUtils.emptyTheFolder(u'./005learnedDict/intersectionHumanAutoDict/nonIntersect/', fileExtensionOrListOfExtensions=u'json')
	#make sure the folder paths end in /
	inputFolderPath = u'{0}/'.format(inputFolderPath) if inputFolderPath[-1] != u'/' else inputFolderPath
	outputFolderPath = u'{0}/'.format(outputFolderPath) if outputFolderPath[-1] != u'/' else outputFolderPath
	#get content of input folder (sets)
	listSetFiles = myUtils.getContentOfFolder(inputFolderPath)
	#eliminate all previous outputs from the align folder
	myUtils.emptyTheFolder(outputFolderPath, fileExtensionOrListOfExtensions=u'json')
	for nb in range(len(listSetFiles)):
		nbPattern = myUtils.getNbPattern(nb)
		#each cross validation file must have a number, find the files containing said number
		pairedFiles = [ file for file in listSetFiles if nbPattern.search(file)]
		if len(pairedFiles) != 0:
			#get the right paths to the files
			pathToFile0 = u'{0}{1}'.format(inputFolderPath, [file for file in pairedFiles if u'nonMatched' in file][0])
			pathToFile1 = u'{0}{1}'.format(inputFolderPath, [file for file in pairedFiles if u'matchCounter' in file][0])
			pathToFile2 = u'{0}{1}'.format(inputFolderPath, [file for file in pairedFiles if u'nonMatchCounter' in file][0])
			#output path
			outputDictFilePath = u'{0}ororaAbbreviationDict{1}.json'.format(outputFolderPath, nb)
			#launch function and dump
			finalDict = makeDictFromTsvTrain(pathToFile0, startDict, pathToFile1, pathToFile2, u'fr', outputDictFilePath)
			lenFinalDicts.append(len(finalDict))
			#get and dumpt intersection of human and auto dicts
			intersectDict, nonIntersectAutoDict = dumpDictIntersectAutoAndHuman(finalDict, 
				humanDict=None, 
				outputPath=u'./005learnedDict/intersectionHumanAutoDict/ororaAbbreviationDict{0}.json'.format(nb))
			ratioIntersectDicts.append(float(len(intersectDict))/float(len(finalDict)))
	print('mean size of dict nb : ', sum(lenFinalDicts)/len(lenFinalDicts))
	print('in average, {0} percent of the auto dict also appears in the human'.format(sum(ratioIntersectDicts)/float(len(ratioIntersectDicts))))	
	return None


#makeDictFromTsvTrain(pathNonMatch, startDict, pathMatch, pathNonMatch, language, outputDictFilePath)
#makeDictFromTsvTrain(u'./004nonMatchExtracted/nonMatched1.tsv', startDict, u'./004nonMatchExtracted/matchCounterDict1.json', u'./004nonMatchExtracted/nonMatchCounterDict1.json', language, outputDictFilePath)

makeDictCrossVal(inputPath, outputPath, startDict)

