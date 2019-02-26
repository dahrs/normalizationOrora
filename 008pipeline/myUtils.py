#!/usr/bin/python
#-*- coding:utf-8 -*- 

import pandas as pd
import os, codecs, sys, re, functools
from nltk.metrics import distance


######################################################################
# OS FUNCTIONS 
######################################################################

def getDataFrameFromArgs(df1arg, df2arg=None, header=True):
	'''
	we chech if 'df1arg' and 'df2arg' are string paths or pandas dataframes
	'''
	#df1
	if type(df1arg) != str: # or type(df1arg) != unicode:
		df1 = df1arg
	else:
		#with header as df.columns
		if header == True:
			df1 = pd.read_csv(df1arg, sep=u'\t')
		#without header (useful for series instead of df)
		else:
			df1 = pd.read_csv(df1arg, sep=u'\t', header=None)
	#df2
	if df2arg is None:
		return df1
	elif type(df2arg) != str: # or type(df2arg) != unicode:
		df2 = df2arg
	else:
		#with header as df.columns
		if header == True:
			df2 = pd.read_csv(df2arg, sep=u'\t')
		#without header (useful for series instead of df)
		else:			
			df2 = pd.read_csv(df2arg, sep=u'\t', header=None)
	return df1, df2 


def dumpDictToJsonFile(aDict, pathOutputFile='./dump.json', overwrite=False):
	'''
	save dict content in json file
	'''
	import json
	if overwrite == False:
		#to avoid overwriting the name may change
		pathOutputFile = safeFilePath(pathOutputFile)
	#dumping
	with codecs.open(pathOutputFile, u'wb', encoding=u'utf8') as dictFile:
		dictFile.write('')
		json.dump(aDict, dictFile)
	return 


def dumpRawLines(listOfRawLines, filePath, addNewline=True, rewrite=True): 
	'''
	Dumps a list of raw lines in a a file 
	so the Benchmark script can analyse the results
	'''
	folderPath = u'/'.join((filePath.split(u'/'))[:-1]+[''])
	if not os.path.exists(folderPath):
		os.makedirs(folderPath)
	#we dump an empty string to make sure the file is empty
	if rewrite == True:
		openedFile = codecs.open(filePath, 'w', encoding='utf8')
		openedFile.write('')
		openedFile.close()
	openedFile = codecs.open(filePath, 'a', encoding='utf8')
	#we dump every line of the list
	for line in listOfRawLines:
		if addNewline == True:
			openedFile.write(u'%s\n' %(line))
		else:
			openedFile.write(u'%s' %(line))
	openedFile.close()
	return


def createEmptyFile(filePath, headerLine=None):
	'''
	we dump an empty string to make sure the file is empty
	and we return the handle to the ready to append file
	'''
	openFile = codecs.open(filePath, u'w', encoding=u'utf8')
	openFile.write(u'')
	openFile.close()
	openFile = open(filePath, 'a', encoding='utf8', buffering=1)
	#if needed we add a header
	if headerLine != None:
		openFile.write(u'{0}\n'.format(headerLine))
	return openFile


def openJsonFileAsDict(pathToFile):
	'''	loads a json file and returns a dict '''
	import json
	with codecs.open(pathToFile, u'r', encoding=u'utf8') as openedFile:
		return json.load(openedFile)


######################################################################
# ORORAZATION AND NORMALIZATION
######################################################################

def ororaZe(string, advanced=True):
	''' 
	' --> ''
	\s\s --> \s
	a --> A
	à --» A
	###########
	the "plus" option:	
	- --> \s
	'''
	if type(string) is int or type(string) is float:
		return string
	#replace simple apostrophe with 2 apostrophes
	string = string.replace(u"'", u"''")
	#this is an encoding problem that clouds our capacity to correctly evaluate our algorithm
	string = string.replace(u'’', u"''").replace(u'«', u'"').replace(u'»', u'"')
	#string = string.replace(u'’', u'�').replace(u'«', u'�').replace(u'»', u'�') #################################
	#replace multiple spaces with 1 space
	string = re.sub(r'(\s)+', ' ', string)
	#advanced ororazation
	if advanced != False:
		string = advancedOroraze(string)
	#uppercase it all
	string = string.upper()
	#replace diacritical characters with non diacritical characters
	replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
	for replaceTuple in replacements:
		for char in replaceTuple[1]:
			string = string.replace(char, replaceTuple[0])
	return string


