from general_func import *
import pandas as pd
import numpy as np
from more_itertools import unique_everseen
import pymorphy2
from tqdm import tqdm_notebook as tq
from nltk import word_tokenize, sent_tokenize
import codecs
import re
from IPython.display import display
from ipymarkup import show_span_ascii_markup as show_markup
from yargy import (Parser, or_, rule)
from yargy.pipelines import morph_pipeline
from yargy.predicates import (eq, in_, dictionary, type, gram)
from yargy.tokenizer import MorphTokenizer
from yargy import interpretation as interp
from yargy.interpretation import fact, attribute
from yargy.relations import gnc_relation


class Extractor(object):

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.gnc = gnc_relation()
        R = pd.read_csv('../data/reactions.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        React_list = list(R['ID'])
        React_list = recursive_flatten_generator(list((unique_everseen(React_list))))

        E = pd.read_csv('../data/environment.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        env_list = list(E['ID'])
        env_list = [item.lower() for item in env_list]
        env_list = recursive_flatten_generator(list((unique_everseen(env_list))))

        F = pd.read_csv('../data/food.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        food_list = list(F['ID'])
        food_list = [item.lower() for item in food_list]
        food_list = recursive_flatten_generator(list((unique_everseen(food_list))))

        M = pd.read_csv('../data/medication.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        med_list = list(M['ID'])
        med_list = [item.lower() for item in med_list]
        med_list = recursive_flatten_generator(list((unique_everseen(med_list))))

        def generate_allergen_rule(allergen_list):
            ADJF = gram('ADJF')
            PRTF = gram('PRTF')
            ADVB = gram('ADVB')
            Allergen = fact('Allergen', ['term', 'modifier'])
            Adjs = fact('Adjs', [attribute('parts').repeatable()])
            ALL = morph_pipeline(allergen_list).interpretation(Allergen.term.normalized()).match(self.gnc)
            ADJ = or_(ADJF, PRTF, ADVB).interpretation(Allergen.modifier.inflected()).match(self.gnc).interpretation(
                Adjs.parts)
            ADJS = ADJ.repeatable(max=1).interpretation(Adjs)
            MODIFIER = rule(ADJS).interpretation(Allergen.modifier).match(self.gnc)
            ALLERGEN = or_(
                rule(ALL.interpretation(Allergen.term)),
                rule(ALL, MODIFIER),
                rule(MODIFIER, ALL)
            ).interpretation(Allergen)
            return ALLERGEN

        FOOD_RULE = generate_allergen_rule(food_list)
        ENV_RULE = generate_allergen_rule(env_list)
        MED_RULE = generate_allergen_rule(med_list)
        self.parser_med = Parser(MED_RULE)
        self.parser_food = Parser(FOOD_RULE)
        self.parser_env = Parser(ENV_RULE)

        ADJF = gram('ADJF')
        PRTF = gram('PRTF')
        ADVB = gram('ADVB')
        ADJS = gram('ADJS')
        Reaction = fact('Reaction', ['term', 'modifier'])
        Adjs = fact('Adjs', [attribute('parts').repeatable()])
        ADJ = or_(ADJF, PRTF, ADVB, ADJS).interpretation(Reaction.modifier.inflected()).match(self.gnc).interpretation(Adjs.parts)
        adjs = ADJ.repeatable(max=1).interpretation(Adjs)
        MODIFIER = rule(adjs).interpretation(Reaction.modifier).match(self.gnc)
        REACT = morph_pipeline(React_list).interpretation(Reaction.term.normalized()).match(self.gnc)
        REACT_RULE = or_(
            rule(REACT),
            rule(REACT, MODIFIER),
            rule(MODIFIER, REACT)).interpretation(Reaction)
        self.parser_react = Parser(REACT_RULE)

        cont = ['замена', 'смена', 'купирует', 'мг', 'трансаминаз', 'потребность', 'купируется', 'добавлен',
                'продолжен', 'без эффекта', 'положительный эффект', 'заменен', 'принимать', 'регулярный прием']
        Context = fact('Context', ['term'])
        CONT = morph_pipeline(cont).interpretation(Context.term.normalized()).match(self.gnc)
        CONT_RULE = or_(rule(CONT)).interpretation(Context)
        self.parser_cont = Parser(CONT_RULE)

        allerg = ['аллергия', 'аллергический', 'непереносимость', 'реакция', 'сенсибилизация',
                  'с положительным эффектом, но', 'не принимать', 'плохая переносимость']
        Allergic = fact('Allergic', ['term'])
        ALL = morph_pipeline(allerg).interpretation(Allergic.term.normalized()).match(self.gnc)
        ALL_RULE = or_(rule(ALL)).interpretation(Allergic)
        self.parser_all = Parser(ALL_RULE)



    def generate_allergen_rule(self, allergen_list):
        ADJF = gram('ADJF')
        PRTF = gram('PRTF')
        ADVB = gram('ADVB')
        Allergen = fact('Allergen', ['term', 'modifier'])
        Adjs = fact('Adjs', [attribute('parts').repeatable()])
        ALL = morph_pipeline(allergen_list).interpretation(Allergen.term.normalized()).match(self.gnc)
        ADJ = or_(ADJF, PRTF, ADVB).interpretation(Allergen.modifier.inflected()).match(self.gnc).interpretation(
            Adjs.parts)
        ADJS = ADJ.repeatable(max=1).interpretation(Adjs)
        MODIFIER = rule(ADJS).interpretation(Allergen.modifier).match(self.gnc)
        ALLERGEN = or_(
            rule(ALL.interpretation(Allergen.term)),
            rule(ALL, MODIFIER),
            rule(MODIFIER, ALL)
        ).interpretation(Allergen)
        return ALLERGEN

    def give_facts(self, rule, string):
        parser = Parser(rule)
        matches = parser.findall(string)
        if matches:
            facts = [_.fact for _ in matches]
        return facts

    def get_right_word(self, word):
        right_words = []
        marker = []
        p = self.morph.parse(word)
        for item in p:
            if {'NOUN', 'nomn'} in item.tag:
                marker.append(1)
                right_words.append(item)
            else:
                marker.append(0)
        s = sum(marker)
        if s == 0:
            right_word = p[0]
        elif s > 0:
            right_word = right_words[0]
        return s, right_word

    def match_gnc(self, term, parts, list_):
        need_gnc, term = self.get_right_word(term)
        modifier_pos = self.morph.parse(parts[0])[0].normalized.tag.POS
        new_parts = []
        if need_gnc and modifier_pos == 'ADJF':
            term_gender = term.tag.gender
            modifier_gender = self.morph.parse(parts[0])[0].normalized.tag.gender
            new_modifier = []
            if term_gender != modifier_gender and modifier_gender:
                for item in parts:
                    new_item = self.morph.parse(item)[0].inflect({term_gender}).word
                    if not new_item in list_:
                        new_modifier.append(new_item)
                    new_modifier.append(term.word)
                    new_modifier = ' '.join(new_modifier)
            else:

                for item in parts:
                    if not item in list_:
                        new_parts.append(item)
                new_parts.append(term.word)
                new_modifier = ' '.join(new_parts)
        else:
            new_parts.append(term.word)
            new_modifier = ' '.join(new_parts)
        return new_modifier

    def match_fact_instring(self, parser, string, list_exclude):
        terms = []
        term = []
        matches = parser.findall(string)
        facts = [_.fact for _ in matches]
        for fact in facts:
            if fact.term:
                term = fact.term
            if fact.modifier:
                parts = fact.modifier.parts
            else:
                parts = []
            if parts != []:
                new_fact = self.match_gnc(term, parts, list_exclude)
            else:
                new_fact = term
            terms.append(new_fact)
        return terms

    def min_len(self, a, l, p):
        """
        Принимает на вход число и два списка (индекс термина и индексы контекстных ключей).
        Определяет, к какому ключу искомый термин ближе.
        """
        dl = [abs(item - a) for item in l]
        min_dl = min(dl)
        dp = [abs(item - a) for item in p]
        min_dp = min(dp)
        min_d = min_dl - min_dp
        return min_d

    def find_centre(self, parser, string):
        centres = []
        for item in parser.findall(string):
            centres.append((item.span.start + item.span.stop) / 2)
        return centres

    def match_value_instring(self, parser, string):
        matches = parser.findall(string)
        values = []
        for match in matches:
            values.append(' '.join([_.value for _ in match.tokens]))
        return values

    def extract(self, s):
        # Проверяем, есть ли контекстные ключи в строке
        cont_terms = self.match_value_instring(self.parser_cont, s)
        if cont_terms:
            indicator = 1
        else:
            indicator = 0

        # Ищем, какой ключ ближе к медикаменту
        if indicator == 1:
            # Ищем слова аллергического контекста
            index_med = self.find_centre(self.parser_med, s)
            index_cont = self.find_centre(self.parser_cont, s)
            index_all = self.find_centre(self.parser_all, s)

            how_to_parse = []
            for ind in index_med:
                if index_all:
                    d = self.min_len(ind, index_all, index_cont)
                    if d >= 0:
                        how_to_parse.append(0)
                    else:
                        how_to_parse.append(1)
                else:
                    how_to_parse.append(0)

            terms = self.match_fact_instring(self.parser_med, s, [])
            if not len(terms) == len(how_to_parse):
                raise Exception('Number of terms mismatch')
            final_med_terms = []
            for ind, item in enumerate(how_to_parse):
                if item == 1:
                    final_med_terms.append(terms[ind])
        else:
            final_med_terms = self.match_fact_instring(self.parser_med, s, [])

        final_food_terms = self.match_fact_instring(self.parser_food, s, [])
        final_env_terms = self.match_fact_instring(self.parser_env, s, [])
        final_react_terms = self.match_fact_instring(self.parser_react, s, [])
        final_react_terms = list(unique_everseen(final_react_terms))

        allergens = final_food_terms + final_env_terms + final_med_terms
        allergens = list(unique_everseen(allergens))
        return allergens, final_react_terms
