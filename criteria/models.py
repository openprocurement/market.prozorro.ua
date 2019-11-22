import uuid
from django.db import models

DATATYPE_CHOICES = (
    ('string', 'string'),
    ('boolean', 'boolean'),
    ('integer', 'integer'),
    ('number', 'number'),
)


class Criteria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True)
    name_eng = models.CharField(max_length=255, null=True)
    data_type = models.CharField(max_length=10, choices=DATATYPE_CHOICES)
    min_value = models.CharField(max_length=50, null=True)
    max_value = models.CharField(max_length=50, null=True)

    unit_code = models.CharField(max_length=5)
    unit_name = models.CharField(max_length=50)

    classification_id = models.CharField(max_length=10)
    classification_description = models.CharField(max_length=255)

    additional_classification_id = models.CharField(max_length=10, null=True)
    additional_classification_description = models.CharField(max_length=255, null=True)
    additional_classification_scheme = models.CharField(max_length=10, null=True)

    date_modified = models.DateTimeField(auto_now=True)
    archive = models.BooleanField(default=False)

    class Meta:
        ordering = ('-date_modified', )

    def __str__(self):
        return f'<Criteria for classification (id: {self.classification_id})'

    @property
    def unit(self):
        return {
            'name': self.unit_name,
            'code': self.unit_code,
        }

    @unit.setter
    def unit(self, value):
        self.unit_name = value.get('name')
        self.unit_code = value.get('code')

    @property
    def classification_scheme(self):
        return 'ДК021'

    @property
    def classification(self):
        return {
            'id': self.classification_id,
            'scheme': self.classification_scheme,
            'description': self.classification_description,
        }

    @classification.setter
    def classification(self, value):
        self.classification_id = value.get('id')
        self.classification_description = value.get('description')

    @property
    def additional_classification(self):
        if not self.additional_classification_id:
            return None
        return {
            'id': self.additional_classification_id,
            'scheme': self.additional_classification_scheme,
            'description': self.additional_classification_description,
        }

    @additional_classification.setter
    def additional_classification(self, value):
        self.additional_classification_id = value.get('id')
        self.additional_classification_scheme = value.get('scheme')
        self.additional_classification_description = value.get('description')