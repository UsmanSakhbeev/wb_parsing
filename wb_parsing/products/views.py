from rest_framework import mixins, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .models import Product
from .serializers import ProductSerializer
from .filters import ProductFilter


class ProductViewSet(mixins.ListModelMixin,
                     mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = ProductFilter
    ordering_fields = ("price", "rating", "feedbacks", "name")
    ordering = ("-rating",)
