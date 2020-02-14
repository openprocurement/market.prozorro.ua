import json
from copy import deepcopy

from rest_framework.exceptions import ValidationError


CLASSIFICATION_REFERENCE_MAPPING = {
    'ДК021': 'classifiers_dk021_uk.json',
    'CPV_EN': 'classifiers_cpv_en.json',
    'CPV_RU': 'classifiers_cpv_ru.json',
    'ДК003': 'classifiers_dk003_uk.json',
    'ДК015': 'classifiers_dk015_uk.json',
    'ДК018': 'classifiers_dk018_uk.json',
    'КЕКВ': 'classifiers_kekv_uk.json',
    'NONE': 'classifiers_none_uk.json',
    'specialNorms': 'classifiers_special_norms_uk.json',
    'UA-ROAD': 'classifiers_ua_road.json',
    'GMDN': 'classifiers_gmdn.json',
}

STANDART_CLASSIFICATION_REFERENCE_SCHEMES = (
    'ДК003', 'ДК015', 'ДК018', 'ДК021', 'specialNorms', 'UA-ROAD',
    'GMDN', 'CPV_EN', 'CPV_RU', 'NONE'
)


class StandartsByReferenceValidator:
    def __init__(self, data):
        self.data = deepcopy(data)

    def _validate_classifiers_by_standarts_default(self, filename):
        with open(f'standarts/{filename}', 'r') as json_file:
            classification_codes = json.loads(json_file.read())
            try:
                classification_name = classification_codes[self.data['id']]
            except KeyError:
                raise ValidationError({'code': 'Wrong id'})
        self.data['description'] = classification_name

    def validate_unit(self,):
        try:
            unit_code = self.data['code']
        except KeyError:
            raise ValidationError({'code': 'Code is required'})
        with open('standarts/unit_codes_all.json', 'r') as json_file:
            unit_codes_all = json.loads(json_file.read())
            try:
                unit_code = unit_codes_all[self.data['code']]
            except KeyError:
                raise ValidationError({'code': 'Wrong code'})
        self.data['name'] = unit_code['name']
        return self.data

    def validate_classifiers(self):
        scheme = self.data['scheme']
        try:
            reference_filename = CLASSIFICATION_REFERENCE_MAPPING[scheme]
        except KeyError:
            raise ValidationError({'scheme': 'Unknown scheme'})

        if scheme in STANDART_CLASSIFICATION_REFERENCE_SCHEMES:
            self._validate_classifiers_by_standarts_default(reference_filename)

        return self.data
