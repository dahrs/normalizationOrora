#!/usr/bin/python
#-*- coding:utf-8 -*- 


import os, codecs, sys, re, functools
import pandas as pd
import multiprocessing as mp
from contextlib import closing
from nltk.metrics import distance
from nltk.corpus import stopwords	
from functools import partial


######################################################################
# OS FUNCTIONS 
######################################################################

def getContentOfFolder(folderPath):
	'''	Gets a list of all the files present in a specific folder '''
	return [file for file in os.listdir(folderPath)]


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
	string = string.replace(u'-', u' ').replace(u"''''", u"''").replace(u"'''", u"''")
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


def isTokenStopWord(token, language=u'fr'):
	''' detects if the token is a stop-word or not '''
	lang = {u'fr':u'french', u'en': u'english'}
	lang = lang[language] if len(language) == 2 else language
	stopWordList = stopwords.words(lang)
	if token.lower() in stopWordList:
		return True
	elif token in [ ororaZe(stopW, advanced=False) for stopW in stopWordList ]:
		return True
	elif token in [ ororaZe(stopW, advanced=True) for stopW in stopWordList ]:
		return True
	return False


def removeStopwords(tokenList, language=u'english'):
	from nltk.corpus import stopwords		
	#stopwords
	to_remove = set(stopwords.words("english") + ['', ' ', '&'])
	return list(filter(lambda tok: tok not in to_remove, tokenList))


def getTokenRegex(capturePunctuation=False, captureSymbols=False, language='english'):
	''''''
	prefix, suffix, punctuation, symbols = r"", r"", r"", r""
	#gets some possible punctuation
	if capturePunctuation == True:
		punctuation = r'[。\.\?\!\:\;¡¿\(\)\[\]\{\}]+|'
	#put all the given puntuation characters in a list, then in a regex string
	elif capturePunctuation != False:
		punctList = [punct for punct in capturePunctuation]
		punctuation = r'[{0}]+|'.format( r''.join(punctList) ) if len(punctList) > 0 else r''
	#adds the apostrophe at the start of the word in english and at the end of the word in other languages
	if captureSymbols == True or u"'" in captureSymbols:
		prefix, suffix = (r"(\b|')", r"\b") if language == 'english' else (r"\b", r"('|\b)")
	#list the symbols
	if captureSymbols == True:
		symbols = r'|-|\+|\#|\$|%|&|\'|\*|\^|_|`|\||~|:|@|<|>'
	elif captureSymbols != False:
		#put all the symbols in a list then transform it into a string
		symbList = [symb for symb in captureSymbols if symb != u"'"]
		symbols = r'{0}'.format( r''.join(symbList) ) if len(symbList) > 0 else r''
	return r"({0}{1}[\w{2}]+{3})".format(prefix, punctuation, symbols, suffix) 


def naiveRegexTokenizer(string, caseSensitive=True, eliminateStopwords=False, language=u'english', capturePunctuation=False, captureSymbols=False):
	'''
	returns the token list using a very naive regex tokenizer
	does not return the punctuation symbols nor the newline
	if captureSymbols is a string or a list of strings then those strings will also be captured 
	(ie, captureSymbols="'" , then r"(\b\w+(\b   |'   ))")
	'''
	#make the regex
	regex = getTokenRegex(capturePunctuation, captureSymbols, language)
	#make list of tokens
	plainWords = re.compile(regex, re.UNICODE)
	tokens = re.findall(plainWords, string.replace(u'\r', u'').replace(u'\n', u' '))
	#if we don't want to be case sensitive
	if caseSensitive != True:
		tokens = [tok.lower() for tok in tokens]
	#if we don't want the stopwords
	if eliminateStopwords != False:
		tokens = removeStopwords(tokens, language=language)
	return tokens


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


##################################################################################
#SPELLING
##################################################################################


