import os
from copy import deepcopy
import uuid

from django.conf import settings
from passlib.apache import HtpasswdFile
from rest_framework import status
from rest_framework.test import APITestCase

from criteria.models import Criteria
from profiles.models import Profile

API_URL = '/api/0/profiles/'

USER_CREDENTIALS = {
    'admin': 'adminpassword',
    'user': 'userpassword',
}


class ProfileAPITestCase(APITestCase):
    def setUp(self):
        ht = HtpasswdFile(settings.PATH_TO_HTPASSWD_FILE, new=True)
        for username, password in USER_CREDENTIALS.items():
            ht.set_password(username, password)
        ht.save()

        admin_token = list(USER_CREDENTIALS.values())[0]
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Token {admin_token}'
        )

        Profile.objects.all().delete()  # ensure no Profile in db

        self.criteria_data = {
            'name': 'Name',
            'classification': {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "data_type": "number",
            "unit": {
                "name": "millilitre of water",
                "code": "WW"
            }
        }
        criteria = Criteria.objects.create(**self.criteria_data)

        self.valid_profile_data_1 = {
            "title": "Test name",
            "description": "Test description",
            "classification": {
                "id": "92350000-9",
                "scheme": "ДК021",
                "description": "Послуги гральних закладів і тоталізаторів"
            },
            "additionalClassification": [
                {
                    "description": "Кишкові щипці",
                    "id": "11785",
                    "scheme": "GMDN"
                },
                {
                    "description": "Анатомічні пінцети для розтину",
                    "scheme": "ДК021",
                    "id": "33912100-7"
                },
            ],
            "images": [
                {
                    "sizes": "228",
                    "url": "https://test.url"
                }
            ],
            "unit": {
                "name": "Одиниця",
                "code": "E50"
            },
            "value": {
                "valueAddedTaxIncluded": 'true',
                "amount": "50.00",
                "currency": "UAH"
            },
            "criteria": [
                {
                    "title": "Test criteria",
                    "description": "Test description",
                    "requirementGroups": [
                        {
                            "description": "Test requirement group",
                            "requirements": [
                                {
                                    "title": "Test requirement",
                                    "description": "Test requirement description",
                                    "relatedCriteria_id": criteria.id.hex,
                                    "expectedValue": "5",
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        self.valid_profile_data_2 = {
            "title": "Test name2",
            "description": "Test description2",
            "classification": {
                "id": "03114100-4",
                "scheme": "ДК021",
                "description": "Солома"
            },
            "additionalClassification": [
                {
                    "description": "Насіння",
                    "scheme": "ДК021",
                    "id": "03111000-2"
                },
            ],
            "images": [
                {
                    "sizes": "300",
                    "url": "https://test.url"
                }
            ],
            "unit": {
                "name": "Одиниця",
                "code": "E50"
            },
            "value": {
                "valueAddedTaxIncluded": 'false',
                "amount": "50.00",
                "currency": "UAH"
            },
            "criteria": [
                {
                    "title": "Test criteria2",
                    "description": "Test description2",
                    "requirementGroups": [
                        {
                            "description": "Test requirement group2",
                            "requirements": [
                                {
                                    "title": "Test requirement2",
                                    "description": "Test requirement description2",
                                    "relatedCriteria_id": criteria.id.hex,
                                    "expectedValue": "100",
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        self.valid_profile_data = (
            self.valid_profile_data_1,
            self.valid_profile_data_2,
        )

    def tearDown(self):
        Profile.objects.all().delete()  # ensure no Criteria in db
        os.remove(settings.PATH_TO_HTPASSWD_FILE)


class TestProfileCreating(ProfileAPITestCase):
    def test_profile_creating_errors(self):
        self.assertEqual(Profile.objects.count(), 0)
        self.assertEqual(
            self.client.post(path=API_URL).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(Profile.objects.count(), 0)

        profile_data = deepcopy(self.valid_profile_data_1)

        requirement = profile_data['criteria'][0]['requirementGroups'][0]['requirements'][0]

        requirement['maxValue'] = 5
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        requirement.pop('maxValue')
        requirement.pop('expectedValue')
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        requirement['maxValue'] = None
        criteria = Criteria.objects.get(id=requirement['relatedCriteria_id'])

        criteria.data_type = 'string'
        criteria.save()
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria.data_type = 'number'
        criteria.save()
        requirement['maxValue'] = 'gmo'
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria.data_type = 'integer'
        criteria.save()
        requirement['maxValue'] = '2.4'
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        criteria.data_type = 'boolean'
        criteria.save()
        requirement['maxValue'] = 'foo'
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        requirement['relatedCriteria_id'] = uuid.uuid4()
        self.assertEqual(
            self.client.post(path=API_URL, data=profile_data).status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_profile_creating(self):
        profile_data = self.valid_profile_data_2
        post_response = self.client.post(path=API_URL, data=profile_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)

        profile_obj = Profile.objects.get()

        self.assertIsNotNone(profile_obj.author)
        self.assertIsNotNone(profile_obj.id)
        self.assertEqual(profile_obj.status, 'active')
        self.assertEqual(
            profile_obj.criteria.count(), len(profile_data['criteria'])
        )
        profile_criteria = profile_obj.criteria.all()[0]
        profile_criteria_data = profile_data['criteria'][0]
        self.assertIsNotNone(profile_criteria.id)
        self.assertEqual(
            profile_criteria.requirement_groups.count(),
            len(profile_criteria_data['requirementGroups'])
        )

        requirement_group_data = profile_criteria_data['requirementGroups'][0]
        requirement_group = profile_criteria.requirement_groups.all()[0]
        self.assertIsNotNone(requirement_group.id)
        self.assertEqual(
            requirement_group.requirements.count(),
            len(requirement_group_data['requirements'])
        )

        self.assertEqual(
            len(profile_obj.additional_classification),
            len(profile_data['additionalClassification'])
        )

    def test_profile_access_token(self):
        post_response = self.client.post(
            path=API_URL, data=self.valid_profile_data_1
        )
        access_data = post_response.json().get('access')
        self.assertIsNotNone(access_data)
        access_token = access_data.get('token')

        profile_obj = Profile.objects.first()
        self.assertEqual(access_token, profile_obj.access_token.hex)
        self.assertEqual(access_data.get('owner'), profile_obj.author)


class TestProfileListing(ProfileAPITestCase):
    def test_profile_listing(self):
        self.assertEqual(Profile.objects.count(), 0)

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(get_response.json()['results'], [])
        for data in self.valid_profile_data:
            self.client.post(path=API_URL, data=data)
        self.assertEqual(Profile.objects.count(), len(self.valid_profile_data))

        get_response = self.client.get(path=API_URL)
        self.assertEqual(
            get_response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            len(get_response.json()['results']),
            len(self.valid_profile_data)
        )

    def test_profile_filtering(self):
        criteria = Criteria.objects.create(**self.criteria_data)
        self.assertEqual(Criteria.objects.count(), 2)

        profile_data = deepcopy(self.valid_profile_data_2)
        post_response = self.client.post(path=API_URL, data=profile_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 1)

        profile_data['criteria'][0]['requirementGroups'][0]['requirements'][0]['relatedCriteria_id'] = criteria.id.hex
        post_response = self.client.post(path=API_URL, data=profile_data)
        self.assertEqual(post_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Profile.objects.count(), 2)
        profile_id = post_response.json()['data']['id']

        get_response = self.client.get(
            path=API_URL,
            data={'criteria_requirementGroups_requirements_relatedCriteria_id': criteria.id.hex}
        )
        self.assertEqual(get_response.json()['count'], 1)
        self.assertEqual(get_response.json()['results'][0]['id'], profile_id)


class TestProfileDetail(ProfileAPITestCase):
    def test_profile_detail_info(self):
        self.client.post(path=API_URL, data=self.valid_profile_data_1)
        profile_obj = Profile.objects.first()

        get_response = self.client.get(path=f'{API_URL}{profile_obj.id.hex}/')
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        get_response_json = get_response.json()
        self.assertEqual(profile_obj.title, get_response_json['title'])
        self.assertEqual(profile_obj.id.hex, get_response_json['id'])
        self.assertEqual(profile_obj.author, get_response_json['author'])
        self.assertEqual(profile_obj.status, get_response_json['status'])
        self.assertEqual(
            profile_obj.description, get_response_json['description']
        )

        self.assertEqual(
            profile_obj.criteria.count(), len(get_response_json['criteria'])
        )
        profile_criteria = profile_obj.criteria.all()[0]
        profile_criteria_data = get_response_json['criteria'][0]
        self.assertIsNotNone(profile_criteria.id)
        self.assertEqual(
            profile_criteria.requirement_groups.count(),
            len(profile_criteria_data['requirementGroups'])
        )

        requirement_group_data = profile_criteria_data['requirementGroups'][0]
        requirement_group = profile_criteria.requirement_groups.all()[0]
        self.assertIsNotNone(requirement_group.id)
        self.assertEqual(
            requirement_group.requirements.count(),
            len(requirement_group_data['requirements'])
        )

        self.assertEqual(
            len(profile_obj.additional_classification),
            len(get_response_json['additionalClassification'])
        )

    def test_profile_patch(self):
        post_response = self.client.post(
            path=API_URL, data=self.valid_profile_data_1
        )
        correct_access_data = post_response.json().get('access')

        profile_obj = Profile.objects.first()
        data = {
            'data': {
                'title': 'New name'
            }
        }

        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{profile_obj.id.hex}/', data=data
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        data['access'] = {
            'owner': 'foo',
            'token': 'bar'
        }
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{profile_obj.id.hex}/', data=data
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        data['access'] = correct_access_data
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(patch_response.json()['title'], 'New name')

        # adding new requirements to existing requirement group
        criteria = Criteria.objects.create(**self.criteria_data)
        criteria_data = post_response.json()['data']['criteria'][0]
        requirement_group_data = criteria_data['requirementGroups'][0]
        requirements = requirement_group_data['requirements']

        new_requirement = {
            "title": "New requirement",
            "description": "New requirement description2",
            "relatedCriteria_id": criteria.id.hex,
            "expectedValue": "322",
        }
        requirements.append(new_requirement)
        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
                'requirementGroups': [
                    {
                        'id': requirement_group_data['id'],
                        'requirements': requirements
                    }
                ]
            }
        ]
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(patch_response.json()['criteria'][0]['requirementGroups'][0]['requirements']),
            len(requirements)
        )

        data['data']['namess'] = 'foo'
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{profile_obj.id.hex}/', data=data
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )
        data['data'].pop('namess')

        # adding new requirement group
        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
                'requirementGroups': [
                    {
                        'requirements': [new_requirement]
                    },
                    {
                        'id': requirement_group_data['id']
                    }
                ]
            }
        ]
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(patch_response.json()['criteria'][0]['requirementGroups']), 2
        )

        # adding new criteria
        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
            },
            {
                'requirementGroups': [
                    {
                        'requirements': [new_requirement]
                    },
                    {
                        'id': requirement_group_data['id'],
                        'description': 'foo'
                    }
                ]
            }
        ]
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(patch_response.json()['criteria']), 2
        )
        self.assertEqual(
            patch_response.json()['criteria'][1]['requirementGroups'][1]['description'],
            'foo'
        )

        # editing requirement group
        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
                'requirementGroups': [
                    {
                        'id': uuid.uuid4(),
                    }
                ]
            }
        ]
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{profile_obj.id.hex}/', data=data
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
                'requirementGroups': [
                    {
                        'id': requirement_group_data['id'],
                        'description': 'new description'
                    }
                ]
            }
        ]
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            patch_response.json()['criteria'][0]['requirementGroups'][0]['description'],
            'new description'
        )

        # editing criteria
        data['data']['criteria'] = [
            {
                'id': uuid.uuid4(),
                'title': 'foo'
            }
        ]
        self.assertEqual(
            self.client.patch(
                path=f'{API_URL}{profile_obj.id.hex}/', data=data
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        data['data']['criteria'] = [
            {
                'id': criteria_data['id'],
                'title': 'foo'
            }
        ]
        patch_response = self.client.patch(
            path=f'{API_URL}{profile_obj.id.hex}/',
            data=data
        )
        self.assertEqual(patch_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            patch_response.json()['criteria'][0]['title'], 'foo'
        )

    def test_profile_delete(self):
        self.client.post(path=API_URL, data=self.valid_profile_data_1)
        profile_obj = Profile.objects.first()
        correct_access_data = {
            "token": profile_obj.access_token.hex,
            "owner": profile_obj.author,
        }

        self.assertEqual(
            self.client.delete(
                path=f'{API_URL}{profile_obj.id.hex}/'
            ).status_code,
            status.HTTP_400_BAD_REQUEST
        )

        self.assertEqual(
            self.client.delete(
                path=f'{API_URL}{profile_obj.id.hex}/',
                data={'access': correct_access_data}
            ).status_code,
            status.HTTP_200_OK
        )

        profile_obj = Profile.objects.get()
        self.assertEqual(profile_obj.status, 'hidden')
