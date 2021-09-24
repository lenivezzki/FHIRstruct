from general_func import *
import symspellpy
from nltk.corpus import stopwords
from nltk import word_tokenize
import re
from more_itertools import unique_everseen
from symspellpy import Verbosity


class ErrorCorrector(object):

    def __init__(self):
        sym_spell = symspellpy.SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        sym_spell.load_dictionary('../data/dict_with_freq.txt', term_index=0, count_index=1, separator='\t', encoding='cp1251')
        vocabulary_result = sym_spell.words
        self.sym_spell = sym_spell
        self.dict_ = vocabulary_result.keys()
        #cuts = read_list('cuts.txt','utf-8')
        stop = stopwords.words('russian')
        letters = [word for word in stop if len(word) < 4 and len(word) > 2]
        #letters.append(cuts)
        letters = list(unique_everseen(recursive_flatten_generator(letters)))
        minus_words = ['я', 'вма', 'л', 'и', 'а', 'е', 'вот', 'ли', 'ней', 'ой', 'уж', 'но', 'ли', 'про', 'ее', 'три','он', ]
        letters = [w for w in letters if not w in minus_words]
        self.letters = letters


    def clean(self, string):
        regex1 = r'\d[а-я]'  # 80мг->80 мг
        regex2 = r'\d[А-Я]'  # 2014ДИ->2014 ДИ
        regex4 = r'(?i)[а-я][0-9]'  # эктомияв2014->эктомияв 2014
        regex7 = r'[а-я][А-Я]{2,5}[а-я]'  # железодефицитнаяАХЗпост -> железодефицитная АХЗ пост
        regex8 = r'[A-Z][а-я]'  # IDаллергия -> ID аллергия
        regex9 = r'[A-Z][А-Я]'  # IDАллергия -> ID Аллергия
        regex10 = r'[а-я][А-Я]{2,5}'  # аллергияХУГГЕ -> аллергия ХУГГЕ

        clean_text = string.replace('..', '.')
        clean_text = clean_text.replace(',,', ',')
        clean_text = put_spaces(regex1, clean_text)
        clean_text = put_spaces(regex2, clean_text)
        clean_text = put_spaces(regex4, clean_text)
        clean_text = put_spaces(regex8, clean_text)
        clean_text = put_spaces(regex9, clean_text)
        clean_text = put_spaces(regex10, clean_text)
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = put_spaces_abb(regex7, clean_text)
        return clean_text

    def put_case(self, string):
        words = word_tokenize(string)
        ind_words = []
        for word in words:
            if word[:1].isupper():
                ind_word = [word, 1]
            else:
                ind_word = [word, 0]
            ind_words.append(ind_word)
        return ind_words

    def simple_checker(self, string, list_):
        if string.lower() in list_:
            return True
        else:
            return False

    def segment_with_case(self, string):
        ind_words = self.put_case(string)
        for ind, word in enumerate(ind_words):
            if not word[0].lower() in self.dict_:
                r = self.sym_spell.word_segmentation(word[0], ignore_token=r'\d+', max_edit_distance=2)
                r = str(r.corrected_string)
                if r.replace(' ', '').lower() == word[0].replace(' ', '').lower():
                    ind_words[ind][0] = r
        for ind, item in enumerate(ind_words):
            if item[1] == 1 and item[0][:1].islower():
                ind_words[ind][0] = item[0].capitalize()
        new_words = [item[0] for item in ind_words]
        new_words = ' '.join(new_words)
        return new_words

    def is_in_dict(self, string):
        words = word_tokenize(string)
        is_all_in_dict = []
        for item in words:
            if item.lower() in self.dict_:
                is_all_in_dict.append((item, 1))
            else:
                is_all_in_dict.append((item, 0))
        return is_all_in_dict

    def correct_with_case(self, string):
        ind_words = self.put_case(string)
        for ind, word in enumerate(ind_words):
            if not self.simple_checker(word[0], self.dict_) and not self.simple_checker(word[0], self.letters):
                if not word[0].isdigit():
                    new_word = str(self.sym_spell.lookup(word[0], Verbosity.CLOSEST, max_edit_distance=2,
                                                    transfer_casing=False, ignore_token='\W', include_unknown=True)[
                                       0]).split(' ')[0]
                    new_word = new_word[:-1]
                    ind_words[ind][0] = new_word
        for ind, item in enumerate(ind_words):
            if item[1] == 1 and item[0][:1].islower():
                ind_words[ind][0] = item[0].capitalize()
        new_words = [item[0] for item in ind_words]
        new_words = ' '.join(new_words)
        return new_words

    def secondary_segment_with_case(self, string):
        ind_words = self.put_case(string)
        for ind, word in enumerate(ind_words):
            if not word[0].lower() in self.dict_:
                r = self.sym_spell.word_segmentation(word[0], ignore_token=r'\d+', max_edit_distance=0)
                r = str(r.corrected_string)
                ind_words[ind][0] = r
        for ind, item in enumerate(ind_words):
            if item[1] == 1 and item[0][:1].islower():
                ind_words[ind][0] = item[0].capitalize()
        new_words = [item[0] for item in ind_words]
        new_words = ' '.join(new_words)
        return new_words

    def correct(self, string):
        string = self.clean(string)
        segment = self.segment_with_case(string)
        is_all_in_dict = self.is_in_dict(segment)
        correct = [self.correct_with_case(item[0]) if item[1] == 0 else item[0] for item in
                   is_all_in_dict]
        correct = ' '.join(correct)
        correct = self.is_in_dict(correct)
        correct = [self.secondary_segment_with_case(item[0]) if item[1] == 0 else item[0] for item
                   in correct]
        correct = [item.replace('. .', '.') for item in correct]
        correct = [item.replace(', ,', ',') for item in correct]
        return ' '.join(correct)









