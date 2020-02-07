from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from profiles.models import (
    ProfileCriteria, Requirement, RequirementGroup, CURRENCY_CHOICES, Profile
)
from criteria.models import Criteria
from standarts.serializers import (
    ClassificationSerializer, UnitSerializer,
    AdditionalClassificationSerializer
)


class RequirementSerializer(serializers.ModelSerializer):
    ONE_VALUE_AT_A_TIME_FIELDS = set(
        ('expected_value', 'min_value', 'max_value')
    )

    relatedCriteria_id = serializers.UUIDField(source='related_criteria_id')
    unit = UnitSerializer(read_only=True)
    expectedValue = serializers.CharField(
        required=False, source='expected_value', allow_null=True
    )
    minValue = serializers.CharField(
        required=False, source='min_value', allow_null=True
    )
    maxValue = serializers.CharField(
        required=False, source='max_value', allow_null=True
    )

    class Meta:
        model = Requirement
        exclude = (
            'related_criteria', 'min_value', 'max_value', 'expected_value',
            'id'
        )

    def validate(self, data):
        error_msg = (
            'You must pass exact one of following keys: '
            '"expectedValue", "minValue", "maxValue"'
        )

        # dict for storing passed values for expectedValue, minValue, maxValue
        value_dict = {}
        for key, value in data.items():
            if key in self.ONE_VALUE_AT_A_TIME_FIELDS:
                if value and value_dict:
                    raise ValidationError(error_msg)
                else:
                    value_dict[key] = value
        if not value_dict:
            raise ValidationError(error_msg)

        self.validate_value(value_dict)
        return data

    def validate_value(self, value_dict):
        key, value = next(iter(value_dict.items()))
        data_type = self.criteria.data_type
        error_dict = {key: f'You must provide a valid {data_type} value'}

        if data_type == 'string':
            if not isinstance(value, str):
                raise ValidationError(error_dict)
        elif data_type == 'boolean':
            if value not in ('true', 'false'):
                raise ValidationError(error_dict)
        elif data_type == 'integer':
            try:
                int(value)
            except ValueError:
                raise ValidationError(error_dict)
        elif data_type == 'number':
            try:
                float(value)
            except ValueError:
                raise ValidationError(error_dict)

    def validate_relatedCriteria_id(self, value):
        try:
            self.criteria = Criteria.objects.get(id=value, status='active')
        except Criteria.DoesNotExist:
            raise ValidationError(
                {'relatedCriteria_id': 'No active Criteria found by passed id'}
            )
        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['relatedCriteria_id'] = instance.related_criteria.id.hex
        return data


class RequirementGroupSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex', required=False)
    requirements = RequirementSerializer(many=True)

    class Meta:
        model = RequirementGroup
        exclude = ()


class ProfileCriteriaSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex', required=False)
    requirementGroups = RequirementGroupSerializer(
        source='requirement_groups', many=True
    )

    class Meta:
        model = ProfileCriteria
        exclude = ('requirement_groups', )


class ProfileImageSerializer(serializers.Serializer):
    sizes = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )
    url = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )


class ValueSerializer(serializers.Serializer):
    valueAddedTaxIncluded = serializers.BooleanField(
        source='value_added_tax_included'
    )
    amount = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False
    )
    currency = serializers.ChoiceField(choices=CURRENCY_CHOICES)


class ProfileBaseSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='id.hex', read_only=True)
    unit = UnitSerializer()
    value = ValueSerializer()
    criteria = ProfileCriteriaSerializer(many=True)
    images = ProfileImageSerializer(many=True)
    dateModified = serializers.DateTimeField(
        source='date_modified', read_only=True
    )

    class Meta:
        model = Profile
        exclude = (
            'classification_id', 'classification_description', 'unit_code',
            'unit_name', 'value_amount', 'additional_classification',
            'value_currency', 'value_value_added_tax_included', 'access_token',
            'date_modified'
        )
        read_only_fields = ('status', 'author', )

    def _create_requirement(self, requirement_data):
        criteria = Criteria.objects.get(
            id=requirement_data.pop('related_criteria_id'),
            status='active'
        )
        requirement_data['related_criteria'] = criteria
        return Requirement.objects.create(
            **requirement_data
        )

    def _create_requirement_group(self, requirement_group_data):
        requirements_list = requirement_group_data.pop('requirements', [])
        group_id = requirement_group_data.pop('id', {}).get('hex')
        if group_id:
            try:
                requirement_group = RequirementGroup.objects.get(
                    id=group_id
                )
            except RequirementGroup.DoesNotExist:
                raise ValidationError({
                    'criteria': [
                        {'requirementGroups': [{
                            'id': f'RequirementGroup with id {group_id} not found'
                        }]}
                    ]
                })

            for attr, value in requirement_group_data.items():
                setattr(requirement_group, attr, value)
            requirement_group.save()
        else:
            requirement_group = RequirementGroup.objects.create(
                **requirement_group_data
            )

        if requirements_list:
            self._set_requirements_to_requirement_group(
                requirements_list, requirement_group
            )
        return requirement_group

    def _set_requirements_to_requirement_group(
        self, requirements_list_data, requirement_group
    ):
        requirement_instances = []
        for requirement_data in requirements_list_data:
            requirement = self._create_requirement(requirement_data)
            requirement_instances.append(requirement)
        requirement_group.requirements.set(requirement_instances)

    def _create_criteria(self, criteria_data):
        requirement_group_list = criteria_data.pop('requirement_groups', [])
        profile_criteria = ProfileCriteria.objects.create(**criteria_data)
        for requirement_group_data in requirement_group_list:
            requirement_group = self._create_requirement_group(
                requirement_group_data
            )
            profile_criteria.requirement_groups.add(requirement_group)
        return profile_criteria


