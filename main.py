#!/usr/bin/python
#-*- coding:utf-8 -*-  

import utilsString, utilsDataStruct, utilsNormalization, utilsOs, dataFormater


##################################################################################
#MAKE NGRAM RESSOURCE FILES
##################################################################################

'''
#make the ngram count dict for the french corpus
###inputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/rawText/fr.txt'
###outputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/tokDict/frTok3gram.json'
inputPath = u'/part/01/Tmp/alfonsda/dump/fr.txt'
outputPath = u'/part/01/Tmp/alfonsda/dump/frTok3gram.json'
utilsString.makeTokNgramCountDictFromText(inputPath, outputPath, n=3)
'''
'''
#make the ngram count dict for the english corpus
inputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/rawText/en.txt'
outputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/tokDict/enTok3gram.json'
utilsString.makeTokNgramCountDictFromText(inputPath, outputPath, n=3) 
'''


##################################################################################
#MAKE RESSOURCES
##################################################################################

frTokenDict = u'./utilsString/tokDict/frTok.json'
frTokenDictReducedLess25 = './utilsString/tokDict/frTokReducedLessThan25Instances.json'
frTokenDictReducedLess100 = './utilsString/tokDict/frTokReducedLessThan100Instances.json'
frTokenDictReducedLess1000 = './utilsString/tokDict/frTokReducedLessThan1000Instances.json'

utilsString.removeLessFrequentFromBigDataDict(frTokenDict, frTokenDictReducedLess100, minValue=1000)


##################################################################################
#MAKE GOLD STANDARD
##################################################################################

inputPath = u'./002Data/client1input/inputClient1Unified.tsv'
outputPath = u'./002Data/client1output/outputClient1Unified.tsv'
goldStandardPath = u'./003goldStandard/inputOutputGs.tsv'

###dataFormater.makeGoldStandardOrora(inputPath, outputPath, goldStandardPath)


##################################################################################
#MAKE BASELINE
##################################################################################

baselinePath = u'./004outputResult/000baseline.tsv'

#utilsNormalization.applyNormalisationGetResult(goldStandardPath, baselinePath)


##################################################################################
#APPLY STATISTICAL AND NAIVE TOKEN SPELL CHECKER 
##################################################################################

naiveSpellCheckPath = u'./004outputResult/000statSpellCheck.tsv'

wordCountDict = utilsOs.openJsonFileAsDict(u'./utilsString/tokDict/frTok.json')

#utilsNormalization.applyNormalisationGetResult(goldStandardPath, naiveSpellCheckPath, utilsString.naiveSpellChecker, u'fr', wordCountDict, False)