def advancedOroraze(string):
	''' applies orora changes that are supposed to appear in the dict of pair words '''
	#replace the hyphens with 1 space (the only place multiple spaces appear is where there use to be an hyphen sorrounded by spaces) 
	string = string.replace(u'-', u' ')
	#replace symbol chars with their equivalent
	string = string.replace(u'???', u'?').replace(u'. . . .', u'0')
	string = string.replace(u'. .', u'0').replace(u'??', u'?').replace(u'?!?', u'?').replace(u'_____', u' ')
	string = string.replace(u'@', u'A').replace(u'[ ]', u'OK').replace(u'^', u' ').replace(u'_', u' ')
	###string = string.replace(u'<(>&<)>', u'&').replace(u'</>', u'').replace(u'<H>', u'').replace(u'<U>', u'').replace(u'"', u'apostrophe').replace(u'**', u'0')
	return string


######################################################################
# STRINGS
######################################################################

def eliminateMultipleSpaces(string):
	''''''
	if type(string) is int or type(string) is float:
		return string
	#find all multiple spaces
	listSpaces = re.findall(r'[ ]{3,}', string)
	for spaceChars in listSpaces:
		string = string.replace(spaceChars, u'')
	#replace all double spaces left with a single space
	string = string.replace(u'  ', u' ')
	return string


def detectNbChar(string):
	''''''
	pattern = re.compile(r'[0-9]')
	s = pattern.search(string)
	if s == None:
		return False
	return True


def replaceTabs(string):
	''' replaces tabs with spaces'''
	if type(string) is int or type(string) is float:
		return string
	return string.replace(u'\t', u' ')


######################################################################
# ALIGNMENT
######################################################################

def vecinityAlignmentMatch(tokenList1, tokenList2, alignList1, alignList2, ind1, ind2, endInd2):
	''' return the modified alignment lists if the token in "a" is found in a nearby index in "b"'''
	ind2Temp = int(ind2)
	if tokenList1[ind1] in tokenList2[ind2:endInd2]:
		#look in the vecinity of the string2
		while ind2Temp != endInd2:
			#if it's not that particular element in the window, we add an empty element to the alignment
			if tokenList1[ind1] != tokenList2[ind2Temp]:
				alignList1.append(u'∅')				
				alignList2.append(tokenList2[ind2Temp])				
				ind2 = ind2+1 if ind2+1 != len(tokenList2) else None
				ind2Temp += 1
			#if we find the rigth element
			else:
				alignList1.append(tokenList1[ind1])
				alignList2.append(tokenList2[ind2Temp])
				#change both indices
				ind1 = ind1+1 if ind1+1 != len(tokenList1) else None
				ind2 = ind2+1 if ind2+1 != len(tokenList2) else None
				#we stop to avoid going further than  the found element
				break
	return alignList1, alignList2, ind1, ind2


def makeSimilarityList4FirstTok1(tokens1, tokens2):
	''' given 2 list of tokens, creates an ordered list containing all distances between the first token1 and all the tokens2 '''
	similList = []
	nonMatchTokens2 = []
	#only compare for the immediate tokens2-neighbours that do not appear in tokens1
	for tok2 in tokens2:
		if tok2 not in tokens1:
			nonMatchTokens2.append(tok2)
		else: break
	#make the similarity list with the other tokens
	for i2, tok2 in enumerate(nonMatchTokens2):
		similList.append([ distance.edit_distance(tokens1[0], tok2), tok2, i2 ])
	#order the list
	similList = sorted(similList, key=lambda distList: distList[0])
	return similList


