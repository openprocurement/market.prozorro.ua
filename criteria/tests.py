import base64
import os
from copy import deepcopy

from django.conf import settings
from passlib.apache import HtpasswdFile
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


USER_CREDENTIALS = {
    'admin': 'adminpassword',
    'user': 'userpassword',
}


class TestAuth(APITestCase):

    def setUp(self):
        # creating file with credentials
        ht = HtpasswdFile(settings.PATH_TO_HTPASSWD_FILE, new=True)
        for username, password in USER_CREDENTIALS.items():
            ht.set_password(username, password)
        ht.save()

    def tearDown(self):
        os.remove(settings.PATH_TO_HTPASSWD_FILE)  # deleting created file

    def test_authorization(self):
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_401_UNAUTHORIZED
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token random_token'
        )
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_401_UNAUTHORIZED
        )
        random_basic_header = base64.b64encode(
            'wrong_username:password'.encode("utf-8")
        ).decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {random_basic_header}')
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_401_UNAUTHORIZED
        )

        username = 'admin'
        password = 'wrong_password'
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {password}'
        )
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_401_UNAUTHORIZED
        )
        basic_auth_header = base64.b64encode(
            f'{username}:{password}'.encode("utf-8")
        ).decode('utf-8')
        self.client.credentials(HTTP_AUTHORIZATION=f'Basic {basic_auth_header}')
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_401_UNAUTHORIZED
        )

        for username, password in USER_CREDENTIALS.items():
            self.client.credentials(
                HTTP_AUTHORIZATION=f'Token {password}'
            )
            self.assertEqual(
                self.client.get(path=API_URL).status_code, status.HTTP_200_OK
            )
            basic_auth_header = base64.b64encode(
                f'{username}:{password}'.encode("utf-8")
            ).decode('utf-8')
            self.client.credentials(HTTP_AUTHORIZATION=f'Basic {basic_auth_header}')
            self.assertEqual(
                self.client.get(path=API_URL).status_code, status.HTTP_200_OK
            )

    def test_admin_permissions(self):
        admin_token = list(USER_CREDENTIALS.values())[0]
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {admin_token}'
        )
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_200_OK
        )

        criteria_data = {
            'name': 'Name',
            'classification': {
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

        post_response = self.client.post(path=API_URL, data=criteria_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)

        criteria_id = post_response.json()['id']
        self.assertEqual(
            self.client.get(path=f'{API_URL}{criteria_id}/').status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{criteria_id}/',
                data={'name': 'New name'}
            ).status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            self.client.delete(path=f'{API_URL}{criteria_id}/').status_code,
            status.HTTP_200_OK
        )

    def test_regular_user_permissions(self):
        regular_user_token = list(USER_CREDENTIALS.values())[1]
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {regular_user_token}'
        )
        self.assertEqual(
            self.client.get(path=API_URL).status_code, status.HTTP_200_OK
        )

        criteria_data = {
            'name': 'Name',
            'classification': {
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

        post_response = self.client.post(path=API_URL, data=criteria_data)
        self.assertEqual(post_response.status_code, status.HTTP_403_FORBIDDEN)
        criteria_obj = Criteria.objects.create(
            **api_criteria_data_to_model(criteria_data)
        )

        criteria_id = criteria_obj.id
        self.assertEqual(
            self.client.get(path=f'{API_URL}{criteria_id}/').status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{criteria_id}/',
                data={'name': 'New name'}
            ).status_code,
            status.HTTP_403_FORBIDDEN
        )
        self.assertEqual(
            self.client.delete(path=f'{API_URL}{criteria_id}/').status_code,
            status.HTTP_403_FORBIDDEN
        )


class CriteriaAPITestCase(APITestCase):
    def setUp(self):
        ht = HtpasswdFile(settings.PATH_TO_HTPASSWD_FILE, new=True)
        for username, password in USER_CREDENTIALS.items():
            ht.set_password(username, password)
        ht.save()

        admin_token = list(USER_CREDENTIALS.values())[0]
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {admin_token}'
        )

        Criteria.objects.all().delete()  # ensure no Criteria in db
        self.valid_criteria_data_1 = {
            "name": "c",
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
            "name": "b",
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
            "name": "a",
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
                "id": "03114100-4",
                "scheme": "ДК021",
                "description": "Солома"
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
        os.remove(settings.PATH_TO_HTPASSWD_FILE)


class TestCriteriaCreating(CriteriaAPITestCase):
    def test_criteria_creating_errors(self):
        self.assertEqual(Criteria.objects.count(), 0)
        self.assertEqual(
            self._post_json(path=API_URL).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Criteria.objects.count(), 0)

    def test_criteria_basic_validation(self):
        criteria_data = deepcopy(self.valid_full_criteria_data)
        criteria_data['minValue'] = 'foo'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data['maxValue'] = 'foo'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data['maxValue'] = '1'
        criteria_data['minValue'] = '2'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_criteria_classifiers_reference_validation(self):
        criteria_data = deepcopy(self.valid_full_criteria_data)
        criteria_data['classification']['id'] = '1111111111-1'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data['classification']['id'] = '22222222-1'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data['additionalClassification']['scheme'] = 'foo'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria_data['unit']['code'] = 'foo'
        self.assertEqual(
            self._post_json(path=API_URL, data=criteria_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

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
        self.assertEqual(criteria_obj.status, 'active')
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
        self.assertEqual(post_response_json['status'], 'active')
        self.assertIsNotNone(post_response_json['id'])


class TestCriteriaListing(CriteriaAPITestCase):
    def test_criteria_listing(self):
        self.assertEqual(Criteria.objects.count(), 0)

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(get_response.json()['results'], [])
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))
        self.assertEqual(
            Criteria.objects.count(), len(self.valid_criteria_data)
        )

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            len(get_response.json()['results']),
            len(self.valid_criteria_data)
        )

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
            }
        }
        criteria_filtered = Criteria.objects.create(
            **api_criteria_data_to_model(data_for_filtering)
        )

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        get_response_json = get_response.json()
        self.assertEqual(
            len(get_response_json['results']),
            Criteria.objects.count()
        )

        query_params = {
            'name': 'Cus',
            'classification_id': '0311',
            'additionalClassification_id': '4241',
            'unit_code': '2N',
        }
        for key, value in query_params.items():
            filter_get_response = self.client.get(path=API_URL, data={key: value})
            self.assertEqual(
                filter_get_response.status_code, status.HTTP_200_OK
            )
            filter_get_response_json = filter_get_response.json()
            self.assertEqual(len(filter_get_response_json['results']), 1)
            self.assertEqual(
                filter_get_response_json['results'][0]['id'],
                criteria_filtered.id.hex
            )

        filter_get_response = self.client.get(path=API_URL, data={'name': 'bar'})
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(len(filter_get_response.json()['results']), 0)

        filter_get_response = self.client.get(path=API_URL, data={'foo': 'bar'})
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )

    def test_criteria_filtering_by_status(self):
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))

        criteria_obj = Criteria.objects.all()[0]
        criteria_obj.status = 'archive'
        criteria_obj.save()
        filter_get_response = self.client.get(
            path=API_URL, data={'status': 'all'}
        )
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            len(filter_get_response.json()['results']),
            Criteria.objects.count()
        )
        filter_get_response = self.client.get(
            path=API_URL, data={'status': 'archive'}
        )
        self.assertEqual(
            filter_get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            len(filter_get_response.json()['results']),
            Criteria.objects.filter(status='archive').count()
        )

    def test_criteria_listing_ordering(self):
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))
        for ordering in ('name', '-name'):
            get_response = self.client.get(path=API_URL, data={'ordering': ordering})
            self.assertEqual(
                get_response.status_code, status.HTTP_200_OK
            )
            get_response_json = get_response.json()['results']
            self.assertEqual(len(get_response_json), Criteria.objects.count())
            self.assertEqual(
                get_response_json[0]['id'],
                Criteria.objects.all().order_by(ordering)[0].id.hex
            )

    def test_criteria_listing_opt_fields(self):
        for data in self.valid_criteria_data:
            Criteria.objects.create(**api_criteria_data_to_model(data))
        get_response_results = self.client.get(path=API_URL).json()['results']
        for result in get_response_results:
            self.assertNotIn('dateModified', result)
            self.assertNotIn('nameEng', result)

        # test passing one opt_field
        get_response_results = self.client.get(
            path=API_URL, data={'opt_fields': 'dateModified'}).json()['results']
        for result in get_response_results:
            self.assertIn('dateModified', result)

        # test passing multiple opt_field
        get_response_results = self.client.get(
            path=API_URL, data={'opt_fields': 'dateModified,nameEng'}).json()['results']
        for result in get_response_results:
            self.assertIn('dateModified', result)
            self.assertIn('nameEng', result)

        # test returning only fields from model
        get_response_results = self.client.get(
            path=API_URL, data={'opt_fields': 'dateModified,foo'}).json()['results']
        for result in get_response_results:
            self.assertIn('dateModified', result)
            self.assertNotIn('foo', result)


