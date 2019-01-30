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

import utilsString

l = ['aaaaaa', 'bbbbbbb', 'cccccc', 'dddddd', 'eeeeeee']

for tok in l:
	utilsString.edits1(tok)