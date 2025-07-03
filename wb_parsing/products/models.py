from django.db import models


class Product(models.Model):
    nm_id = models.BigIntegerField(
        primary_key=True,
        verbose_name="WB nmId",
    )
    name = models.CharField(
        max_length=512,
        verbose_name="Название",
    )
    price = models.PositiveIntegerField(
        verbose_name="Цена без скидки (коп.)",
    )
    sale_price = models.PositiveIntegerField(
        verbose_name="Цена со скидкой (коп.)",
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name="Рейтинг 0-5",
    )
    feedbacks = models.PositiveIntegerField(
        verbose_name="Кол-во отзывов",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    @property
    def price_rub(self) -> float:
        return self.price / 100

    @property
    def sale_price_rub(self) -> float:
        return self.sale_price / 100

    class Meta:
        verbose_name = "Товар WB"
        verbose_name_plural = "Товары WB"
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["price"]),
            models.Index(fields=["sale_price"]),
            models.Index(fields=["rating"]),
            models.Index(fields=["feedbacks"]),
        ]

    def __str__(self) -> str:
        return f"{self.name[:60]} … ({self.nm_id})"
