import json
import uuid
from simplejson.errors import JSONDecodeError
from webtest import TestApp
from webob.request import DisconnectionError


CRITERIA_URL = '/api/0/criteria/'
PROFILE_URL = '/api/0/profiles/'

API_HOST = 'http://127.0.0.1:8080'

CRITERIA_DATA = {
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

PROFILE_DATA = {
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
                            "relatedCriteria_id": uuid.uuid4(),
                            "expectedValue": "5",
                        }
                    ]
                }
            ]
        }
    ]
}


class CriteriaDocsGenerator:

    app = TestApp(API_HOST)

    def __init__(self, *args, **kwargs):
        self.app.authorization = ('Basic', ('admin', 'adminpassword'))

    def _format_response_output(self, resp):
        request = resp.request
        url = request.url
        host = request.host_url
        url = url[len(host):]
        parts = [(f'{request.method} {url} {request.http_version}')]

        for k, v in sorted(request.headers.items()):
            header = f'{k} {v}'
            parts.append(header)

        try:
            try:
                parts.append(json.dumps(request.json or {}, indent=2, ensure_ascii=False))
            except JSONDecodeError:
                parts.append(json.dumps(request.text or {}, indent=2, ensure_ascii=False))
        except DisconnectionError:
            parts.append(json.dumps(CRITERIA_DATA, indent=2, ensure_ascii=False))
        parts.extend(['', ''])
        try:
            resp.charset = 'UTF-8'
        except AttributeError:
            pass
        parts.append(resp.status)
        for k, v in sorted(request.headers.items()):
            header = f'{k} {v}'
            parts.append(header)

        try:
            parts.append(json.dumps(resp.json or {}, indent=2, ensure_ascii=False))
        except AttributeError:
            pass
        return '\r\n'.join(parts)

    def _criteria_listing(self):
        resp = self.app.get(CRITERIA_URL)
        return self._format_response_output(resp)

    def _create_criteria(self):
        resp = self.app.post_json(CRITERIA_URL, CRITERIA_DATA)

        self.criteria_id = resp.json['id']
        return self._format_response_output(resp)

    def _view_criteria(self):
        resp = self.app.get(f'{CRITERIA_URL}{self.criteria_id}/')
        return self._format_response_output(resp)

    def _patch_criteria(self):
        resp = self.app.patch_json(f'{CRITERIA_URL}{self.criteria_id}/', {'name': 'New name'})
        return self._format_response_output(resp)

    def _delete_criteria(self):
        resp = self.app.delete(f'{CRITERIA_URL}{self.criteria_id}/')
        return self._format_response_output(resp)

    def _write_resp_to_file(self, content, file_path):
        text_file = open(file_path, 'wt')
        text_file.write(content)
        text_file.close()

    def generate_code_snippets(self):
        print(' - Creating Criteria')
        self._write_resp_to_file(self._create_criteria(), 'docs/create_criteria.html')
        print(' - View Criteria')
        self._write_resp_to_file(self._view_criteria(), 'docs/view_criteria.html')
        print(' - Patch Criteria')
        self._write_resp_to_file(self._patch_criteria(), 'docs/patch_criteria.html')
        print(' - Delete Criteria')
        self._write_resp_to_file(self._delete_criteria(), 'docs/delete_criteria.html')


