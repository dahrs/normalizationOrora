 
import re, codecs
from collections import Counter
import utilsDataStruct

import utilsString




#utilsString.makeTokenCountDictFromText(u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/rawText/en.txt', u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/enTok.json')
#print(utilsString.naiveSpellChecker(u''' superve kollection de jdyaux ''', u'fr'))

inputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/rawText/en.txt'
outputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/tokDict/enTok3gram.json'
makeTokNgramCountDictFromText(inputPath, outputPath, n=3)

inputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/rawText/fr.txt'
outputPath = u'/data/rali5/Tmp/alfonsda/wikiDump/outputWikidump/tokDict/frTok3gram.json'
makeTokNgramCountDictFromText(inputPath, outputPath, n=3)
