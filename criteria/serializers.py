from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from criteria.models import DATATYPE_CHOICES, Criteria
from standarts.validators import StandartsByReferenceValidator


class UnitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=5)

    def validate(self, data):
        StandartsByReferenceValidator(data).validate_unit()
        return data


class BaseClassificationSerializer(serializers.Serializer):
    description = serializers.CharField(max_length=255)

    def validate(self, data):
        return StandartsByReferenceValidator(data).validate_classifiers()


class ClassificationSerializer(BaseClassificationSerializer):
    scheme = serializers.CharField(max_length=15, read_only=True)
    id = serializers.CharField(
        max_length=10,
        validators=(
            RegexValidator(regex=r'^\d{8}-\d$'),
        )
    )

    def validate(self, data):
        data['scheme'] = 'ДК021'
        return super().validate(data)


class AdditionalClassificationSerializer(BaseClassificationSerializer):
    id = serializers.CharField(max_length=10)
    scheme = serializers.CharField(max_length=15)


class CriteriaListSerializer(serializers.ModelSerializer):
    DEFAULT_FIELDNAMES = [
        'id', 'name', 'classification', 'additionalClassification',
        'unit', 'status'
    ]

    id = serializers.CharField(source='id.hex', read_only=True)
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification', allow_null=True
    )
    unit = UnitSerializer()
    minValue = serializers.FloatField(source='min_value', required=False)
    maxValue = serializers.FloatField(source='max_value', required=False)
    dataType = serializers.ChoiceField(
        source='data_type', choices=DATATYPE_CHOICES
    )
    nameEng = serializers.CharField(source='name_eng', required=False)
    dateModified = serializers.DateTimeField(source='date_modified')

    class Meta:
        model = Criteria
        fields = '__all__'

    def get_field_names(self, *args, **kwargs):
        all_fields = super().get_field_names(*args, **kwargs)

        optional_fields = self.context['request'].GET.get('opt_fields', '').split(',')
        return self.DEFAULT_FIELDNAMES + [field for field in optional_fields if field in all_fields]


class CriteriaCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex', read_only=True)
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification', allow_null=True
    )
    unit = UnitSerializer()
    minValue = serializers.FloatField(source='min_value', required=False)
    maxValue = serializers.FloatField(source='max_value', required=False)
    dataType = serializers.ChoiceField(
        source='data_type', choices=DATATYPE_CHOICES
    )
    nameEng = serializers.CharField(source='name_eng', required=False)

    class Meta:
        model = Criteria
        fields = (
            'id', 'name', 'nameEng', 'minValue', 'maxValue', 'dataType',
            'status', 'classification', 'additionalClassification', 'unit',
            'dateModified'
        )
        read_only_fields = ('status', )
        extra_kwargs = {
            'name': {'required': False},
            'dateModified': {'source': 'date_modified'}
        }

    def validate(self, data):
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        if min_value and max_value and min_value > max_value:
            raise ValidationError('minValue can`t be greater than maxValue')
        return data

    def create(self, validated_data):
        """We must manually create Criteria instance
        because of nested serializers"""
        return Criteria.objects.create(**validated_data)


class CriteriaDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex')
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification'
    )
    unit = UnitSerializer()
    minValue = serializers.CharField(source='min_value', required=False)
    maxValue = serializers.CharField(source='max_value', required=False)
    dataType = serializers.ChoiceField(
        source='data_type', choices=DATATYPE_CHOICES
    )

    class Meta:
        model = Criteria
        fields = (
            'id', 'name', 'nameEng', 'minValue', 'maxValue', 'dataType',
            'dateModified', 'status', 'classification',
            'additionalClassification', 'unit'
        )
        extra_kwargs = {
            'nameEng': {'source': 'name_eng'},
            'dateModified': {'source': 'date_modified'}
        }


class CriteriaEditSerializer(serializers.ModelSerializer):
    minValue = serializers.FloatField(source='min_value', required=False)
    maxValue = serializers.FloatField(source='max_value', required=False)

    class Meta:
        model = Criteria
        fields = (
            'minValue', 'maxValue', 'name', 'nameEng', 'status'
        )
        extra_kwargs = {
            'nameEng': {'source': 'name_eng'},
        }

    def validate(self, data):
        # check if extra fields were passed
        if hasattr(self, 'initial_data'):
            unknown_keys = \
                set(self.initial_data.keys()) - set(self.fields.keys())
            if unknown_keys:
                raise ValidationError(
                    f'Got unknown fields for PATCH: {", ".join(unknown_keys)}'
                )

        min_value = data.get('min_value')
        max_value = data.get('max_value')
        if min_value and max_value and float(min_value) > float(max_value):
            raise ValidationError('minValue can`t be greater than maxValue')
        return data
