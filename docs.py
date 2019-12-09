import json
from simplejson.errors import JSONDecodeError
from webtest import TestApp
from webob.request import DisconnectionError


API_URL = '/api/0/criteria/'
API_HOST = 'http://127.0.0.1:8000'

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
        resp = self.app.get(API_URL)
        return self._format_response_output(resp)

    def _create_criteria(self):
        resp = self.app.post_json(API_URL, CRITERIA_DATA)

        self.criteria_id = resp.json['id']
        return self._format_response_output(resp)

    def _view_criteria(self):
        resp = self.app.get(f'{API_URL}{self.criteria_id}/')
        return self._format_response_output(resp)

    def _patch_criteria(self):
        resp = self.app.patch_json(f'{API_URL}{self.criteria_id}/', {'name': 'New name'})
        return self._format_response_output(resp)

    def _delete_criteria(self):
        resp = self.app.delete(f'{API_URL}{self.criteria_id}/')
        return self._format_response_output(resp)

    def _write_resp_to_file(self, content, file_path):
        text_file = open(file_path, 'wt')
        text_file.write(content)
        text_file.close()

    def generate_code_snippets(self):
        self._write_resp_to_file(self._create_criteria(), 'docs/create_criteria.html')
        self._write_resp_to_file(self._view_criteria(), 'docs/view_criteria.html')
        self._write_resp_to_file(self._patch_criteria(), 'docs/patch_criteria.html')
        self._write_resp_to_file(self._delete_criteria(), 'docs/delete_criteria.html')


if __name__ == "__main__":
    CriteriaDocsGenerator().generate_code_snippets()
