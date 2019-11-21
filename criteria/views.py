from django_filters import rest_framework as filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet

from criteria import serializers as criteria_serializers
from criteria.models import Criteria


class CriteriaFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    classification_id = filters.CharFilter(lookup_expr='icontains')
    additional_classification_id = filters.CharFilter(lookup_expr='icontains')
    unit_code = filters.CharFilter(lookup_expr='icontains')
    archive = filters.BooleanFilter()

    class Meta:
        model = Criteria
        fields = (
            'name', 'archive', 'classification_id',
            'additional_classification_id', 'unit_code'
        )


class CriteriaViewset(ModelViewSet):
    SERIALIZERS_MAPPING = {
        'list': criteria_serializers.CriteriaListSerializer,
        'create': criteria_serializers.CriteriaCreateSerializer,
        'retrieve': criteria_serializers.CriteriaDetailSerializer,
    }

    queryset = Criteria.objects.all()
    serializer_class = criteria_serializers.CriteriaListSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = CriteriaFilter

    def get_serializer_class(self):
        return self.SERIALIZERS_MAPPING.get(self.action, self.serializer_class)
