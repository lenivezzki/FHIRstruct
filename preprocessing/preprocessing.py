import re
import pymorphy2
morph = pymorphy2.MorphAnalyzer()
from nltk.corpus import stopwords
import nltk
nltk.download('stopwords')
from nltk import sent_tokenize

regex1 = r'\d[а-я]'#80мг->80 мг
regex2 = r'\d[А-Я]'#2014ДИ->2014 ДИ
regex3 = r'[а-я][А-Я][а-я]'#ОсложненияИнвазивный->Осложнения Инвазивный
regex4 = r'[а-я]\d' #эктомияв2014->эктомияв 2014
regex5 = r'\d\.\ \d' #15. 10. 2014->15.10.2014
regex6 = r'[а-я]+\ +[А-Я][а-я]+' #Флюорограмма безпатологии Гепатит отрицает -> Флюорограмма безпатологии. Гепатит отрицает
regex7 = r'[а-я][А-Я]{2,5}[а-я]' #железодефицитнаяАХЗпост -> железодефицитная АХЗ пост
regex8 = r'[A-Z][а-я]' #IDаллергия -> ID аллергия
regex9 = r'[A-Z][А-Я]' #IDАллергия -> ID Аллергия
regex10 = r'[а-я][А-Я]{2,5}' #аллергияХУГГЕ -> аллергия ХУГГЕ


regex_all = r'(?i)\b\w*аллерг\w*\b'
regex_per = r'(?i)\b\w*перенос\w*\b'
regex_otm = r'(?i)\b\w*отмен\w*\b'

rus_reg = r'(?i)[а-я]'


def put_spaces(regex, string):
    l = re.findall(regex, string)
    aim = [i[0]+' '+i[1:] for i in l]
    for i, w in enumerate(l):
        string = string.replace(l[i], aim[i])
    return string

def correct_dates(regex, string):
    l = re.findall(regex, string)
    a = [item.split(' ') for item in l]
    aim = [''.join(item) for item in a]
    for i, w in enumerate(l):
        string = string.replace(l[i], aim[i])    
    return string

def dots_for_sent(regex, string):
    l = re.findall(regex,string)
    a = [item.split(' ') for item in l]
    aim = ['.'.join(item) for item in a]
    for i, w in enumerate(l):
        string = string.replace(l[i], aim[i])    
    return string

def put_spaces_abb(regex, string):
    l = re.findall(regex, string)
    aim =[]
    for i, w in enumerate(l):
        n = len(w)
        aim += [l[i][0]+' '+l[i][1:n-1]+' '+l[i][n-1]]
        string = string.replace(l[i], aim[i])
    return string

def normalize_corp(corp_list):
    norm_corp = []
    for item in corp_list:
        words = re.split('\W+', item)
        norm_word = [morph.parse(word)[0].normal_form for word in words]
        norm_corp.append(norm_word)
    norm_corp = [" ".join(item) for item in norm_corp]
    return norm_corp


def remove_russian_stopwords_from_corp_but_list(not_stop_list, corp):
    stop_list = stopwords.words("russian")
    stopwords_list = list(set(stop_list) - set(not_stop_list))
    clean_corp = ' '.join(word for word in corp.split() if word not in stopwords_list)
    return clean_corp

def remove_words_from_string(words_list, corp):
    clean_string = ' '.join(word for word in corp.split() if word not in words_list)
    return clean_string


def find_indexes_of_regex_in_string(regex, string):
    index = []
    reg = re.findall(regex, string)
    a = [[ind for ind, word in enumerate(re.split('\W+', string)) if word == reg[num]] for num in range(len(reg))]
    c = [item for sublist in a for item in sublist]
    c = list(set(c))
    index.append(sorted(c))
    return index[0]


def regex_list_from_string(regex, string):
    reg = re.findall(regex, string)
    regex_list = list(set(reg))
    return regex_list


