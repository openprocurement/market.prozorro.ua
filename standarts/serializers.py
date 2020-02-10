from django.core.validators import RegexValidator
from rest_framework import serializers

from standarts.validators import StandartsByReferenceValidator


class UnitSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=50)
    code = serializers.CharField(max_length=5, required=True)

    def validate(self, data):
        return StandartsByReferenceValidator(data).validate_unit()


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