def frenchFemininAccordsCodification(string, isInput=False):
	''' replaces all possible french feminin accord with a code containing a 
	number, so the normalization function doesn' change it
	if isInput is False, then we transform the code into the original'''
	femAccCorrespondence = [ (u'ée', u'¤0¤ée¤0¤'), (u'ee', u'¤0¤ee¤0¤'), (u'ÉE', u'¤0¤ÉE¤0¤'), (u'EE', u'¤0¤EE¤0¤'), (u'éE', u'¤0¤éE¤0¤'), (u'Ée', u'¤0¤Ée¤0¤'), (u'éé', u'¤0¤éE¤0¤'), (u'ÉÉ', u'¤0¤Ée¤0¤'), (u'eE', u'¤0¤eE¤0¤'), (u'Ee', u'¤0¤Ee¤0¤') ]
	if isInput != False:
		string = u'{0} '.format(string)
		#find every feminin accord
		femininAccords = re.compile(r'[e|é|E|É]{2}[\s|\.|,|?|!|;|:|)|\]|}]+')
		femininAccordsList = re.findall(femininAccords, string)
		for eeSubStr in femininAccordsList:
			string = string.replace(eeSubStr, u'¤0¤{0}¤0¤{1}'.format(eeSubStr[:2], eeSubStr[-1]))
	else:
		string = string.replace(u'¤0¤', u'')
		if string[-1] == u' ':
			string = string[:-1]
	return string


def wordProbability(word, wordCountDict, N=None): 
	'''Probability of `word`.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	#if the word is not in the dict
	if word not in wordCountDict:
		return 0
	#if the word is present in the dict
	if N == None:
		N = sum(wordCountDict.values())
	return wordCountDict[word] / N


def correction(word, lang=u'en', returnProbabilityScore=False, wordCountDict=None): 
	'''Most probable spelling correction for word.
	based on statistical token frequency from peter norvig spell post : 
	https://norvig.com/spell-correct.html
	'''
	if wordCountDict != None:
		wordCountDict = openJsonFileAsDict(u'../utilsString/tokDict/{0}TokReducedLessThan100Instances.json'.format(lang))
	cadidatesList = candidates(word, wordCountDict)
	maxValWord = (word, 0)
	#evaluate for all candidates wich is most probable
	for candidate in cadidatesList:
		val = wordProbability(candidate, wordCountDict)
		if val > maxValWord[1]:
			maxValWord = (candidate, val)
	#if both the candidate and score are needed
	if returnProbabilityScore != False:
		#return most probable word and its score
		return maxValWord
	#if only the candidate is needed
	else: 
		#return most probable
		return maxValWord[0]


def correctionNgram(ngram, lang=u'en', ngramCountDict=None): 
	'''Most probable spelling correction for ngram.
	based on statistical ngram frequency
		- 'hybrid' : using ngram frequency and if it doesn't find it, uses token frequency
	based on from peter norvig spell post : https://norvig.com/spell-correct.html
	'''
	if ngramCountDict != None:
		ngramCountDict = openJsonFileAsDict(u'../utilsString/tokDict/{0}Tok.json'.format(lang))
	cadidatesList = candidatesNgram(ngram, ngramCountDict)
	maxValNgram = (ngram, 0)
	#evaluate for all candidates wich is most probable
	for candidate in cadidatesList:
		val = wordProbability(candidate, ngramCountDict)
		if val > maxValNgram[1]:
			maxValNgram = (candidate, val)
	#return most probable
	return maxValNgram


def candidates(word, wordCountDict): 
	'''Generate possible spelling corrections for word.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	return (known([word], wordCountDict) or known(edits1(word), wordCountDict) or known(edits2(word), wordCountDict) or [word])


def candidatesNgram(ngram, ngramCountDict): 
	'''Generate possible spelling corrections for word.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	return (known([ngram], ngramCountDict) 
		or known(editsTrigram(ngram), ngramCountDict)
		or [ngram])

def known(words, wordCountDict): 
	'''The subset of `words` that appear in the dictionary of wordCountDict.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	return set(w for w in words if w in wordCountDict)


def edits1(word, lang=u'fr'):
	'''All edits that are one edit away from `word`.
	extracted from peter norvig spell post : https://norvig.com/spell-correct.html'''
	letters	= u'abcdefghijklmnopqrstuvwxyz'
	if lang == u'fr': letters += u'àâçéèêïîôùüû'
	#make all possible 1-distance changes
	splits = [(word[:i], word[i:])		for i in range(len(word) + 1)]
	deletes = [L + R[1:]					for L, R in splits if R]
	transposes = [L + R[1] + R[0] + R[2:]	for L, R in splits if len(R)>1]
	replaces = [L + c + R[1:]				for L, R in splits if R for c in letters]
	inserts = [L + c + R					for L, R in splits for c in letters]
	return set(deletes + transposes + replaces + inserts)


def edits2(word): 
	'''All edits that are two edits away from `word`.
	extracted from peter norvig spell post : https://norvig.com/spell-correct.html'''
	return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def edits3(word): 
	'''All edits that are three edits away from `word`.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	return (e3 for e1 in edits1(word) for e3 in edits2(e1))


def edits4(word): 
	'''All edits that are three edits away from `word`.
	based on peter norvig spell post : https://norvig.com/spell-correct.html'''
	return (e4 for e2 in edits2(word) for e4 in edits2(e2))


