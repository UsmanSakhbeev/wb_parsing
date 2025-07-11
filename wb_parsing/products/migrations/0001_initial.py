# Generated by Django 5.2.3 on 2025-06-26 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('nm_id', models.BigIntegerField(primary_key=True, serialize=False, verbose_name='WB nmId')),
                ('name', models.CharField(max_length=512, verbose_name='Название')),
                ('price', models.PositiveIntegerField(verbose_name='Цена без скидки (коп.)')),
                ('sale_price', models.PositiveIntegerField(verbose_name='Цена со скидкой (коп.)')),
                ('rating', models.DecimalField(decimal_places=2, max_digits=3, verbose_name='Рейтинг 0-5')),
                ('feedbacks', models.PositiveIntegerField(verbose_name='Кол-во отзывов')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Обновлено')),
            ],
            options={
                'verbose_name': 'Товар WB',
                'verbose_name_plural': 'Товары WB',
                'ordering': ['-updated_at'],
                'indexes': [models.Index(fields=['price'], name='products_pr_price_9b1a5f_idx'), models.Index(fields=['sale_price'], name='products_pr_sale_pr_78511c_idx'), models.Index(fields=['rating'], name='products_pr_rating_c3ba71_idx'), models.Index(fields=['feedbacks'], name='products_pr_feedbac_4ac9cf_idx')],
            },
        ),
    ]