def addTokToALign(immediateSimilList1, immediateSimilList2, tokenList1, tokenList2, alignList1, alignList2, ind1, ind2):
	''''''
	#we add to the token1		
	emptyTokens = [u'∅']*immediateSimilList1[0][2]
	alignList1 = alignList1 + emptyTokens + [tokenList1[ind1]]
	ind1 = ind1+1 if ind1+1 != len(tokenList1) else None
	#we add the token2
	alignList2 = alignList2 + tokenList2[ ind2:(ind2+immediateSimilList1[0][2]+1) ]
	ind2 = ind2+(1+immediateSimilList1[0][2]) if ind2+(1+immediateSimilList1[0][2]) != len(tokenList2) else None
	return alignList1, alignList2, ind1, ind2


def getMostSimilarAlignment(tokenList1, tokenList2, alignList1, alignList2, ind1, ind2, endInd1, endInd2):
	''' looks at the context window of the token and populates the alignString list to match the most similar to the token '''
	immediateSimilList1 = makeSimilarityList4FirstTok1( tokenList1[ind1:endInd1], tokenList2[ind2:endInd2] )
	immediateSimilList2 = makeSimilarityList4FirstTok1( tokenList2[ind2:endInd2], tokenList1[ind1:endInd1] )
	#decide which token (the first one from the first list or form the second list) has better similarity
	if immediateSimilList1[0][0] == immediateSimilList2[0][0]: #if the distance is the same
		#if there is a cross, e.g., l1 = [7, 8] ; l2 = [8, 9]    and the distance is the same
		if immediateSimilList1[0][0] == immediateSimilList2[0][0] and immediateSimilList1[0][2] != 0 and immediateSimilList2[0][2] != 0 and immediateSimilList1[0][2] == immediateSimilList2[0][2]:
			#we return the first token of both lists
			alignList1.append(tokenList1[ind1])
			alignList2.append(tokenList2[ind2])
			#change both indices
			ind1 = ind1+1 if ind1+1 != len(tokenList1) else None
			ind2 = ind2+1 if ind2+1 != len(tokenList2) else None
		#take the first appearing one
		elif immediateSimilList1[0][2] <= immediateSimilList2[0][2]:
			alignList1, alignList2, ind1, ind2 = addTokToALign(immediateSimilList1, immediateSimilList2, tokenList1, tokenList2, alignList1, alignList2, ind1, ind2)
		else:
			alignList2, alignList1, ind2, ind1 = addTokToALign(immediateSimilList2, immediateSimilList1, tokenList2, tokenList1, alignList2, alignList1, ind2, ind1)
	#if the distance for the token1 is smaller
	elif immediateSimilList1[0][0] < immediateSimilList2[0][0]:
		alignList1, alignList2, ind1, ind2 = addTokToALign(immediateSimilList1, immediateSimilList2, tokenList1, tokenList2, alignList1, alignList2, ind1, ind2)
	#if the distance for the token 2 is smaller
	else:
		alignList2, alignList1, ind2, ind1 = addTokToALign(immediateSimilList2, immediateSimilList1, tokenList2, tokenList1, alignList2, alignList1, ind2, ind1)
	return alignList1, alignList2, ind1, ind2 

	
