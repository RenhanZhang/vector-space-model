from preprocess import preprocess
from os import listdir
import math
import os.path
import operator
import re
import sys
import numpy

def weight_compute(tf, idf, scheme, max_tf = 1):
    if scheme == 'd_tfidf' or scheme == 'q_tfidf':
        return tf * idf
    elif scheme == 'd_myown':
        return tf
    elif scheme == 'q_myown':
        return (0.5 + 0.5 * tf / max_tf) * idf
    else: raise NameError('Invalid weighting scheme: ')

def retriveDocuments(query, inverted_index, idf, doc_lengths, query_id):
    q_dict = preprocess(query, stopwords)
    scores = {}
    q_max_tf = max(q_dict.iteritems(), key = operator.itemgetter(1))[1]
    for word in q_dict.keys():
        if word not in inverted_index.keys():
            continue
        q_weight = weight_compute(q_dict.get(word, 0), idf.get(word, 0), q_scheme, q_max_tf)

        for filename in inverted_index[word].keys():
            doc_weight = weight_compute(inverted_index[word][filename], idf[word], d_scheme)
            scores[filename] = scores.get(filename, 0) + float(q_weight * doc_weight)/doc_lengths[filename]
    scores = sorted(scores.items(), key = operator.itemgetter(1), reverse = True)
    for i in range(0,len(scores)):
        print query_id + ' ' + scores[i][0] + " scores " + str(scores[i][1]) + ", ranked " + str(i)
    return scores

# update inverted_index with (word, count) in dict associated with a typical file
def add_freq(inverted_index, dict, filename):
    for word, count in dict.iteritems():
        word_dict = inverted_index.get(word, None)
        if word_dict == None:
            word_dict = {}
            inverted_index[word] = word_dict
        word_dict[filename] = word_dict.get(filename, 0) + count

def indexDocument(path):
    inverted_index = {}
    for filename in listdir(path):
        complete_filename = path + filename
        f = open(complete_filename, 'r')
        str = f.read()
        word_count_dict = preprocess(str, stopwords)
        add_freq(inverted_index, word_count_dict, filename)
        f.close()
    return inverted_index

def get_idf(inverted_index, path):
    num_total_docs = len([name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name))])
    idf = {}
    for word in inverted_index:
        num_docs = len(inverted_index[word])             # number of documents that contain the word
        idf[word] = math.log(num_total_docs, 10) - math.log(num_docs, 10)
    return idf

def extract_sol(reljudge_filename):
    test_file = open(reljudge_filename, 'r')
    solutions = test_file.readlines()
    rel_judge = {}
    for sol in solutions:
        query_id = re.search('^\d+\s', sol).group()
        sol = re.sub('^\d+\s+', '', sol)
        l = rel_judge.get(query_id, None)
        if l == None:
           l = []
           rel_judge[query_id] = l
        sol = str(int(sol)).zfill(4)
        l.append('cranfield' + sol)
    test_file.close()

    return rel_judge

def similarity(l1, l2):
    return len([x for x in l1 if x in l2])

def recall_prec_stat(ranks, rel_judge, rank_range):
    precisions = []
    recalls = []
    #compare my own answers in ranks to solutions provided in test_file
    for query_id in ranks.keys():
        own_rank = [x[0] for x in ranks[query_id]]
        sol_rank = rel_judge[query_id]
        precision = similarity(own_rank[:rank_range], sol_rank)/float(rank_range)
        precisions.append(precision)
        recall = similarity(own_rank[:rank_range], sol_rank)/float(len(sol_rank))
        recalls.append(recall)

    avg_precision = sum(precisions)/len(precisions)
    avg_recall = sum(recalls)/len(recalls)

    return [avg_precision, avg_recall]

def batch_querying(query_filename, inverted_index, idf, doc_lengths):
    query_f = open(query_filename, 'r')
    scores = {}
    for query in query_f.readlines():
        query_id = re.search('^\d+\s', query).group()
        query = re.sub('^\d+\s', '', query)
        score = retriveDocuments(query, inverted_index, idf, doc_lengths, query_id)
        scores[query_id] = score
    query_f.close()
    return scores

def doc_lens(inverted_index, idf):
    lengths = {}
    for word in inverted_index.keys():
        for filename in inverted_index[word].keys():
            weight = weight_compute(inverted_index[word][filename], idf[word], d_scheme, 'd')
            lengths[filename] = lengths.get(filename, 0) + math.pow(weight, 2)
    return lengths

def main():
    inverted_index = indexDocument(doc_path)
    idf = get_idf(inverted_index, doc_path)
    doc_lengths = doc_lens(inverted_index, idf)
    ranks = batch_querying(query_filename, inverted_index, idf, doc_lengths)

    rank_ranges = [10, 50, 100, 500]
    rel_judge = extract_sol(reljudge_filename)
    a = 'tfidf'
    if d_scheme != 'd_tfidf': a = 'txc'
    b = 'tfidf'
    if q_scheme != 'q_tfidf': b = 'nfx'
    print '\nWeighting scheme for document is ' + a + ' for query is ' + b + ' \n'
    for rank_range in rank_ranges:
        [p, r] = recall_prec_stat(ranks, rel_judge, rank_range)
        print 'For the top ' + str(rank_range) + ' documents, the precision is ' + str(p) + ' and the recall is ' + str(r) + '\n'
    

query_filename = 'cranfield.queries.test'
reljudge_filename = 'cranfield.reljudge.test'
d_scheme = 'd_tfidf'
q_scheme = 'q_tfidf'
doc_path = 'cranfieldDocs/'
if len(sys.argv) == 5:
    if sys.argv[1] != 'tfidf':
        d_scheme = 'd_myown'
    if sys.argv[2] != 'tfidf':
        q_scheme = 'q_myown'
    doc_path = sys.argv[3]
    query_filename = sys.argv[4]

with open('stopwords.txt', 'r') as f:
    stopwords = f.read().splitlines()
stopwords = [x.rstrip() for x in stopwords]     # remove trailing spaces

if __name__ == '__main__':
    main();
