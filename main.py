#!/usr/bin/python
#-*- coding:utf-8 -*-  

import utilsString, utilsDataStruct, utilsNormalization, utilsOs, dataFormater, utilsML


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
frTokenDictReducedLess25 = u'./utilsString/tokDict/frTokReducedLessThan25Instances.json'
frTokenDictReducedLess100 = u'./utilsString/tokDict/frTokReducedLessThan100Instances.json'
frTokenDictReducedLess1000 = u'./utilsString/tokDict/frTokReducedLessThan1000Instances.json'

#utilsString.removeLessFrequentFromBigDataDict(frTokenDict, frTokenDictReducedLess100, minValue=100, removeNumbers=True)

frAbbrDictReducedLess1000 = u'./utilsString/tokDict/frAbbrevDictReducedLess1000.json'
frAbbrDictReducedLessOrora = u'./utilsString/tokDict/frAbbrevDictORORA.json'

#utilsString.makeBigDataDictOfArtificialErrorsAndAbbreviations(frTokenDictReducedLess1000, frAbbrDictReducedLessOrora, errorsEditDist=0, abbreviations=True, unusualAbbrOnly=True)


##################################################################################
#MAKE GOLD STANDARD
##################################################################################

inputPath = u'./002Data/client1input/inputClient1Unified.tsv'
outputPath = u'./002Data/client1output/outputClient1Unified.tsv'
testFilePath = u'./003goldStandard/inputOutputGs.tsv'

###dataFormater.makeGoldStandardOrora(inputPath, outputPath, testFilePath)


##################################################################################
#MAKE BASELINE
##################################################################################

baselinePath = u'./004outputResult/000baselineZeroEffort.tsv'

#utilsNormalization.applyNormalisationGetResult(testFilePath, baselinePath, ororazeOutput=False)

baselinePath = u'./004outputResult/001baselineOrorazedSimple.tsv'

#utilsNormalization.applyNormalisationGetResult(testFilePath, baselinePath, ororazeOutput=(True, False))

baselinePath = u'./004outputResult/002baselineOrorazedAdvanced.tsv'

#utilsNormalization.applyNormalisationGetResult(testFilePath, baselinePath, ororazeOutput=True)


##################################################################################
#MAKE TRAIN, VALIDATION AND TEST SETS
##################################################################################

origDf = u'./003goldStandard/inputOutputGs.tsv'

testSetsPath = u'./005mlModelsDatasets/'

#utilsML.makeTrainTestValidSetsFromTsv(origDf, ratioSizes=[0.2, 0.8], outputFolderPath=testSetsPath)

crossValidSetsPath = u'./005mlModelsDatasets/crossValidation/'

utilsML.makeSetsForCrossVal(origDf, nbSegmentations=0.05, randomize=True, outputFolderPath=crossValidSetsPath)


##################################################################################
#MAKE ABBREVIATION DICT FROM TRAIN
##################################################################################

learnedAbbrDictPath = u'./007learnedDict/learnedOroraAbbrDict.json'
#utilsNormalization.makeDictFromTsvTrain(u'./005mlModelsDatasets/train.tsv', u'CommentIn', u'CommentOut', outputDictFilePath=learnedAbbrDictPath, preOrorazeOrig=False)


##################################################################################
#APPLY STATISTICAL AND NAIVE TOKEN SPELL CHECKER 
##################################################################################

naiveSpellCheckPath = u'./004outputResult/003statSpellCheck.tsv'

#wordCountDict = utilsOs.openJsonFileAsDict(u'./utilsString/tokDict/frTokReducedLessThan1000Instances.json')

#utilsNormalization.applyNormalisationGetResult(testFilePath, naiveSpellCheckPath, True, False, utilsString.naiveSpellCheckerOrora, u'fr', wordCountDict, False)


##################################################################################
#APPLY NAIVE DICT LEARNING
##################################################################################


replacedFromAbbrDictFilePath = u'./004outputResult/004fromLearnedAbbrDict.tsv'
testFilePath = u'./005mlModelsDatasets/test.tsv'

#utilsNormalization.applyNormalisationGetResult(testFilePath, replacedFromAbbrDictFilePath, ororazeOutput=True, useAbbrDict=learnedAbbrDictPath, normalizationFunction=None)


resultFilePath = u'./004outputResult/005fromLearnedAbbrDictCrosVal.results'
alignMostSimilar = True

utilsNormalization.applyNormalisationGetResultCrossVal(crossValidSetsPath, resultFilePath, ororazeOutput=True, preOrorazeOrig=False, alignMostSimilar=alignMostSimilar, normalizationFunction=None)


##################################################################################
#APPLY NAIVE DICT LEARNING WITH IMPROVED EDIT-DIST ALIGNER
##################################################################################