def getAllEditsOfToken(token):
	''' Generate all spelling variations for token '''
	return edits1(token).union(edits2(token)).union(set([token]))


def editsTrigram(ngram):
	''' given an ngram, tokenizes, applies the edits to each token,
	then returns the ngram '''
	with closing( mp.Pool(processes=4) ) as pool:
		ngramTokens = naiveRegexTokenizer(ngram)
		token1Edits = pool.apply_async(getAllEditsOfToken, [ngramTokens[0]] )
		#token1Edits = getAllEditsOfToken(ngramTokens[0])
		token2Edits = pool.apply_async(getAllEditsOfToken, [ngramTokens[1]] )
		#token2Edits = getAllEditsOfToken(ngramTokens[1])
		token3Edits = pool.apply_async(getAllEditsOfToken, [ngramTokens[2]] )
		#token3Edits = getAllEditsOfToken(ngramTokens[2])
		setProducts = itertools.product(token1Edits.get(), token2Edits.get(), token3Edits.get())
	return { u' '.join(editSet) for editSet in setProducts }


def getElemsNotInIterObj(elemDict, iterObj, replaceKeyForValue=False):
	'''given a dict of elements and an iterable object, if the elements are
	found in the iterable object, it replaces the None value with the iterable element '''
	#if it's not a dict, make it a dict
	if type(elemDict) is not dict:
		elemList, elemDict = list(elemDict), {}
		for index,key in enumerate(elemList):
			#if the token appears multiple times in the list
			if key in elemDict:
				elemDict[key] = (None, elemDict[key][1]+[index])
			else:
				elemDict[key] = (None, [index])
	#if the element is in the iterable object
	for keyElem,valueElem in elemDict.items():
		if valueElem[0] == None and keyElem in iterObj:
			#if the iterable object is a dict and we want the value, not the key
			if type(iterObj) is dict and replaceKeyForValue != False:
				elemDict[keyElem] = (iterObj[keyElem], valueElem[1])
			else:
				elemDict[keyElem] = (keyElem, valueElem[1])
		#if there is a numeric or ascii symbol character in the token we take it as is
		elif len(re.findall( re.compile(r'([0-9]|-|\+|\!|\#|\$|%|&|\'|\*|\?|\.|\^|_|`|\||~|:|@)' ), keyElem)) > 0:
			elemDict[keyElem] = (keyElem, valueElem[1])
	return elemDict


def applyNaiveStatCorrection(notPresentList, elemDict, lang, wordCountDict, dejavuDict):
	''' given a list of uncorrected tokens, applies a naive statistic spell correction
	and saves the result to the dict '''
	#multi threading
	with closing( mp.Pool(processes=4) ) as pool:
		#put in a variable the function correction with a constant argument lang
		correctionWithConstantLangVar = partial(correction, lang=lang, returnProbabilityScore=False, wordCountDict=wordCountDict)
		#correct each token and put it in a different list using multiprocessing to go faster
		correctedStringTokenList = pool.map( correctionWithConstantLangVar, list(notPresentList) )
	#dump into dict
	for index, notCorrectedTok in enumerate(notPresentList):
		#into the element dict
		elemDict[notCorrectedTok] = ( correctedStringTokenList[index], elemDict[notCorrectedTok][1] )
		#and into the deja vu dict
		dejavuDict[notCorrectedTok] = correctedStringTokenList[index]
	return elemDict, dejavuDict


def gethigherIndex(aDict):
	higherIndex = 0
	for valTupl in aDict.values():
		for ind in valTupl[1]:
			if ind > higherIndex:
				higherIndex = ind
	return higherIndex


def elemDictToList(elemDict):
	''''''
	correctedStringTokenList = [None] * (gethigherIndex(elemDict)+1)
	changedTokenCounter = 0
	for keyTok,valTok in elemDict.items():
		if valTok[0] != None:
			for valIndex in valTok[1]:
				correctedStringTokenList[valIndex] = valTok[0] 
			changedTokenCounter += 1
		else:
			correctedStringTokenList[valTok[1]] = keyTok
	return correctedStringTokenList


