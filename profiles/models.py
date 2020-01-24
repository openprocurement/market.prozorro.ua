import uuid

from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


STATUS_CHOICES = (
    ('active', 'Active'),
    ('draft', 'Draft'),
    ('hidden', 'Hidden'),
)

CURRENCY_CHOICES = (
    ('UAH', 'UAH'),
    ('USD', 'USD'),
    ('EUR', 'EUR'),
)


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    access_token = models.UUIDField(default=uuid.uuid4, editable=False)
    author = models.CharField(max_length=50)

    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0]
    )
    date_modified = models.DateTimeField(auto_now=True)

    title = models.CharField(max_length=255)
    description = models.CharField(max_length=1000, null=True)

    classification_id = models.CharField(max_length=10)
    classification_description = models.CharField(max_length=255)

    additional_classification = ArrayField(JSONField(), blank=True, null=True)

    criteria = models.ManyToManyField('ProfileCriteria')

    images = ArrayField(JSONField(), blank=True, null=True)

    unit_code = models.CharField(max_length=5)
    unit_name = models.CharField(max_length=50)

    value_amount = models.DecimalField(max_digits=10, decimal_places=2)
    value_currency = models.CharField(
        max_length=3, choices=STATUS_CHOICES, default=CURRENCY_CHOICES[0][0]
    )
    value_value_added_tax_included = models.BooleanField(
        default=True, null=True, blank=True
    )

    class Meta:
        ordering = ('-date_modified', )

    def __str__(self):
        return f'<Profile {self.title}(id: {self.id.hex})'

    # Unit
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

    # Classification
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

    # Value
    @property
    def value(self):
        return {
            'amount': self.value_amount,
            'currency': self.value_currency,
            'valueAddedTaxIncluded': self.value_value_added_tax_included,
        }

    @value.setter
    def value(self, value):
        self.value_amount = value.get('amount')
        self.value_currency = value.get('currency')
        self.value_value_added_tax_included = value.get(
            'value_added_tax_included'
        )


class ProfileImage(models.Model):
    size = models.CharField(max_length=10, null=True)
    url = models.CharField(max_length=100, null=True)


class ProfileCriteria(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255, null=True)
    title = models.CharField(max_length=255)
    requirement_groups = models.ManyToManyField('RequirementGroup')


class RequirementGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255, null=True)
    requirements = models.ManyToManyField('Requirement')


class Requirement(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField(max_length=255, null=True)
    related_criteria = models.ForeignKey(
        'criteria.Criteria', on_delete=models.CASCADE
    )

    expected_value = models.CharField(max_length=255, null=True)
    min_value = models.CharField(max_length=255, null=True)
    max_value = models.CharField(max_length=255, null=True)