def align2SameLangStrings(string1, string2, windowSize=2, alignMostSimilar=False, tokenizingFunct=None, *args):
	''' given 2 strings in the same language, it aligns them in a table of tuples '''
	alignString1 = []
	alignString2 = []
	#replace repetition of space characters with a distinctive symbol
	for nbSpace in reversed(range(3, 10)):
		if (u' '*nbSpace) in string1:
			string1 = string1.replace(u' '*nbSpace, u' {0} '.format(u'¤*¤¤¤¤'*nbSpace))
		if (u' '*nbSpace) in string2:
			string2 = string2.replace(u' '*nbSpace, u' {0} '.format(u'¤*¤¤¤¤'*nbSpace))
	#tokenize (we don't use the naive regex tokenizer to avoid catching the  "-" and "'" and so on)
	if tokenizingFunct == None:
		string1Tok = string1.split(u' ')
		string2Tok = string2.split(u' ')
	#if there is a particular tokenizing function we wish to use
	else:
		string1Tok = tokenizingFunct(string1, *args)
		string2Tok = tokenizingFunct(string2, *args)
	#replace back the distinctive characters replacing the spaces with actual spaces
	string1Tok = [elem.replace(u'¤*¤¤¤¤', u' ') for elem in string1Tok]
	string2Tok = [elem.replace(u'¤*¤¤¤¤', u' ') for elem in string2Tok]
	#prepare the alignment indexes
	ind1, ind2 = 0, 0
	#start aligning
	while ind1 != len(string1Tok) and ind2 != len(string2Tok):
		#if ind1 and 2 are None
		if ind1 == None and ind2 == None:
			break
		#if ind1 is None
		elif ind1 == None:
			alignString1 = alignString1 + ([u'∅']*len(string2Tok[ind2:]))
			alignString2 = alignString2 + string2Tok[ind2:]
			break
		#if ind2 is None
		elif ind2 == None:
			alignString2 = alignString2 + ([u'∅']*len(string1Tok[ind1:]))
			alignString1 = alignString1 + string1Tok[ind1:]
			break
		#get the end index
		endInd1 = ind1+windowSize+1 if ind1+windowSize+1 < len(string1Tok) else len(string1Tok)
		endInd2 = ind2+windowSize+1 if ind2+windowSize+1 < len(string2Tok) else len(string2Tok)
		#if they correspond
		if string1Tok[ind1] == string2Tok[ind2]:
			#add them to the aligned list
			alignString1.append(string1Tok[ind1])
			alignString2.append(string2Tok[ind2])
			#change both indices
			ind1 = ind1+1 if ind1+1 != len(string1Tok) else None
			ind2 = ind2+1 if ind2+1 != len(string2Tok) else None
		#if the token in string1 is found in a nearby index in string2 or vice-versa
		elif string1Tok[ind1] in string2Tok[ind2:endInd2]:
			alignString1, alignString2, ind1, ind2 = vecinityAlignmentMatch(string1Tok, string2Tok, alignString1, alignString2, ind1, ind2, endInd2)
		#if the token in string2 is found in a nearby index in string1
		elif string2Tok[ind2] in string1Tok[ind1:endInd1]:
			alignString2, alignString1, ind2, ind1 = vecinityAlignmentMatch(string2Tok, string1Tok, alignString2, alignString1, ind2, ind1, endInd1)
		#if we want to try and match the most similar in each vecinity
		elif alignMostSimilar != False:
			alignString1, alignString2, ind1, ind2 = getMostSimilarAlignment(string1Tok, string2Tok, alignString1, alignString2, ind1, ind2, endInd1, endInd2)
		#if the token is nowhere to be found
		else:
			#add them to the aligned list
			alignString1.append(string1Tok[ind1])
			alignString2.append(string2Tok[ind2])
			#change both indices
			ind1 = ind1+1 if ind1+1 != len(string1Tok) else None
			ind2 = ind2+1 if ind2+1 != len(string2Tok) else None
	#delete the aligned empty elements, if there are (for some reason)
	alignString1, alignString2 = delEmptyElements(alignString1, alignString2)
	return alignString1, alignString2


def delEmptyElements(alignList1, alignList2):
	''''''
	cleanAlignList1 = []
	cleanAlignList2 = []
	for index, elem1 in enumerate(alignList1):
		elem2 = alignList2[index]
		#detect empty elements
		if elem1 in [u'', u'∅'] and elem2 in [u'', u'∅']:
			pass
		else:
			cleanAlignList1.append(elem1)
			cleanAlignList2.append(elem2)
	return cleanAlignList1, cleanAlignList2



######################################################################
# DATAFRAME CLEANERS
######################################################################