def naiveSpellChecker(string, dejavuDict={}, lang=u'en', wordCountDict=None, returnCorrectedTokenScore=False, captureSymbols=False):
	'''
	for each token in the string, it returns the most statistically 
	closely	related and most counted token in the big data
	'''
	def getGreaterVal(listOfLists):
		greater = [None, 0]
		for aList in listOfLists:
			if aList[1] > greater[1]:
				greater = aList
		return greater[0]
	#get the tokens from the string
	stringTokenList = naiveRegexTokenizer(string, caseSensitive=False, eliminateStopwords=False, captureSymbols=captureSymbols)
	#get the most common (and probably correctly written) tokens from wikipedia
	setOfMostCommon = set([ key.lower() for key in openJsonFileAsDict(u'../utilsString/tokDict/{0}TokReducedLessThan1000Instances.json'.format(lang)) ])
	#get the abbreviation dict
	abbreviationDict = { key:getGreaterVal(value) for key,value in openJsonFileAsDict(u'../utilsString/tokDict/{0}AbbrevDictReducedLess1000.json'.format(lang)).items() }
	#verify if the tokens are not already well written	
	elemDict = getElemsNotInIterObj(stringTokenList, setOfMostCommon)
	#verify if not in dejavus
	elemDict = getElemsNotInIterObj(elemDict, dejavuDict, replaceKeyForValue=True)
	#verify if it's not an abbreviation	
	elemDict = getElemsNotInIterObj(elemDict, abbreviationDict, replaceKeyForValue=True)
	#if there are still tokens that have not yet been seen
	notPresentList = [ k for k,v in elemDict.items() if v[0] == None]
	if len(notPresentList) != 0:
		#apply correction
		elemDict, dejavuDict = applyNaiveStatCorrection(notPresentList, elemDict, lang, wordCountDict, dejavuDict)
	#make a list of the final elements to return
	correctedStringTokenList = elemDictToList(elemDict)
	#give a normalized score representing how many tokens in the whole string needed some level of correction
	if returnCorrectedTokenScore != False:
		correctedTokenScore = float(len([ tok for tok in elemDict if tok not in setOfMostCommon ])) / float(len(elemDict))
		return u' '.join(correctedStringTokenList), correctedTokenScore, dejavuDict
	#otherwise
	return u' '.join(correctedStringTokenList), dejavuDict


def naiveSpellCheckerOrora(string, dejavuDict={}, lang=u'en', wordCountDict=None, returnCorrectedTokenScore=False, capturePunctuation=False, captureSymbols=[r'\+', r'\#', r'\$', r'%', r'&', r'\'', r'\*', r'`', r'\|', r'~', r':', r'-', r'¤']):
	'''
	for each token in the string, it returns the most statistically 
	closely	related and most counted token in the big data
	'''	
	def getGreaterVal(listOfLists):
		greater = [None, 0]
		for aList in listOfLists:
			if aList[1] > greater[1]:
				greater = aList
		return greater[0]
	#get the tokens from the string
	stringTokenList = naiveRegexTokenizer(string, caseSensitive=False, eliminateStopwords=False, capturePunctuation=capturePunctuation, captureSymbols=captureSymbols)
	#get the most common (and probably correctly written) tokens from wikipedia, if there is a number or symbol in the set of most commons, eliminate it
	nbAndSymbols = re.compile(r'([0-9]|-|\+|\!|\#|\$|%|&|\'|\*|\?|\.|\^|_|`|\||~|:|@)')
	setOfMostCommon = set([ key.lower() for key in openJsonFileAsDict(u'../utilsString/tokDict/{0}TokReducedLessThan1000Instances.json'.format(lang)) if len(re.findall(nbAndSymbols, key))==0])
	#get the abbreviation dict
	abbreviationDict = { key:getGreaterVal(value) for key,value in openJsonFileAsDict(u'../utilsString/tokDict/{0}AbbrevDictORORA.json'.format(lang)).items() }
	#verify if the tokens are not already well written	
	elemDict = getElemsNotInIterObj(stringTokenList, setOfMostCommon)
	#verify if not in dejavus
	elemDict = getElemsNotInIterObj(elemDict, dejavuDict, replaceKeyForValue=True)
	#verify if it's not an abbreviation	
	elemDict = getElemsNotInIterObj(elemDict, abbreviationDict, replaceKeyForValue=True)
	#if there are still tokens that have not yet been seen
	notPresentList = [ k for k,v in elemDict.items() if v[0] == None]
	if len(notPresentList) != 0:
		#apply correction
		elemDict, dejavuDict = applyNaiveStatCorrection(notPresentList, elemDict, lang, wordCountDict, dejavuDict)
	#make a list of the final elements to return
	correctedStringTokenList = elemDictToList(elemDict)
	#give a normalized score representing how many tokens in the whole string needed some level of correction
	if returnCorrectedTokenScore != False:
		correctedTokenScore = float(len([ tok for tok in elemDict if tok not in setOfMostCommon ])) / float(len(elemDict))
		return u' '.join(correctedStringTokenList), correctedTokenScore, dejavuDict
	#otherwise
	return u' '.join(correctedStringTokenList), dejavuDict


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
		alignGold = [ elem.replace(u'’', u"''").replace(u'‘', u"''").replace(u'«', u'"').replace(u'»', u'"') for elem in alignGold]
		#browse the alignment lists to know what to replace
		for ind, origElem in enumerate(alignOrig):
			if u'’' in origElem:
				#replace the problematic char in the original
				alignOrig[ind] = origElem.replace(u'’', u"'").replace(u'‘', u"''")
				alignGold = replaceWthGoodChar(alignGold, ind, problemCharList=[u'’', u'�'], goodChar=u"''")#we replace it with 2 single quotes because it corresponds to the ororazed format
			if u'«' in origElem or u'»' in origElem :
				#replace the problematic char in the original
				alignOrig[ind] = origElem.replace(u'«', u'"').replace(u'»', u'"')
				alignGold = replaceWthGoodChar(alignGold, ind, problemCharList=[u'«', u'»', u'�'], goodChar=u'"')#we replace the « and the » characters with the same " char
		#replace row content with corrected comments
		problematicDf[u'CommentIn'][index] = u' '.join( [t for t in alignOrig if t != u'∅'] )
		problematicDf[u'CommentOut'][index] = u' '.join( [t for t in alignGold if t != u'∅'] )
	#replace the original rows with the solved ones
	originalAndGoldDf.update(problematicDf)
	#replace in the whole df the unambiguous problematic chars that present no ambiguity
	def mkReplace(string):
		if type(string) is str:
			return string.replace(u'’', u"''").replace(u'‘', u"''").replace(u'«', u'"').replace(u'»', u'"')
		return string
	originalAndGoldDf = originalAndGoldDf.applymap(mkReplace)
	#dump
	if cleanedOutputPath != None:
		originalAndGoldDf.to_csv(cleanedOutputPath, sep='\t', index=False)
	return originalAndGoldDf


