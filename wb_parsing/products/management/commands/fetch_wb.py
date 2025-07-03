# products/management/commands/fetch_wb.py
import time
import typing as _t
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.db.models import F
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from wb_parsing.products.models import Product

WB_URL = "https://search.wb.ru/exactmatch/ru/common/v4/search"
HEADERS = {
    # Реальный браузерный UA, чтобы не спалиться как бот
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    )
}
LIMIT = 100  # максимум, который даёт WB


class WBRequestError(Exception):
    """Прокидываем ненулевые ответы для ретраев."""


@retry(
    retry=retry_if_exception_type(WBRequestError),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
)
def _fetch_page(query: str, page: int, dest: int) -> list[dict]:
    """Получить одну страницу выдачи Wildberries Search."""
    params = {
        "appType": 1,
        "curr": "rub",
        "dest": dest,
        "query": query,
        "page": page,
        "limit": LIMIT,
        "sort": "popular",
        "resultset": "catalog",
        "spp": 0,
    }
    resp = requests.get(WB_URL, params=params, headers=HEADERS, timeout=20)
    if resp.status_code != 200:
        raise WBRequestError(f"WB status {resp.status_code}")
    data = resp.json()
    return data.get("data", {}).get("products", [])


def _extract_fields(raw: dict) -> dict:
    """Свести JSON-поле WB к нашей схеме Product."""
    return {
        "nm_id": raw["id"],
        "name": raw.get("name", "")[:512],
        "price": raw.get("priceU") or 0,
        "sale_price": raw.get("salePriceU") or raw.get("priceU") or 0,
        "rating": round(raw.get("rating", 0), 2),
        "feedbacks": raw.get("feedbacks") or 0,
    }


def _bulk_upsert(items: list[dict]) -> None:
    """Создаём новые и обновляем существующие товары пачкой."""
    if not items:
        return

    nm_ids = [i["nm_id"] for i in items]
    existing = Product.objects.filter(pk__in=nm_ids).values_list("pk", flat=True)
    existing_set = set(existing)

    to_create = [Product(**d) for d in items if d["nm_id"] not in existing_set]
    to_update = [d for d in items if d["nm_id"] in existing_set]

    with transaction.atomic():
        if to_create:
            Product.objects.bulk_create(to_create, batch_size=500)

        if to_update:
            # bulk_update требует уже существующие объекты;
            # вытаскиваем их и обновляем поля
            update_map = {d["nm_id"]: d for d in to_update}
            obj_list = Product.objects.filter(pk__in=update_map.keys())
            for obj in obj_list:
                data = update_map[obj.nm_id]
                obj.name = data["name"]
                obj.price = data["price"]
                obj.sale_price = data["sale_price"]
                obj.rating = data["rating"]
                obj.feedbacks = data["feedbacks"]
            Product.objects.bulk_update(
                obj_list,
                ["name", "price", "sale_price", "rating", "feedbacks"],
                batch_size=500,
            )


class Command(BaseCommand):
    help = "Скачать товары с Wildberries Search и сохранить/обновить в БД"

    def add_arguments(self, parser):
        parser.add_argument("--query", required=True, help="Поисковый запрос WB")
        parser.add_argument(
            "--pages", type=int, default=1, help="Сколько страниц парсить (1-∞)"
        )
        parser.add_argument(
            "--dest",
            type=int,
            default=-1257786,
            help="Логистический регион WB (-1257786=Москва/ЦФО)",
        )
        parser.add_argument(
            "--delay",
            type=float,
            default=1.0,
            help="Пауза между страницами, сек (анти-бан)",
        )

    def handle(self, *args, **opts):
        query: str = opts["query"]
        pages: int = opts["pages"]
        dest: int = opts["dest"]
        delay: float = opts["delay"]

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                f'📥 WB fetch: "{query}", pages={pages}, dest={dest}'
            )
        )

        total_items = 0
        for page in range(1, pages + 1):
            try:
                raw_products = _fetch_page(query, page, dest)
            except WBRequestError as exc:
                raise CommandError(f"WB request failed: {exc}") from exc

            products = [_extract_fields(p) for p in raw_products]
            _bulk_upsert(products)

            total_items += len(products)
            self.stdout.write(
                self.style.SUCCESS(f"  ✓ page {page}: {len(products)} items")
            )

            if page < pages:
                time.sleep(delay)

        self.stdout.write(
            self.style.SUCCESS(f"Done. {total_items} products processed.")
        )
