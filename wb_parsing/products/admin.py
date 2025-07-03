from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("nm_id", "name", "price_rub", "sale_price_rub",
                    "rating", "feedbacks", "updated_at")
    list_filter = ("rating",)
    search_fields = ("name", "nm_id")
