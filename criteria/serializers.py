import json

from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from criteria.models import DATATYPE_CHOICES, Criteria


class UnitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=5)


class BaseClassificationSerializer(serializers.Serializer):
    id = serializers.CharField(
        max_length=10,
        validators=(
            RegexValidator(regex=r'^\d{8}-\d$'),
        )
    )
    description = serializers.CharField(max_length=255)


class ClassificationSerializer(BaseClassificationSerializer):
    def to_representation(self, data):
        data['scheme'] = 'ДК021'
        return data


class AdditionalClassificationSerializer(BaseClassificationSerializer):
    scheme = serializers.CharField(max_length=10)


class CriteriaListSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex')
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        source='additional_classification'
    )
    unit = UnitSerializer()

    class Meta:
        model = Criteria
        fields = (
            'id', 'name', 'classification', 'additionalClassification',
            'unit', 'archive'
        )


class CriteriaCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex', read_only=True)
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification'
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
            'archive', 'classification', 'additionalClassification', 'unit',
            'dateModified'
        )
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
            'dateModified', 'archive', 'classification',
            'additionalClassification', 'unit'
        )
        extra_kwargs = {
            'nameEng': {'source': 'name_eng'},
            'dateModified': {'source': 'date_modified'}
        }
