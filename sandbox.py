'''
from flair.embeddings import FlairEmbeddings
from flair.data import Token

flair_embedding_forward = FlairEmbeddings('multi-forward-fast')

token = Token('green')

flair_embedding_forward.embed(token)

print(token)
'''


'''
import utilsOs
import fastText
from fastText.util import util
import numpy as np

class FastTextNN:
	""" found in comments in https://github.com/facebookresearch/fastText/issues/384 """
	
	def __init__(self, ft_model=None, ft_matrix=None):
		if ft_model == None:
			ft_model = fastText.load_model(u'/data/rali5/Tmp/alfonsda/fasttextVectorModels/wiki.fr.bin')
		self.ft_model = ft_model		
		self.ft_words = ft_model.get_words()
		self.word_frequencies = dict(zip(*ft_model.get_words(include_freq=True)))
		self.ft_matrix = ft_matrix
		if self.ft_matrix is None:
			self.ft_matrix = np.empty((len(self.ft_words), ft_model.get_dimension()))
			for i, word in enumerate(self.ft_words):
				self.ft_matrix[i,:] = ft_model.get_word_vector(word)
	

	def find_nearest_neighbor(self, query, vectors, n=10,  cossims=None):
		"""
		query is a 1d numpy array corresponding to the vector to which you want to
		find the closest vector
		vectors is a 2d numpy array corresponding to the vectors you want to consider

		cossims is a 1d numpy array of size len(vectors), which can be passed for efficiency
		returns the index of the closest n matches to query within vectors and the cosine similarity (cosine the angle between the vectors)

		"""
		if cossims is None:
			cossims = np.matmul(vectors, query, out=cossims)

		norms = np.sqrt((query**2).sum() * (vectors**2).sum(axis=1))
		cossims = cossims/norms
		result_i = np.argpartition(-cossims, range(n+1))[1:n+1]
		return list(zip(result_i, cossims[result_i]))


	def nearest_words(self, word, n=10, word_freq=None):
		result = self.find_nearest_neighbor(self.ft_model.get_word_vector(word), self.ft_matrix, n=n)
		if word_freq:
			return [(self.ft_words[r[0]], r[1]) for r in result if self.word_frequencies[self.ft_words[r[0]]] >= word_freq]
		else:
			return [(self.ft_words[r[0]], r[1]) for r in result]





model = fastText.load_model(u'/data/rali5/Tmp/alfonsda/fasttextVectorModels/wiki.fr.bin')
print(model.get_dimension())

tok = (model.get_word_vector('machine'))

n = FastTextNN()
print(n.nearest_words('minuteor'))

'''
'''
import os
os.environ['LD_LIBRARY_PATH'] = '/u/alfonsda/anaconda3/lib/'
import flair
import re

def getElemsNotInIterObj(elemDict, iterObj, replaceKeyForValue=False):
	"""given a dict of elements and an iterable object, if the elements are
	found in the iterable object, it replaces the None value with the iterable element """
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


#print(getElemsNotInIterObj(['abc', 3, 'abcd', 'acc'], ['abc', 'abfc', 'aebc'], replaceKeyForValue=False))
'''

'''
from pywiktionary import Wiktionary

wikt = Wiktionary(XSAMPA=True)

dump_file = "/data/rali5/Tmp/alfonsda/wikiDump/wiktionary/frwiktionary-20190201-pages-articles-multistream.xml"
pron = wikt.extract_IPA(dump_file)
'''
def ororaZe(string, advanced=False):
	''' 
	' --> ''
	\s\s --> \s
	a --> A
	à --» A
	###########
	the "plus" option:	
	- --> \s
	'''
	#replace simple apostrophe with 2 apostrophes
	string = string.replace(u"'", u"''")
	#replace multiple spaces with 1 space
	string = re.sub(r'(\s)+', ' ', string)
	#advanced ororazation
	if advanced != False:
		#replace the hyphens with 1 space (the only place multiple spaces appear is where there use to be an hyphen sorrounded by spaces) 
		string = string.replace(u'-', u' ')
		#replace symbol chars with their equivalent
		string = string.replace(u'???', u'?').replace(u'. . . .', u'0')
		string = string.replace(u'. .', u'0').replace(u'??', u'?').replace(u'?!?', u'?').replace(u'_____', u' ')
		string = string.replace(u'@', u'A').replace(u'[ ]', u'OK').replace(u'^', u' ').replace(u'_', u' ')
		###string = string.replace(u'<(>&<)>', u'&').replace(u'</>', u'').replace(u'<H>', u'').replace(u'<U>', u'').replace(u'"', u'apostrophe').replace(u'**', u'0')
	#uppercase it all
	string = string.upper()
	#replace diacritical characters with non diacritical characters
	replacements = [(u'A', u'ÀÂ'), (u'E', u'ÉÈÊ'), (u'I', u'ÎÏ'), (u'O', u'Ô'), (u'U', u'ÙÛÜ'), (u'C', u'Ç')]
	for replaceTuple in replacements:
		for char in replaceTuple[1]:
			string = string.replace(char, replaceTuple[0])
	return string
'''
import utilsString, utilsOs, re

wordCountDict = utilsOs.openJsonFileAsDict(u'./utilsString/tokDict/frTokReducedLessThan1000Instances.json')

line = 'PDF A METTRE HAUT-PARLEURS SUR CANAL 2 13.10.2017 10:14:48 EST Lorraine Fournel (FOURNELO) *DEMANDE PAR A.BRIE COURRIEL 13.10.2017'
normOutput = str(line)

normOutput, dejavuDict = utilsString.naiveSpellCheckerOrora(normOutput.lower(), {}, u'fr', wordCountDict, returnCorrectedTokenScore=False, captureSymbols=[r'\+', r'\.', r'\(', r'\)', r'\[', r'\]', r'\{', r'\}', r'\#', r'\$', r'%', r'&', r'\'', r'\*', r'`', r'\|', r'~', r':', r'-'])

print(ororaZe(normOutput, True))
'''

print('xdcvbn'[:-1])