class ProfileCreateSerializer(ProfileBaseSerializer):
    classification = ClassificationSerializer()
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification',
        allow_null=True, many=True
    )

    def create(self, data):
        criteria_data_list = data.pop('criteria')
        data['author'] = self.context['request'].user.username
        instance = Profile.objects.create(**data)

        criteria_instances = self._create_requirement_criteria(
            criteria_data_list
        )
        instance.criteria.set(criteria_instances)
        return instance

    def _create_requirement_criteria(self, criteria_data_list):
        criteria_instances = []
        for criteria_data in criteria_data_list:
            profile_criteria = self._create_criteria(criteria_data)

            criteria_instances.append(profile_criteria)
        return criteria_instances


class ProfileEditSerializer(ProfileBaseSerializer):
    classification = ClassificationSerializer(read_only=True)
    additionalClassification = AdditionalClassificationSerializer(
        required=False, source='additional_classification',
        allow_null=True, many=True, read_only=True
    )

    def update(self, instance, validated_data):
        criteria_data_list = validated_data.pop('criteria', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        criteria_instances = self._update_requirement_criteria(
            criteria_data_list, instance
        )
        instance.criteria.set(criteria_instances)
        return instance

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

    def _update_requirement_criteria(self, criteria_data_list, instance):
        criteria_instances = []
        for criteria_data in criteria_data_list:
            criteria_id = criteria_data.pop('id', {}).get('hex')

            if criteria_id:
                # editing existing ProfileCriteria
                try:
                    profile_criteria = ProfileCriteria.objects.get(
                        id=criteria_id
                    )
                except ProfileCriteria.DoesNotExist:
                    raise ValidationError({
                        'criteria': [
                            {'id': f'Criteria with id {criteria_id} not found'}
                        ]
                    })
                # setting new field values for ProfileCriteria
                requirement_group_list = criteria_data.pop('requirement_groups', [])
                for attr, value in criteria_data.items():
                    setattr(profile_criteria, attr, value)
                profile_criteria.save()

                requirement_group_instances = []
                for requirement_group_data in requirement_group_list:
                    requirement_group_id = requirement_group_data.pop('id', {}).get('hex')

                    if requirement_group_id:
                        # editing existing RequirementGroup
                        try:
                            requirement_group = RequirementGroup.objects.get(
                                id=requirement_group_id
                            )
                        except RequirementGroup.DoesNotExist:
                            raise ValidationError({
                                'criteria': [
                                    {'requirementGroups': [{
                                        'id': f'RequirementGroup with id {requirement_group_id} not found'
                                    }]}
                                ]
                            })

                        requirements_list = requirement_group_data.pop('requirements', [])
                        # setting new field values for RequirementGroup
                        for attr, value in requirement_group_data.items():
                            setattr(requirement_group, attr, value)
                        requirement_group.save()

                        if requirements_list:
                            self._set_requirements_to_requirement_group(
                                requirements_list, requirement_group
                            )
                    else:
                        # creating RequirementGroup
                        requirement_group = self._create_requirement_group(requirement_group_data)
                    requirement_group_instances.append(requirement_group)

                profile_criteria.requirement_groups.set(requirement_group_instances)
            else:
                # creating ProfileCriteria
                profile_criteria = self._create_criteria(criteria_data)
            criteria_instances.append(profile_criteria)
        return criteria_instances
