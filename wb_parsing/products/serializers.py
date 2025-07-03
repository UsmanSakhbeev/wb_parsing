from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """Плоский сериализатор без вложенных структур."""

    class Meta:
        model = Product
        fields = (
            "nm_id",
            "name",
            "price_rub",
            "sale_price_rub",
            "rating",
            "feedbacks",
        )
        read_only_fields = fields
