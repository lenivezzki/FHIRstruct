from config_func import *
from fhir.resources.patient import Patient
from fhir.resources.identifier import Identifier
from fhir.resources.coding import Coding
from fhir.resources.codeableconcept import CodeableConcept
from fhir.resources.fhirreference import FHIRReference
from fhir.resources.fhirdate import FHIRDate
from fhir.resources.quantity import Quantity
from fhir.resources.humanname import HumanName
from fhir.resources.contactpoint import ContactPoint
from fhir.resources.address import Address
from fhir.resources.observation import Observation
import numpy as np
import json

class FHIR_Mapper(object):

    def __init__(self, config_path):
        self.config_path = config_path
        weights = get_setting(config_path, 'Paths', 'weight_path')
        cardio = get_setting(config_path, 'Paths', 'cardio_db_path')
        cache = get_setting(config_path, 'Paths', 'cache_db_path')
        df = pd.read_csv(weights, encoding='cp1251', sep='\t', engine='python', header=0, error_bad_lines=False)
        df = df.drop('Unnamed: 0', axis=1)
        df = df.iloc[1:]
        df['Вес'] = df['Вес'].replace(',', '', regex=True)
        df['Вес'] = df['Вес'].replace(' ', '', regex=True)
        df[df['Вес'] == ""] = np.NaN
        df = df.dropna()
        df['DateTime'] = pd.Series(['20200627' for x in range(len(df.index))])
        df = df.reset_index(drop=True)
        df['Вес'] = df['Вес'].astype(float)
        self.weights_db = df.reset_index(drop=True)
        self.cardio_db = pd.read_csv(cardio, encoding='cp1251', sep='\t', engine='python', header=0, error_bad_lines=False)
        cache_db = pd.read_csv(cache, encoding='cp1251', sep='\t', engine='python', header=0, error_bad_lines=False)
        cache_db.drop(['Name_x', 'EpizodesForMerge', 'epizod_y', 'Name_y', 'Unnamed: 0'], axis='columns', inplace=True)
        self.cache_db = cache_db.reset_index(drop=True)

    def make_FHIR_patient_from_Cache(self, row_ind, print_=False):
        pat = Patient()
        # Идентификатор
        cdb = self.cache_db
        if cdb.epizod_x[row_ind] == cdb.epizod_x[row_ind]:
            identifier = Identifier()
            identifier.value = 'Patient/' + cdb.epizod_x[row_ind]
            pat.identifier = list()
            pat.identifier.append(identifier)

        # Имя
        if cdb.fio[row_ind] == cdb.fio[row_ind]:
            humanname = HumanName()
            s = cdb.fio[row_ind]
            humanname.text = s.replace('_', ' ')
            k = s.find('_')
            humanname.family = s[:k]
            p = s[k + 1:].find('_')
            humanname.given = list()
            humanname.given.append(s[k + 1:p + k + 1])
            humanname.given.append(s[p + k + 2:])
            pat.name = list()
            pat.name.append(humanname)

        # Дата Рождения
        if cdb.pI[row_ind] == cdb.pI[row_ind]:
            birthDate = FHIRDate(cdb.pI[row_ind])
            pat.birthDate = birthDate

        # Пол
        if cdb.pJ[row_ind] == cdb.pJ[row_ind]:
            if cdb.pJ[row_ind] == 'Женский':
                gender = 'female'
            else:
                gender = 'male'
            pat.gender = gender

        # Контакты
        telecom = list()
        if cdb.pT[row_ind] == cdb.pT[row_ind]:
            contact_t = ContactPoint()
            contact_t.system = 'phone'
            contact_t.value = cdb.pT[row_ind]
            telecom.append(contact_t)
        if cdb.email[row_ind] == cdb.email[row_ind]:
            contact_e = ContactPoint()
            contact_e.system = 'email'
            contact_e.value = cdb.email[row_ind]
            telecom.append(contact_e)
        if telecom!=[]:
            pat.telecom = telecom

        # Адрес
        address = list()
        addr = Address()
        if cdb.pC[row_ind] == cdb.pC[row_ind]:
            addr.district = cdb.pC[row_ind]
        if cdb.pO[row_ind] == cdb.pO[row_ind]:
            addr.city = cdb.pO[row_ind]
        addr.line = list()
        if cdb.pP[row_ind] == cdb.pP[row_ind]:
            addr.line.append('Улица: ' + cdb.pP[row_ind])
            addr.line.append('Номер дома: хх')
        if cdb.pS[row_ind] == cdb.pS[row_ind]:
            addr.line.append('Квартира: ' + cdb.pS[row_ind])
        if cdb.pM[row_ind] == cdb.pM[row_ind]:
            addr.postalCode = cdb.pM[row_ind]
        address.append(addr)
        if addr.as_json() != {}:
            pat.address = address
        result = pat.as_json()
        if print_ == True:
            filename = '\\Patient_Cache_example'
            path_fin = get_setting(self.config_path, 'Paths', 'path_fin')
            path = path_fin + filename + '.json'
            with open(path, "w") as tf: json.dump(result, tf, ensure_ascii=False)
        return result

    def make_FHIR_patient_from_Cardio(self, row_ind, print_=False):
        pat = Patient()
        cdb = self.cardio_db
        # Идентификатор
        if cdb.PATIENT[row_ind] == cdb.PATIENT[row_ind]:
            identifier = Identifier()
            identifier.value = 'Patient/' + str(cdb.PATIENT[row_ind])
            snils = Identifier()
            snils.system = 'СНИЛС'
            snils.value = cdb.SNILS[row_ind]
            pat.identifier = list()
            pat.identifier.append(identifier)
            pat.identifier.append(snils)

        # Имя
        humanname = HumanName()
        if cdb.LAST_NAME[row_ind] == cdb.LAST_NAME[row_ind]:
            humanname.family = cdb.LAST_NAME[row_ind]
        humanname.given = list()
        if cdb.FIRST_NAME[row_ind] == cdb.FIRST_NAME[row_ind]:
            humanname.given.append(cdb.FIRST_NAME[row_ind])
        if cdb.PATRONYMIC[row_ind] == cdb.PATRONYMIC[row_ind]:
            humanname.given.append(cdb.PATRONYMIC[row_ind])
        full_name = list()
        full_name.extend(humanname.given)
        full_name.append(humanname.family)
        humanname.text = ' '.join(full_name)
        if humanname!={}:
            pat.name = list()
            pat.name.append(humanname)

        # Дата Рождения
        if cdb.BIRTHDAY[row_ind] == cdb.BIRTHDAY[row_ind]:
            birthDate = FHIRDate(cdb.BIRTHDAY[row_ind])
            pat.birthDate = birthDate

        # Пол
        if cdb.GENDER[row_ind] == cdb.GENDER[row_ind]:
            if int(cdb.GENDER[row_ind]) == 0:
                gender = 'female'
            else:
                gender = 'male'
            pat.gender = gender
        result = pat.as_json()
        if print_ == True:
            filename = '\\Patient_cardio_example'
            path_fin = get_setting(self.config_path, 'Paths', 'path_fin')
            path = path_fin + filename + '.json'
            with open(path, "w") as tf: json.dump(result, tf, ensure_ascii=False)
        return result

    def make_FHIR_weights(self, row_ind, print_=False):
        obs = Observation()
        obs.status = 'неизвестно'
        obs.code = CodeableConcept()
        obs.code.coding = list()
        code_coding = Coding()
        code_coding.system = 'http://snomed.info/sct'
        code_coding.code = '27113001'
        code_coding.display = 'Body weight'
        obs.code.coding.append(code_coding)
        obs.code.text = 'Вес'

        wdb = self.weights_db
        iter_obj = wdb[row_ind:row_ind + 1].values.tolist()[0]

        if iter_obj[0]==iter_obj[0]:
            identifier = Identifier()
            identifier.value = iter_obj[0]
            obs.identifier = list()
            obs.identifier.append(identifier)

        if iter_obj[1]==iter_obj[1]:
            reference = FHIRReference()
            reference.reference = 'Patient/' + iter_obj[1]
            obs.subject = reference

        if iter_obj[3]==iter_obj[3]:
            effectiveDateTime = FHIRDate(iter_obj[3])
            obs.effectiveDateTime = effectiveDateTime

        obs.bodySite = CodeableConcept()
        obs.bodySite.coding = list()
        bS_coding = Coding()
        bS_coding.system = 'http://snomed.info/sct'
        bS_coding.code = '261188006'
        bS_coding.display = 'Whole body'
        obs.bodySite.coding.append(bS_coding)

        valueQuantity = Quantity()
        if iter_obj[2]==iter_obj[2]:
            valueQuantity.value = iter_obj[2]
        valueQuantity.unit = 'kg'
        valueQuantity.system = 'http://snomed.info/sct'
        valueQuantity.code = '258683005'
        obs.valueQuantity = valueQuantity
        result = obs.as_json()
        if print_== True:
            filename = '\\Weight_example'
            path_fin = get_setting(self.config_path, 'Paths', 'path_fin')
            path = path_fin + filename + '.json'
            with open(path, "w") as tf: json.dump(result, tf, ensure_ascii=False)

        return result