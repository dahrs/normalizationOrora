import utilsString, utilsDataStruct, utilsStats
import codecs

#df1 = u'/u/alfonsda/Documents/workRALI/000Orora/002Data/client1input/AVANT_BT_Champs_texte_345.tsv'
#df2 = u'/u/alfonsda/Documents/workRALI/000Orora/002Data/client1output/APRES_ParsingReport(Champs_texte345)NoNewlineNoDoubles.tsv'
'''
df1 = u'/u/alfonsda/Documents/workRALI/000Orora/002Data/client1input/AVANT_Champs_texte_12345.tsv'
df2 = u'/u/alfonsda/Documents/workRALI/000Orora/002Data/client1output/APRES_ParsingReport(Champs_texte_12)NoNewlineNoDoubles.tsv'

dfIntersect, intersectdict = utilsStats.dataframesIntersection(df1, df2, ['Ordre', 'Comments'], outputFilePath=None, lowerCase=True)

print(intersectdict)
'''
def d(func, *argv):
	for arg in argv:
		func(arg)
	print('fin')
def c(func, *argv):
	d(func, *argv)

c(print, 1, 2, 5)