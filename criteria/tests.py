from rest_framework import status
from rest_framework.test import APITestCase

from criteria.models import Criteria

API_URL = '/api/0/criteria/'


def api_criteria_data_to_model(data):
    fields_mapping = {
        'nameEng': 'name_eng',
        'minValue': 'min_value',
        'maxValue': 'max_value',
        'dataType': 'data_type',
        'dateModified': 'date_modified',
        'additionalClassification': 'additional_classification',
    }
    result = {}
    for key, value in data.items():
        result[fields_mapping.get(key, key)] = data[key]
    return result


class CriteriaAPITestCase(APITestCase):
    def setUp(self):
        Criteria.objects.all().delete()  # ensure no Criteria in db
        self.valid_criteria_data_1 = {
            "classification": {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "dataType": "number",
            "unit": {
                "name": "millilitre of water",
                "code": "WW"
            }
        }
        self.valid_criteria_data_2 = {
            "classification": {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "dataType": "boolean",
            "unit": {
                "name": "millilitre of water",
                "code": "WW"
            }
        }
        self.valid_criteria_data_3 = {
            "classification": {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "dataType": "number",
            "unit": {
                "name": "millilitre of water",
                "code": "WW"
            }
        }
        self.valid_full_criteria_data = {
            "name": "Name",
            "nameEng": "Name eng",
            "classification": {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "additionalClassification": {
                "id": "00000000-5",
                "scheme": "scheme",
                "description": "description"
            },
            "minValue": "11",
            "maxValue": "22",
            "dataType": "number",
            "unit": {
                "name": "millilitre of water",
                "code": "WW"
            }
        }
        self.valid_criteria_data = (
            self.valid_criteria_data_1,
            self.valid_criteria_data_2,
            self.valid_criteria_data_3,
            self.valid_full_criteria_data
        )

    def _post_json(self, path, data=None):
        return self.client.post(path=path, data=data or {}, format='json')

    def tearDown(self):
        Criteria.objects.all().delete()  # ensure no Criteria in db


class TestCriteriaCreating(CriteriaAPITestCase):
    def test_criteria_creating_errors(self):
        self.assertEqual(Criteria.objects.count(), 0)
        self.assertEqual(
            self._post_json(path=API_URL).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Criteria.objects.count(), 0)

    def test_criteria_basic_validation(self):
        # TODO: add logic
        pass

    def test_criteria_classifiers_reference_validation(self):
        # TODO: add logic
        pass

    def test_criteria_successful_creating(self):
        self.assertEqual(Criteria.objects.count(), 0)
        self.assertEqual(
            self._post_json(path=API_URL).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data = self.valid_full_criteria_data
        post_response = self._post_json(path=API_URL, data=criteria_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Criteria.objects.count(), 1)

        criteria_obj = Criteria.objects.get()

        self.assertEqual(criteria_obj.name, criteria_data['name'])
        self.assertEqual(criteria_obj.name_eng, criteria_data['nameEng'])
        self.assertEqual(
            criteria_obj.data_type, criteria_data['dataType']
        )
        self.assertEqual(float(criteria_obj.min_value), float(criteria_data['minValue']))
        self.assertEqual(float(criteria_obj.max_value), float(criteria_data['maxValue']))
        self.assertDictEqual(
            criteria_obj.classification, criteria_data['classification']
        )
        self.assertDictEqual(
            criteria_obj.unit, criteria_data['unit']
        )
        self.assertDictEqual(
            criteria_obj.additional_classification,
            criteria_data['additionalClassification']
        )
        self.assertIsNotNone(criteria_obj.date_modified)
        self.assertFalse(criteria_obj.archive)
        self.assertIsNotNone(criteria_obj.id)

    def test_successful_criteria_creation_output(self):
        criteria_data = self.valid_full_criteria_data
        post_response = self._post_json(path=API_URL, data=criteria_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        post_response_json = post_response.json()
        self.assertEqual(post_response_json['name'], criteria_data['name'])
        self.assertEqual(post_response_json['nameEng'], criteria_data['nameEng'])
        self.assertEqual(
            post_response_json['dataType'], criteria_data['dataType']
        )
        self.assertEqual(float(post_response_json['minValue']), float(criteria_data['minValue']))
        self.assertEqual(float(post_response_json['maxValue']), float(criteria_data['maxValue']))
        self.assertDictEqual(
            post_response_json['classification'], criteria_data['classification']
        )
        self.assertDictEqual(
            post_response_json['unit'], criteria_data['unit']
        )
        self.assertDictEqual(
            post_response_json['additionalClassification'],
            criteria_data['additionalClassification']
        )
        self.assertIsNotNone(post_response_json['dateModified'])
        self.assertFalse(post_response_json['archive'])
        self.assertIsNotNone(post_response_json['id'])


class TestCriteriaListing(CriteriaAPITestCase):
    def test_criteria_listing(self):
        self.assertEqual(Criteria.objects.count(), 0)

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(get_response.json(), [])
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))
        self.assertEqual(Criteria.objects.count(), len(self.valid_criteria_data))

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(len(get_response.json()), len(self.valid_criteria_data))

    def test_criteria_listing_filtering(self):
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))
        data_for_filtering = {
            "name": "Custom name",
            "classification": {
                "id": "03111000-2",
                "scheme": "ДК021",
                "description": "Насіння"
            },
            "additional_classification": {
                "id": "42412200-9",
                "scheme": "ДК021",
                "description": "Кабестани"
            },
            "dataType": "number",
            "unit": {
                "name": "decibel",
                "code": "2N"
            },
            'archive': True
        }
        criteria_filtered = Criteria.objects.create(
            **api_criteria_data_to_model(data_for_filtering)
        )

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        get_response_json = get_response.json()
        self.assertEqual(len(get_response_json), Criteria.objects.count())

        query_params = {
            'name': 'Cus',
            'classification_id': '0311',
            'additional_classification_id': '4241',
            'archive': 'true',
            'unit_code': '2N',
        }
        for key, value in query_params.items():
            filter_get_response = self.client.get(path=API_URL, data={key: value})
            self.assertEqual(
                filter_get_response.status_code, status.HTTP_200_OK
            )
            filter_get_response_json = filter_get_response.json()
            self.assertEqual(len(filter_get_response_json), 1)
            self.assertEqual(
                filter_get_response_json[0]['id'],
                criteria_filtered.id.hex
            )

        filter_get_response = self.client.get(path=API_URL, data={'name': 'bar'})
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(len(filter_get_response.json()), 0)

        filter_get_response = self.client.get(path=API_URL, data={'foo': 'bar'})
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            len(filter_get_response.json()), Criteria.objects.count()
        )

    def test_criteria_listing_ordering(self):
        # TODO: add logic
        pass


class TestCriteriaDetail(CriteriaAPITestCase):
    def test_criteria_detail_info(self):
        self.assertEqual(Criteria.objects.count(), 0)
        criteria_data = self.valid_full_criteria_data

        Criteria.objects.create(**api_criteria_data_to_model(criteria_data))
        criteria_obj = Criteria.objects.get()

        get_response = self.client.get(path=f'{API_URL}{criteria_obj.id.hex}/')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        get_response_json = get_response.json()

        self.assertEqual(criteria_obj.name, get_response_json['name'])
        self.assertEqual(criteria_obj.name_eng, get_response_json['nameEng'])
        self.assertEqual(
            criteria_obj.data_type, get_response_json['dataType']
        )
        self.assertEqual(criteria_obj.min_value, get_response_json['minValue'])
        self.assertEqual(criteria_obj.max_value, get_response_json['maxValue'])
        self.assertDictEqual(
            criteria_obj.classification, get_response_json['classification']
        )
        self.assertDictEqual(
            criteria_obj.unit, get_response_json['unit']
        )
        self.assertDictEqual(
            criteria_obj.additional_classification,
            get_response_json['additionalClassification']
        )
        # self.assertEqual(criteria_obj.date_modified, get_response_json['dateModified'])
        self.assertEqual(criteria_obj.archive, get_response_json['archive'])
        self.assertEqual(criteria_obj.id.hex, get_response_json['id'])
