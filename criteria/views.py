from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from criteria import serializers as criteria_serializers
from criteria.models import Criteria, STATUS_CHOICES
from criteria.permissions import IsAdminOrReadOnlyPermission


class CriteriaStatusFilter(filters.CharFilter):
    """CharFilter class for filtering Criteria by status"""
    def filter(self, qs, value):
        if value == '':
            return qs.filter(status=STATUS_CHOICES[0][0])
        elif value == 'all':
            return qs
        else:
            return qs.filter(status=value)


class CriteriaFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    classification_id = filters.CharFilter(lookup_expr='icontains')
    additionalClassification_id = filters.CharFilter(
        field_name='additional_classification_id', lookup_expr='icontains'
    )
    unit_code = filters.CharFilter(lookup_expr='icontains')
    status = CriteriaStatusFilter()
    dateModified_from = filters.IsoDateTimeFilter(
        field_name='date_modified', lookup_expr='gte'
    )
    dateModified_to = filters.IsoDateTimeFilter(
        field_name='date_modified', lookup_expr='lte'
    )

    class Meta:
        model = Criteria
        fields = (
            'name', 'status', 'classification_id',
            'additional_classification_id', 'unit_code'
        )


class CriteriaViewset(ModelViewSet):
    SERIALIZERS_MAPPING = {
        'list': criteria_serializers.CriteriaListSerializer,
        'create': criteria_serializers.CriteriaCreateSerializer,
        'retrieve': criteria_serializers.CriteriaDetailSerializer,
        'partial_update': criteria_serializers.CriteriaEditSerializer,
    }

    http_method_names = (
        'get', 'post', 'patch', 'delete', 'head', 'options', 'trace'
    )

    queryset = Criteria.objects.all()
    serializer_class = criteria_serializers.CriteriaListSerializer
    permission_classes = (IsAuthenticated, IsAdminOrReadOnlyPermission)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = CriteriaFilter
    ordering_fields = '__all__'

    def get_serializer_class(self):
        return self.SERIALIZERS_MAPPING.get(self.action, self.serializer_class)

    def get_object(self):
        """
        Returns the object the view is displaying.
        """
        queryset = self.get_queryset()

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = generics.get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def destroy(self, request, *args, **kwargs):
        """Instead of deleting Criteria we set archive = True"""
        instance = self.get_object()
        instance.status = 'retired'
        instance.save()
        serializer = criteria_serializers.CriteriaDetailSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)