class TestCriteriaDetail(CriteriaAPITestCase):
    def test_criteria_detail_info(self):
        self.assertEqual(Criteria.objects.count(), 0)
        criteria_data = self.valid_full_criteria_data

        criteria_obj = Criteria.objects.create(
            **api_criteria_data_to_model(criteria_data)
        )

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
        self.assertEqual(criteria_obj.status, get_response_json['status'])
        self.assertEqual(criteria_obj.id.hex, get_response_json['id'])

    def test_criteria_patch(self):
        criteria_obj = Criteria.objects.create(
            **api_criteria_data_to_model(self.valid_full_criteria_data)
        )

        patch_response = self.client.patch(
            path=f'{API_URL}{criteria_obj.id.hex}/',
            data={'name': 'Changed name'},
            format='json'
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)

        self.assertEqual(patch_response.json()['name'], 'Changed name')
        criteria_obj = Criteria.objects.get()
        self.assertEqual(criteria_obj.name, 'Changed name')

    def test_criteria_patch_allowed_fields(self):
        criteria_obj = Criteria.objects.create(
            **api_criteria_data_to_model(self.valid_full_criteria_data)
        )

        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{criteria_obj.id.hex}/',
                data={'dataType': 'Changed name'},
                format='json'
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_criteria_delete(self):
        criteria_obj = Criteria.objects.create(
            **api_criteria_data_to_model(self.valid_full_criteria_data)
        )

        self.assertEqual(
            self.client.delete(
                path=f'{API_URL}{criteria_obj.id.hex}/'
            ).status_code,
            status.HTTP_200_OK
        )
        criteria_obj = Criteria.objects.get()
        self.assertEqual(criteria_obj.status, 'retired')
