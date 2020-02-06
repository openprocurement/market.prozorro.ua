import base64
import os

from django.conf import settings
from passlib.apache import HtpasswdFile
from rest_framework import status
from rest_framework.test import APITestCase

from profiles.models import Profile
from criteria.models import Criteria

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

        criteria_data = {
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
        criteria = Criteria.objects.create(**criteria_data)

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

    def test_profile_creating(self):
        profile_data = self.valid_profile_data_1
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


class TestProfileDetail(ProfileAPITestCase):
    def test_profile_delete(self):
        self.client.post(path=API_URL, data=self.valid_profile_data_1)
        profile_obj = Profile.objects.first()

        self.assertEqual(
            self.client.delete(
                path=f'{API_URL}{profile_obj.id.hex}/'
            ).status_code,
            status.HTTP_200_OK
        )
        profile_obj = Profile.objects.get()
        self.assertEqual(profile_obj.status, 'hidden')
