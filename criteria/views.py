from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.viewsets import ModelViewSet

from criteria import serializers as criteria_serializers
from criteria.models import Criteria


class CriteriaFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    classification_id = filters.CharFilter(lookup_expr='icontains')
    additional_classification_id = filters.CharFilter(lookup_expr='icontains')
    unit_code = filters.CharFilter(lookup_expr='icontains')
    status = filters.CharFilter(lookup_expr='icontains')
    date_modified_from = filters.IsoDateTimeFilter(
        field_name='date_modified', lookup_expr=('gte')
    )
    date_modified_to = filters.IsoDateTimeFilter(
        field_name='date_modified', lookup_expr=('lte')
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
        'update': criteria_serializers.CriteriaEditSerializer,
    }

    http_method_names = (
        'get', 'post', 'patch', 'delete', 'head', 'options', 'trace'
    )

    queryset = Criteria.objects.all()
    serializer_class = criteria_serializers.CriteriaListSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    filterset_class = CriteriaFilter
    ordering_fields = '__all__'

    def get_serializer_class(self):
        return self.SERIALIZERS_MAPPING.get(self.action, self.serializer_class)
