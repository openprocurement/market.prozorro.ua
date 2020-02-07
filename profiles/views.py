from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response

from profiles import models as profile_models
from profiles import serializers as profile_serializers


class ProfileFilter(filters.FilterSet):
    classification_id = filters.CharFilter(lookup_expr='icontains')
    classification_description = filters.CharFilter(lookup_expr='icontains')
    autor = filters.CharFilter(lookup_expr='icontains')
    criteria_requirementGroups_requirements_relatedCriteria_id = filters.UUIDFilter(  # noqa
        field_name='criteria_requirementGroups_requirements_relatedCriteria_id',  # noqa
        method='filter_related_criteria'
    )

    class Meta:
        model = profile_models.Profile
        fields = (
            'classification_id', 'classification_description', 'autor',
            'criteria_requirementGroups_requirements_relatedCriteria_id',
            'status'
        )

    def filter_related_criteria(self, queryset, name, value):
        return queryset.filter(
            criteria__requirement_groups__requirements__related_criteria__id=value  # noqa
        ).distinct()


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = profile_models.Profile.objects.all()
    serializer_class = profile_serializers.ProfileCreateSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = ProfileFilter
    ordering_fields = '__all__'

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'create'):
            return profile_serializers.ProfileCreateSerializer
        else:
            return profile_serializers.ProfileEditSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = self.get_serializer(instance=instance)
        return Response(
            {
                'access': {
                    'token': instance.access_token.hex,
                    'owner': instance.author,
                },
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        data = request.data
        access_data = data.get('access')
        if access_data is None:
            return Response(
                {'detail': 'Missing access data'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            instance = self.get_object()
            if access_data.get('owner') != instance.author or \
                    access_data.get('token') != instance.access_token.hex:
                return Response(
                    {'detail': 'Wrong access data'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                serializer = self.get_serializer(
                    instance, data=data['data'], partial=True
                )
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)

                return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.status = 'hidden'
        instance.save()
        serializer = profile_serializers.ProfileCreateSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
