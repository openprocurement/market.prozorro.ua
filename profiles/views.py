from rest_framework import viewsets

from profiles import models as profile_models
from profiles import serializers as profile_serializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = profile_models.Profile.objects.all()
    serializer_class = profile_serializers.ProfileSerializer