def cleanCorpusToDifferentFromGsOnly(pathOriginalCorpus, outputPathDiffOnly=None, ororaze=True, advanced=True):
	''' given a tsv path to a df, it returns a df containing only the dissimilar elements 
	#cleanCorpusToDifferentFromGsOnly(u'./000corpus/inputOutputGsCleaned.tsv', u'./000corpus/nonExactMatchCleaned.tsv', ororaze=False, advanced=False) '''
	originalAndGoldDf = getDataFrameFromArgs(pathOriginalCorpus)	
	#get rid of multiple spaces in both the original and the gold standard
	copyDf = originalAndGoldDf.copy()
	copyDf = copyDf.applymap(eliminateMultipleSpaces)
	#get all exact matches
	identicalDf = copyDf.loc[copyDf[u'CommentIn'] == copyDf[u'CommentOut']]
	#eliminate all exact matches
	originalAndGoldDf = originalAndGoldDf.loc[~originalAndGoldDf.index.isin(identicalDf.index)]
	#ororaze the original comments
	if ororaze == True:
		ororazePartial = functools.partial(ororaZe, advanced=advanced)
		ororazedDf = originalAndGoldDf.copy()
		ororazedDf[u'CommentIn'] = ororazedDf[u'CommentIn'].apply(ororazePartial)
		#eliminate all exact matches once ororazed			
		identicalDf = ororazedDf.loc[ororazedDf[u'CommentIn'] == ororazedDf[u'CommentOut']]
		originalAndGoldDf = originalAndGoldDf.loc[~originalAndGoldDf.index.isin(identicalDf.index)]
	#dump df
	if outputPathDiffOnly != None:
		originalAndGoldDf.to_csv(outputPathDiffOnly, sep='\t', index=False)
	return originalAndGoldDf


def cleanCorpusFromEncodingErrors(pathOriginalCorpus, cleanedOutputPath=None):
	''' given a path to a tsv df, it detects specific encoding problems and cleans them using heuristics 
	#cleanCorpusFromEncodingErrors(u'./000corpus/inputOutputGs.tsv', cleanedOutputPath=u'./000corpus/inputOutputGsCleaned.tsv') '''
	def replaceWthGoodChar(alignGold, ind, problemCharList, goodChar):
		#browse the gold to find the problematic encoding error
		#take only the part of the alignment because there might be an ambiguity 
		#for which correct char should replace the problematic one (e.g., '�' can be '’' or '«' or '»')
		indStart = ind-4 if ind-4 > 0 else 0
		indEnd = ind+4 if ind+4 < len(alignGold) else len(alignGold)
		for indGold in range(indStart, indEnd):
			for prblmChar in problemCharList:
				if prblmChar in alignGold[indGold]:
					alignGold[indGold] = alignGold[indGold].replace(prblmChar, goodChar)
		return alignGold
	#get df
	originalAndGoldDf = getDataFrameFromArgs(pathOriginalCorpus)
	#make a df of comments with encoding problems
	problematicDf = originalAndGoldDf.loc[originalAndGoldDf[u'CommentOut'].str.contains(u'�')]
	#replace the problematic characters
	for index, row in problematicDf.iterrows():
		alignOrig, alignGold = align2SameLangStrings(row[u'CommentIn'], row[u'CommentOut'], windowSize=4)
		#delete from the gold the problematic chars that present no ambiguity
		alignGold = [ elem.replace(u'’', u"''").replace(u'«', u'"').replace(u'»', u'"') for elem in alignGold]
		#browse the alignment lists to know what to replace
		for ind, origElem in enumerate(alignOrig):
			if u'’' in origElem:
				#replace the problematic char in the original
				alignOrig[ind] = origElem.replace(u'’', u"'")
				alignGold = replaceWthGoodChar(alignGold, ind, problemCharList=[u'’', u'�'], goodChar=u"''")#we replace it with 2 single quotes because it corresponds to the ororazed format
			if u'«' in origElem or u'»':
				#replace the problematic char in the original
				alignOrig[ind] = origElem.replace(u'«', u'"').replace(u'»', u'"')
				alignGold = replaceWthGoodChar(alignGold, ind, problemCharList=[u'«', u'»', u'�'], goodChar=u'"')#we replace the « and the » characters with the same " char
		#replace row content with corrected comments
		problematicDf[u'CommentIn'][index] = u' '.join( [t for t in alignOrig if t != u'∅'] )
		problematicDf[u'CommentOut'][index] = u' '.join( [t for t in alignGold if t != u'∅'] )
	#replace the original rows with the solved ones
	originalAndGoldDf.update(problematicDf)
	#dump
	if cleanedOutputPath != None:
		originalAndGoldDf.to_csv(cleanedOutputPath, sep='\t', index=False)
	return originalAndGoldDf



#cleanCorpusFromEncodingErrors(u'./000corpus/inputOutputGs.tsv', cleanedOutputPath=u'./000corpus/inputOutputGsCleaned.tsv')


