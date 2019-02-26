#!/usr/bin/python
#-*- coding:utf-8 -*- 

import argparse
import myUtils
from tabulate import tabulate

parser = argparse.ArgumentParser()

parser.add_argument(u'-pt', u'--pathToTsv', type=str, default=u'./003alignedTrainSet/alignment.tsv',
                    help=u'path to the tsv file to be pretty printed')
args = parser.parse_args()


pathToTsv = args.pathToTsv


def prettyPrintTsv(pathToTsv):
	with open(pathToTsv) as openedTsv:
		counter = 1
		line = openedTsv.readline()
		while line:
			#get original alignment
			orig = line.replace(u'\n', u'').split(u'\t')
			#get gold alignment
			line = openedTsv.readline()			
			gold = line.replace(u'\n', u'').split(u'\t')
			#color in red the non exact match elements
			for index, origElem in enumerate(orig):
				goldElem = gold[index]
				if origElem != goldElem:
					orig[index] = u'\033[1;31m{0}\033[0m'.format(origElem)
					gold[index] = u'\033[1;31m{0}\033[0m'.format(goldElem)
			print(u'#####################################{0}##########################################'.format(counter))
			#divide the table in 12 elements for it to be printable in the terminal
			for startIndex in range(1, len(orig), 11):
				endIndex = startIndex+11 if startIndex+11 < len(orig) else len(orig)
				#get table to prettyprint
				table = [ [orig[0]]+orig[startIndex:endIndex] , [gold[0]]+gold[startIndex:endIndex] ]
				print( tabulate(table, tablefmt='psql') )
			#get next orig line
			print()
			print()
			line = openedTsv.readline()
			counter += 1


prettyPrintTsv(pathToTsv)