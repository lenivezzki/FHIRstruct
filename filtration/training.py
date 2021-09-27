import pandas as pd
import numpy as np
import collections
from more_itertools import unique_everseen
from collections import Counter

from itertools import chain
from sklearn.model_selection import train_test_split

import warnings
warnings.filterwarnings("ignore")

from sklearn.metrics import f1_score
from sklearn.metrics import average_precision_score
from sklearn.metrics import recall_score

from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

def scores(y_val, predicted):
    # print('Accuracy:', accuracy_score(y_val, predicted))
    print('F-score:', f1_score(y_val, predicted, average='micro'))
    print('Precision:', average_precision_score(y_val, predicted, average='micro'))
    print('Recall:', recall_score(y_val, predicted, average='macro'))


def recursive_flatten_generator(array):
    lst = []
    for i in array:
        if isinstance(i, list):
            lst.extend(recursive_flatten_generator(i))
        else:
            lst.append(i)
    return lst


def my_bag_of_words(text, words_to_index, dict_size):
    result_vector = np.zeros(dict_size)
    keys = [words_to_index[i] for i in text.split(" ") if i in words_to_index.keys()]
    result_vector[keys] = 1
    return result_vector


def top_words(classifier, tag, tags_classes, index_to_words, all_words, cl_type):
    print('Tag:\t{}'.format(tag))
    est = classifier.estimators_[tags_classes.index(tag)]
    if cl_type == 'lr':
        top_positive_words = [index_to_words[x] for x in
                              est.coef_.argsort().tolist()[0][:20]]  # top-30 words sorted by the coefficients.
        top_negative_words = [index_to_words[x] for x in
                              est.coef_.argsort().tolist()[0][-20:]]  # bottom-30 words  sorted by the coefficients.
    else:
        print('No such classifier')

    print('Top positive words:\t{}'.format(', '.join(top_positive_words[::-1])))
    print('Top negative words:\t{}\n'.format(', '.join(top_negative_words)))
    return top_positive_words[::-1], top_negative_words


def train_log_regression(X_train, y_train):
    model = LogisticRegression(C=3, penalty='l2', dual=False, solver='saga', max_iter=4000, multi_class='ovr')
    model = OneVsRestClassifier(model)
    model.fit(X_train, y_train)
    return model

def make_dict(X_train, y_train_cv):
    words_counts = Counter(chain.from_iterable([i.split(" ") for i in X_train]))
    print('Число уникальных слов',len(words_counts))
    DICT_SIZE = len(words_counts)
    WORDS_TO_INDEX = {j[0]:i for i,j in enumerate(sorted(words_counts.items(), key=lambda x: x[1], reverse=True)[:DICT_SIZE])}
    INDEX_TO_WORDS = {i:j[0] for i,j in enumerate(sorted(words_counts.items(), key=lambda x: x[1], reverse=True)[:DICT_SIZE])}
    return DICT_SIZE, WORDS_TO_INDEX, INDEX_TO_WORDS