def cleanTruncatedComments(pathOriginalCorpus, cleanedOutputPath=None, ororaze=True, advanced=True):
	''' given a path to a tsv df, it detects the truncated comments in the 
	gold and gets rid of them both in the gold an in the orig 
	#cleanTruncatedComments(u'./000corpus/inputOutputGsCleaned.tsv', u'./000corpus/inputOutputGsCleanedTrunc.tsv')'''
	def applyAligner(row):
		alignString1, alignString2 = align2SameLangStrings(row[u'CommentIn'], row[u'CommentOut'], windowSize=4, alignMostSimilar=True)
		row[u'CommentIn'] = u' '.join(alignString1)
		row[u'CommentOut'] = u' '.join(alignString2)
		return row
	#get df
	originalAndGoldDf = getDataFrameFromArgs(pathOriginalCorpus)
	#ororaze
	if ororaze == True:
		ororazePartial = functools.partial(ororaZe, advanced=advanced)
		ororazedDf = originalAndGoldDf.copy()
		ororazedDf[u'CommentIn'] = ororazedDf[u'CommentIn'].apply(ororazePartial)
	#get aligned copy of df
	alignedDf = ororazedDf.apply(applyAligner, axis=1)
	#get all non-truncated matches
	nonTruncDf = alignedDf.loc[~ alignedDf[u'CommentOut'].str.endswith(u'∅ ∅')]
	originalAndGoldDf = originalAndGoldDf.iloc[originalAndGoldDf.index.isin(nonTruncDf.index)]
	#dump
	if cleanedOutputPath != None:
		originalAndGoldDf.to_csv(cleanedOutputPath, sep='\t', index=False)
	return originalAndGoldDf




#cleanCorpusFromEncodingErrors(u'./000corpus/inputOutputGs.tsv', cleanedOutputPath=u'./000corpus/inputOutputGsCleaned.tsv')
#cleanTruncatedComments(u'./000corpus/inputOutputGsCleaned.tsv', u'./000corpus/inputOutputGsCleanedTrunc.tsv')
#cleanCorpusToDifferentFromGsOnly(u'./000corpus/inputOutputGsCleanedTrunc.tsv', u'./000corpus/nonExactMatchCleaned.tsv', ororaze=False, advanced=False)
