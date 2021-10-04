from general_func import *
import pandas as pd
import numpy as np
from more_itertools import unique_everseen
import pymorphy2
from tqdm import tqdm_notebook as tq
from nltk import word_tokenize
import codecs
import re

from ipymarkup import show_span_ascii_markup as show_markup
from yargy import (Parser, or_, rule)
from yargy.pipelines import morph_pipeline
from yargy.predicates import (eq, in_, dictionary, type, gram)
from yargy.tokenizer import MorphTokenizer
from yargy import interpretation as interp
from yargy.interpretation import fact, attribute
from yargy.relations import gnc_relation

NOUN = gram('NOUN')
ADJF = gram('ADJF')
PRTF = gram('PRTF')
GENT = gram('gent')
ADVB = gram('ADVB')
TOKENIZER = MorphTokenizer()
gnc = gnc_relation()

from general_func import *
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.fhirreference import FHIRReference
from fhir.resources.annotation import Annotation

class FHIR_Mapper(object):

    def __init__(self):
        self.morph = pymorphy2.MorphAnalyzer()
        self.gnc = gnc_relation()
        R = pd.read_csv('../data/reactions.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        F = pd.read_csv('../data/food.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        E = pd.read_csv('../data/environment.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)
        M = pd.read_csv('../data/medication.txt', encoding='cp1251', sep='\t',
                        engine='python', header=0, error_bad_lines=False)

        def make_list_from_dict(df):
            list_ = list(df['Исходное наименование'])
            list_ = [item.lower() for item in list_]
            list_ = recursive_flatten_generator(list((unique_everseen(list_))))
            return list_

        react_list = make_list_from_dict(R)
        food_list = make_list_from_dict(F)
        env_list = make_list_from_dict(E)
        med_list = make_list_from_dict(M)

        def generate_allergen_rule(allergen_list):
            Allergen = fact('Allergen', ['term', 'modifier'])
            Adjs = fact('Adjs', [attribute('parts').repeatable()])
            ALL = morph_pipeline(allergen_list).interpretation(Allergen.term.normalized()).match(gnc)
            ADJ = or_(ADJF, PRTF, ADVB).interpretation(Allergen.modifier.inflected()).match(gnc).interpretation(Adjs.parts)
            ADJS = ADJ.repeatable(max=1).interpretation(Adjs)
            MODIFIER = rule(ADJS).interpretation(Allergen.modifier).match(gnc)
            ALLERGEN = or_(
                rule(ALL.interpretation(Allergen.term)),
                rule(ALL, MODIFIER),
                rule(MODIFIER, ALL)
                ).interpretation(Allergen)
            return ALLERGEN

        def generate_reaction_rule(react_list):
            Reaction = fact('Reaction', ['term', 'modifier'])
            Adjs = fact('Adjs', [attribute('parts').repeatable()])
            ADJ = or_(ADJF, PRTF, ADVB).interpretation(Reaction.modifier.inflected()).match(gnc).interpretation(
                Adjs.parts)
            ADJS = ADJ.repeatable(max=1).interpretation(Adjs)
            MODIFIER = rule(ADJS).interpretation(Reaction.modifier).match(gnc)
            REACT = morph_pipeline(react_list).interpretation(Reaction.term.normalized()).match(gnc)
            REACT_RULE = or_(
                rule(REACT),
                rule(REACT, MODIFIER),
                rule(MODIFIER, REACT)
            ).interpretation(Reaction)
            return REACT_RULE

        self.FOOD_RULE = generate_allergen_rule(food_list)
        self.ENV_RULE = generate_allergen_rule(env_list)
        self.MED_RULE = generate_allergen_rule(med_list)
        self.REACT_RULE = generate_reaction_rule(react_list)
        self.RULES = [(self.FOOD_RULE, 'food', F), (self.ENV_RULE, 'environment', E), (self.MED_RULE, 'medication', M), (self.REACT_RULE, 'reactions', R)]

    def give_facts(self, rule, string):
        parser = Parser(rule)
        matches = parser.findall(string)
        if matches:
            facts = [_.fact for _ in matches]
        return facts

    def get_right_word(self, word):
        right_words = []
        marker = []
        p = morph.parse(word)
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

    def match_gnc(self, term, parts, list_=None):
        need_gnc, term = self.get_right_word(term)
        modifier_pos = morph.parse(parts[0])[0].normalized.tag.POS
        new_parts = []
        if need_gnc and modifier_pos == 'ADJF':
            term_gender = term.tag.gender
            modifier_gender = morph.parse(parts[0])[0].normalized.tag.gender
            new_modifier = []
            if term_gender != modifier_gender and modifier_gender:
                for item in parts:
                    # print(item)
                    new_item = morph.parse(item)[0].inflect({term_gender}).word
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

    def match_term_instring(self, rule, string, list_exclude=[]):
        terms = []
        term = []
        facts = self.give_facts(rule, string)
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

    def match_term(self, rule, list_, list_exclude=None):
        allergens = []
        for item in tq(list_):
            # print(i)
            term = self.match_term_instring(rule, item, list_exclude)
            allergens.append(term)
        return allergens

    def get_snomed(self, rule, string, dict_df):
        facts = [item.term for item in self.give_facts(rule, string)]
        terms = self.match_term_instring(rule, string)
        if len(list(unique_everseen(facts))) == len(list(unique_everseen(terms))):
            rus_terms = list(unique_everseen(terms))
            rus_facts = list(unique_everseen(facts))
        else:
            rus_terms = terms
            rus_facts = facts
        ind = []
        for item in rus_facts:
            ind.append(dict_df[dict_df['Исходное наименование'] == item].index.tolist())
        ind = recursive_flatten_generator(ind)
        s_terms = [dict_df['Соответствие'][item] for item in ind]
        s_codes = [dict_df['Код'][item] for item in ind]
        return rus_terms, s_terms, s_codes

    def get_type(self, string):
        if re.findall(r'(?i)\b\w*аллерг\w*\b', string):
            type_ = 'allergy'
        elif re.findall(r'(?i)\b\w*перенос\w*\b', string):
            type_ = 'intolerance'
        else:
            type_ = 'allergy'
        return type_

    def get_category(self, rules, string):
        category = []
        for rule in rules:
            parser = Parser(rule[0])
            if list(parser.findall(string)):
                category.append(rule[1])
        return category

    def make_FHIR_AI(self, string):
        ai = AllergyIntolerance()

        reference = FHIRReference()
        reference.reference = 'Patient/example'
        ai.patient = reference

        ai.status = 'test'

        type_ = self.get_type(string)
        ai.type = type_
        category = self.get_category(self.RULES, string)
        category = [item for item in category if item != 'reactions']
        ai.category = category
        # Впилить категоризацию как отдельно импортируемую функцию
        # Передать в категорию список по результатам классификации

        react_snomed_rus, react_snomed, react_snomed_codes = self.get_snomed(self.REACT_RULE, string, self.RULES[3][2])
        food_snomed_rus, food_snomed, food_snomed_codes = self.get_snomed(self.FOOD_RULE, string, self.RULES[0][2])
        env_snomed_rus, env_snomed, env_snomed_codes = self.get_snomed(self.ENV_RULE, string, self.RULES[1][2])
        med_snomed_rus, med_snomed, med_snomed_codes = self.get_snomed(self.MED_RULE, string, self.RULES[2][2])
        rus = food_snomed_rus + env_snomed_rus + med_snomed_rus + react_snomed_rus

        ai.code = CodeableConcept()
        ai.code.coding = list()
        if react_snomed_rus:
            for i, item in enumerate(react_snomed_rus):
                code_coding = Coding()
                code_coding.system = 'http://snomed.info/sct'
                code_coding.code = react_snomed_codes[i]
                code_coding.display = react_snomed[i]
                ai.code.coding.append(code_coding)
        if food_snomed_rus:
            for i, item in enumerate(food_snomed_rus):
                code_coding = Coding()
                code_coding.system = 'http://snomed.info/sct'
                code_coding.code = food_snomed_codes[i]
                code_coding.display = food_snomed[i]
                ai.code.coding.append(code_coding)
        if env_snomed_rus:
            for i, item in enumerate(env_snomed_rus):
                code_coding = Coding()
                code_coding.system = 'http://snomed.info/sct'
                code_coding.code = env_snomed_codes[i]
                code_coding.display = env_snomed[i]
                ai.code.coding.append(code_coding)
            ai.code.text = ', '.join(env_snomed_rus)
        if med_snomed_rus:
            for i, item in enumerate(med_snomed_rus):
                code_coding = Coding()
                code_coding.system = 'http://snomed.info/sct'
                code_coding.code = med_snomed_codes[i]
                code_coding.display = med_snomed[i]
                ai.code.coding.append(code_coding)
            ai.code.text = ', '.join(med_snomed_rus)
        ai.code.text = ', '.join(rus)

        ai.note = list()
        annotation = Annotation()
        annotation.text = string
        ai.note.append(annotation)
        return ai.as_json()