def return_sentences_with_regex(regex_list, corp):
    sentences = []
    for sentence in sent_tokenize(corp):
        if (any(map(lambda word: word in sentence, regex_list))):
            sentences.append(sentence)
    return sentences


def return_n_sentences_before_and_after_regex(regex_list, corp, n):
    fin_list = []
    sentences = sent_tokenize(corp)
    if n != 0:
        finish = len(sentences)
        for i,sentence in enumerate(sentences):
            if (any(map(lambda word: word in sentence, regex_list))):
                if (i-n >= 0) and (i+n < finish):
                    result = [sentences[p] for p in range(i-n, i+n+1)]
                elif (i-n <= 0) and (i+n < finish):
                    result = [sentences[p] for p in range(0, i+n+1)]
                elif (i-n >= 0) and (i+n >= finish):
                    result = [sentences[p] for p in range(i-n, finish)]
                else:
                    result = return_sentences_with_regex(regex_list, corp)
                fin_list.append(result)
        fin_list = [" ".join(item) for item in fin_list]
    else:
        fin_list = return_sentences_with_regex(regex_list, corp)
    return fin_list


def return_n_words_before_and_after_regex(regex, corp, n):
    fin_list = []
    words = re.split('\W+', corp)
    indexes = find_indexes_of_regex_in_string(regex, corp)
    finish = len(words)
    for ind, word in enumerate(words):
        for i in indexes:
            if ind == i in indexes:
                if (ind-n >= 0) and (ind+n < finish):
                    result = [words[p] for p in range(ind-n, ind+n+1)]
                elif (ind-n <= 0) and (ind+n < finish):
                    result = [words[p] for p in range(0, ind+n+1)]
                elif (ind-n >= 0) and (ind+n >= finish):
                    result = [words[p] for p in range(ind-n, finish)]
                else:
                    result = [words[p] for p in range(0, finish)]
                fin_list.append(result)
    fin_list = [" ".join(item) for item in fin_list]
    return fin_list

def prepare_sentences(corp, n, regex1, regex2, non_stop_list):
    corp_list = [re.sub(r'\d+', ' ', item) for item in corp]
    regex_list_1 = [regex_list_from_string(regex1, item) for item in corp_list]
    regex_list_2 = [regex_list_from_string(regex2, item) for item in corp_list]
    regex_list = [regex_list_1[i]+regex_list_2[i] for i in range(len(regex_list_1))]
    sentence = [return_n_sentences_before_and_after_regex(regex_list[i], corp, n) for i, corp in enumerate(corp_list)]
    sentence = [" ".join(item) for item in sentence]
    sentence = normalize_corp(sentence)
    sentence = [remove_russian_stopwords_from_corp_but_list(non_stop_list, item) for ind, item in enumerate(sentence)]
    return sentence

def prepare_words(clean_norm_list, n, regex1, regex2):
    clean_norm_corp_list = [re.sub(r'\d+', ' ', item) for item in clean_norm_list]
    words_1 = [list(set(return_n_words_before_and_after_regex(regex1, corp, n))) for i, corp in enumerate(clean_norm_corp_list)]
    words_2 = [list(set(return_n_words_before_and_after_regex(regex2, corp, n))) for i, corp in enumerate(clean_norm_corp_list)]
    words = [words_1[i]+words_2[i] for i in range(len(words_1))]
    words = [" ".join(item) for item in words]
    return words

def count_word_frequency_in_string(dict_size,string, words_to_index):
    result_vector = np.zeros(dict_size)
    keys = [words_to_index[i] for i in string.split(" ") if i in WORDS_TO_INDEX.keys()]
    value_count = Counter(keys)
    for i,j in sorted(value_count.items()):
        result_vector[i] = j
    return result_vector

def cut_rus_string(regex, string):
    first_rus_symbol = re.search(regex, string)
    k = first_rus_symbol.span(0)[0]
    if k==k:
        cut_string = string[k:]
    else:
        cut_string = string
    return cut_string