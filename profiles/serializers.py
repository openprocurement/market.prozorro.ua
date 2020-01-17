from rest_framework import serializers

from profiles import models as profile_models


class ProfileCriteriaRequirementGroupRequirementSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = profile_models.ProfileCriteriaRequirementGroupRequirement
        exclude = ()


class ProfileCriteriaRequirementGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.ProfileCriteriaRequirementGroup
        exclude = ()


class ProfileCriteriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.ProfileCriteria
        exclude = ()


class ProfileImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.ProfileImage
        exclude = ()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = profile_models.Profile
        exclude = ()