class ProfileDocsGenerator:
    app = TestApp(API_HOST)

    def __init__(self, *args, **kwargs):
        self.app.authorization = ('Basic', ('admin', 'adminpassword'))

    def _format_response_output(self, resp, data_passed=None):
        request = resp.request
        url = request.url
        host = request.host_url
        url = url[len(host):]
        parts = [(f'{request.method} {url} {request.http_version}')]

        for k, v in sorted(request.headers.items()):
            header = f'{k} {v}'
            parts.append(header)

        try:
            try:
                parts.append(json.dumps(request.json or {}, indent=2, ensure_ascii=False))
            except JSONDecodeError:
                parts.append(json.dumps(request.text or {}, indent=2, ensure_ascii=False))
        except DisconnectionError:
            parts.append(json.dumps(data_passed, indent=2, ensure_ascii=False))
        parts.extend(['', ''])
        try:
            resp.charset = 'UTF-8'
        except AttributeError:
            pass
        parts.append(resp.status)
        for k, v in sorted(request.headers.items()):
            header = f'{k} {v}'
            parts.append(header)

        try:
            parts.append(json.dumps(resp.json or {}, indent=2, ensure_ascii=False))
        except AttributeError:
            pass
        return '\r\n'.join(parts)

    def _profile_listing(self):
        for _ in range(2):
            criteria_create_response = self.app.post_json(CRITERIA_URL, CRITERIA_DATA)
            self.criteria_id = criteria_create_response.json['id']
            PROFILE_DATA['criteria'][0]['requirementGroups'][0]['requirements'][0]['relatedCriteria_id'] = self.criteria_id
            self.app.post_json(PROFILE_URL, PROFILE_DATA)

        resp = self.app.get(f'{PROFILE_URL}?limit=2')
        return self._format_response_output(resp)

    def _profile_filtering(self):
        resp = self.app.get(f'{PROFILE_URL}?criteria_requirementGroups_requirements_relatedCriteria_id={self.criteria_id}')
        return self._format_response_output(resp)

    def _create_profile(self):
        criteria_create_response = self.app.post_json(CRITERIA_URL, CRITERIA_DATA)
        self.criteria_id = criteria_create_response.json['id']

        PROFILE_DATA['criteria'][0]['requirementGroups'][0]['requirements'][0]['relatedCriteria_id'] = self.criteria_id
        resp = self.app.post_json(PROFILE_URL, PROFILE_DATA)

        self.profile_id = resp.json['data']['id']
        self.access_data = resp.json['access']

        return self._format_response_output(resp, PROFILE_DATA)

    def _view_profile(self):
        resp = self.app.get(f'{PROFILE_URL}{self.profile_id}/')
        return self._format_response_output(resp)

    def _patch_profile_title(self):
        patch_data = {
            'access': self.access_data,
            'data': {
                'title': 'New title'
            }
        }
        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_change_criteria_list(self):
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        "title": "New criteria",
                        "description": "New description",
                        "requirementGroups": [
                            {
                                "description": "New requirement group",
                                "requirements": [
                                    {
                                        "title": "New requirement",
                                        "description": "New requirement description",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_add_criteria(self):
        profile_data = self.app.get(f'{PROFILE_URL}{self.profile_id}/').json
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        'id': profile_data['criteria'][0]['id']
                    },
                    {
                        "title": "New new criteria",
                        "description": "New new description",
                        "requirementGroups": [
                            {
                                "description": "New new requirement group",
                                "requirements": [
                                    {
                                        "title": "New new requirement",
                                        "description": "New new requirement description",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }

        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_edit_criteria(self):
        profile_data = self.app.get(f'{PROFILE_URL}{self.profile_id}/').json
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        'id': profile_data['criteria'][0]['id'],
                        'title': 'Completely new title'
                    },
                ]
            }
        }
        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_add_requirement_group_to_criteria(self):
        profile_data = self.app.get(f'{PROFILE_URL}{self.profile_id}/').json
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        'id': profile_data['criteria'][0]['id'],
                        'requirementGroups': [
                            {
                                'id': profile_data['criteria'][0]['requirementGroups'][0]['id']
                            },
                            {
                                "description": "Second requirement group",
                                "requirements": [
                                    {
                                        "title": "Second requirement",
                                        "description": "Second requirement description",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        }

        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_set_requirement_groups_to_criteria(self):
        profile_data = self.app.get(f'{PROFILE_URL}{self.profile_id}/').json
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        'id': profile_data['criteria'][0]['id'],
                        'requirementGroups': [
                            {
                                "description": "Requirement group 1",
                                "requirements": [
                                    {
                                        "title": "Requirement 1",
                                        "description": "Requirement description 1",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        }

        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _patch_profile_set_requirements_to_criteria(self):
        profile_data = self.app.get(f'{PROFILE_URL}{self.profile_id}/').json
        patch_data = {
            'access': self.access_data,
            'data': {
                'criteria': [
                    {
                        'id': profile_data['criteria'][0]['id'],
                        'requirementGroups': [
                            {
                                'id': profile_data['criteria'][0]['requirementGroups'][0]['id'],
                                "requirements": [
                                    {
                                        "title": "Requirement 1",
                                        "description": "Requirement description 1",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    },
                                    {
                                        "title": "Requirement 2",
                                        "description": "Requirement description 2",
                                        "relatedCriteria_id": self.criteria_id,
                                        "expectedValue": "5",
                                    }
                                ]
                            }
                        ]
                    },
                ]
            }
        }

        resp = self.app.patch_json(
            f'{PROFILE_URL}{self.profile_id}/',
            patch_data,
            content_type='application/json'
        )
        return self._format_response_output(resp, patch_data)

    def _delete_profile(self):
        resp = self.app.delete(
            url=f'{PROFILE_URL}{self.profile_id}/',
            params=json.dumps({'access': self.access_data}),
            content_type='application/json'
        )
        return self._format_response_output(resp, {'access': self.access_data})

    def _write_resp_to_file(self, content, file_path):
        text_file = open(file_path, 'wt')
        text_file.write(content)
        text_file.close()

    def generate_code_snippets(self):
        print(' - Creating Profile')
        self._write_resp_to_file(
            self._create_profile(),
            'docs/create_profile.html'
        )
        print(' - Listing Profile')
        self._write_resp_to_file(
            self._profile_listing(),
            'docs/listing_profile.html'
        )
        print(' - Filtering Profile')
        self._write_resp_to_file(
            self._profile_filtering(),
            'docs/filtering_profile.html'
        )
        print(' - View Profile')
        self._write_resp_to_file(
            self._view_profile(),
            'docs/view_profile.html'
        )
        print(' - Patch Profile')
        self._write_resp_to_file(
            self._patch_profile_title(),
            'docs/patch_profile_title.html'
        )
        self._write_resp_to_file(
            self._patch_profile_change_criteria_list(),
            'docs/patch_profile_change_criteria_list.html'
        )
        self._write_resp_to_file(
            self._patch_profile_add_criteria(),
            'docs/patch_profile_add_criteria.html'
        )
        self._write_resp_to_file(
            self._patch_profile_edit_criteria(),
            'docs/patch_profile_edit_criteria.html'
        )
        self._write_resp_to_file(
            self._patch_profile_add_requirement_group_to_criteria(),
            'docs/patch_profile_add_requirement_group_to_criteria.html'
        )
        self._write_resp_to_file(
            self._patch_profile_set_requirement_groups_to_criteria(),
            'docs/patch_profile_set_requirement_groups_to_criteria.html'
        )
        self._write_resp_to_file(
            self._patch_profile_set_requirements_to_criteria(),
            'docs/patch_profile_set_requirements_to_criteria.html'
        )

        print(' - Delete Profile')
        self._write_resp_to_file(self._delete_profile(), 'docs/delete_profile.html')


if __name__ == "__main__":
    print('Generating snippets for Criteria')
    CriteriaDocsGenerator().generate_code_snippets()
    print('Generating snippets for Profile')
    ProfileDocsGenerator().generate_code_snippets()
