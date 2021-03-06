from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from criteria.models import DATATYPE_CHOICES, Criteria
from standarts.serializers import (
    ClassificationSerializer, AdditionalClassificationSerializer, 
    UnitSerializer
)


class MinMaxValueSerializer(serializers.Serializer):
    minValue = serializers.CharField(source='min_value', required=False)
    maxValue = serializers.CharField(source='max_value', required=False)

    def validate_minValue(self, value):
        try:
            float(value)
        except ValueError:
            raise ValidationError('Provide a valid number')
        return value

    def validate_maxValue(self, value):
        try:
            float(value)
        except ValueError:
            raise ValidationError('Provide a valid number')
        return value

    def validate(self, data):
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        if min_value and max_value and float(min_value) > float(max_value):
            raise ValidationError('minValue can`t be greater than maxValue')
        return data


class CriteriaListSerializer(
    serializers.ModelSerializer, MinMaxValueSerializer
):
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


class CriteriaCreateSerializer(
    serializers.ModelSerializer, MinMaxValueSerializer
):
    id = serializers.CharField(source='id.hex', read_only=True)
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification', allow_null=True
    )
    unit = UnitSerializer()
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

    def create(self, validated_data):
        """We must manually create Criteria instance
        because of nested serializers"""
        return Criteria.objects.create(**validated_data)


class CriteriaDetailSerializer(
    serializers.ModelSerializer, MinMaxValueSerializer
):
    id = serializers.CharField(source='id.hex')
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification'
    )
    unit = UnitSerializer()
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


class CriteriaEditSerializer(
    serializers.ModelSerializer, MinMaxValueSerializer
):
    id = serializers.CharField(source='id.hex', read_only=True)
    classification = ClassificationSerializer(read_only=True)
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification', read_only=True
    )
    unit = UnitSerializer(read_only=True)

    class Meta:
        model = Criteria
        fields = (
            'id', 'name', 'nameEng', 'minValue', 'maxValue', 'dataType',
            'dateModified', 'status', 'classification', 'unit',
            'additionalClassification',
        )
        read_only_fields = (
            'id', 'dataType', 'dateModified',
        )
        extra_kwargs = {
            'nameEng': {'source': 'name_eng'},
            'dateModified': {'source': 'date_modified'},
            'minValue': {'source': 'min_value'},
            'maxValue': {'source': 'max_value'},
            'dataType': {'source': 'data_type'},
        }

    def validate(self, data):
        # check if extra fields were passed
        if hasattr(self, 'initial_data'):
            writable_fields = set(
                key for key, value in self.fields.items()
                if not value.read_only
            )
            unknown_keys = set(self.initial_data.keys()) - writable_fields
            if unknown_keys:
                raise ValidationError(
                    f'Got unknown fields for PATCH: {", ".join(unknown_keys)}'
                )

        return super().validate(data)
