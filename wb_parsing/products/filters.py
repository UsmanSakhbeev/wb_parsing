import django_filters as df
from .models import Product


class ProductFilter(df.FilterSet):
    min_price = df.NumberFilter(field_name="sale_price", lookup_expr="gte")
    max_price = df.NumberFilter(field_name="sale_price", lookup_expr="lte")
    min_rating = df.NumberFilter(field_name="rating", lookup_expr="gte")
    max_rating = df.NumberFilter(field_name="rating", lookup_expr="lte")
    min_feedbacks = df.NumberFilter(field_name="feedbacks", lookup_expr="gte")

    class Meta:
        model = Product
        fields = ()
