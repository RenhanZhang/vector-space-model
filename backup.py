# name: Renhan Zhang
# unique name: rhzhang
from os import listdir
from os.path import isfile, join
import operator
import sys
import math
import re
from PorterStemmer import PorterStemmer

# why re.split('(\W+)', 'Words, words, words.') produces ['Words', ', ', 'words', ', ', 'words', '.', '']
# while re.split('\W+', 'Words, words, words.') produces ['Words', 'words', 'words', '']
# https://docs.python.org/2/library/re.html

#ps = PorterStemmer()
#stemmed_token = ps.stem(token, 0, len(token)-1)

# include file_with_Porter_stemmer_code?

#last line

def removeSGML(str):
    return re.sub('<.+?>', '', str)

def extract(l, pat, str, sub):
    l.extend(re.findall(pat,str))
    str = re.sub(pat, sub, str)
    return str

def tokenizeText(str):
    l = []
    # extract floating numbers -xxx.xxx
    pat = '[+-]?\d+\.\d+'
    str = extract(l, pat, str, '')

    #extract integer
    pat = '[\+\-]?\d+'
    str = extract(l, pat, str, '')

    # deal with U.S.A..
    str = re.sub('\.{2}', '.', str)

    #tokenization of '.'
    pat = '(?:\w+\.)+'
    str = extract(l, pat, str, '')

    #tokenization of 's, 're, 'm
    pat = '\'s'
    str = extract(l, pat, str, '')

    pat = '\'re'
    str = re.sub(pat, ' are', str)

    pat = '\'m'
    str = re.sub(pat, ' am', str)

    # tokenization of dates: 01/01/2014, 01.01.2014, 01-01-2014, 01 01 2014,
    pat = '(\d{2}/\d{2}/\d{4}) | (\d{2}.\d{2}.\d{4}) | (\d{2}-\d{2}-\d{4}) | (\d{2}\s\d{2}\s\d{4})  '
    str = extract(l, pat, str, '')

    # tokenization of '-'
    pat = '(?:\w+-)+\w+'
    str = extract(l, pat, str, '')


    # remove special char: ,  .  "  :  ;  '  ?
    str = re.sub(',|\.|"|:|;|\'|\?|\(|\)', ' ', str)

    # extract normal words
    l.extend(re.split('\s+', str))

    l = filter(None, l)      #remove empty string
    return l
    #


def removeStopwords(l, stopwords):
    for sw in stopwords:
        l = [x for x in l if x != sw]

    return l

def stemWords(l):
    ps = PorterStemmer()
    return [ps.stem(x, 0, len(x) - 1) for x in l]

def preprocess(str, stopwords):
    str = removeSGML(str)
    l = tokenizeText(str)
    l = removeStopwords(l, stopwords)
    l = stemWords(l)
    word_count_dict = {}
    for word in l:
        word_count_dict[word] = word_count_dict.get(word, 0) + 1
    return word_count_dict




'''
#dict.items returns a list of dict's tuples. the 2nd item of a tuple is indexed as 1
# key is a function used to extract key for comparason, lambda is used to define a function
sortedList = sorted(dict.items(), key = lambda x: x[1], reverse = True)
count = 0
word_count = 0
while(count < 0.25 * total_num ):
    count = count + sortedList[word_count][1]
    word_count = word_count + 1
'''

