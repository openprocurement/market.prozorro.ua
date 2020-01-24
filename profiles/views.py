from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from profiles import models as profile_models
from profiles import serializers as profile_serializers


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = profile_models.Profile.objects.all()
    serializer_class = profile_serializers.ProfileCreateSerializer

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve', 'create'):
            return profile_serializers.ProfileCreateSerializer
        else:
            return profile_serializers.ProfileEditSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            {
                'access': {
                    'token': instance.access_token.hex,
                    'owner': instance.author,
                },
                'data': serializer.data
            },
            status=status.HTTP_201_CREATED, headers=headers
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
