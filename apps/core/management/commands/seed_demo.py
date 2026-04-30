"""Seed the database with 5 demo rows per model.

Run::

    python manage.py seed_demo            # add only if tables are empty
    python manage.py seed_demo --flush    # delete existing rows first
"""
from datetime import date
from io import BytesIO

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFont

from apps.core.models import Category, PortfolioProject, Review, ServiceType


CATEGORIES = [
    {
        "name_uz": "Landing",
        "name_ru": "Лендинг",
        "name_en": "Landing",
    },
    {
        "name_uz": "Onlayn do'kon",
        "name_ru": "Интернет-магазин",
        "name_en": "E-commerce",
    },
    {
        "name_uz": "Korporativ sayt",
        "name_ru": "Корпоративный сайт",
        "name_en": "Corporate website",
    },
    {
        "name_uz": "SMM kampaniya",
        "name_ru": "SMM-кампания",
        "name_en": "SMM campaign",
    },
    {
        "name_uz": "Mobil ilova",
        "name_ru": "Мобильное приложение",
        "name_en": "Mobile app",
    },
]


SERVICE_TYPES = [
    {
        "name_uz": "Veb ishlab chiqish",
        "name_ru": "Веб-разработка",
        "name_en": "Web Development",
        "description_uz": "Tezkor, mobil mos va SEO-ga tayyor saytlar.",
        "description_ru": "Быстрые, адаптивные и SEO-готовые сайты.",
        "description_en": "Fast, mobile-friendly, SEO-ready websites.",
        "what_we_do_uz": ["Landing sahifalar", "Onlayn do'konlar", "Admin paneli", "Integratsiyalar"],
        "what_we_do_ru": ["Лендинги", "Интернет-магазины", "Админ-панели", "Интеграции"],
        "what_we_do_en": ["Landing pages", "E-commerce", "Admin dashboards", "Integrations"],
    },
    {
        "name_uz": "SMM",
        "name_ru": "SMM",
        "name_en": "SMM",
        "description_uz": "Ijtimoiy tarmoqlarda brendni rivojlantirish.",
        "description_ru": "Развитие бренда в социальных сетях.",
        "description_en": "Growing your brand on social media.",
        "what_we_do_uz": ["Kontent rejasi", "Dizayn", "Reklama", "Auditoriya tahlili"],
        "what_we_do_ru": ["Контент-план", "Дизайн", "Реклама", "Анализ аудитории"],
        "what_we_do_en": ["Content plan", "Design", "Ads", "Audience analysis"],
    },
    {
        "name_uz": "UI/UX dizayn",
        "name_ru": "UI/UX-дизайн",
        "name_en": "UI/UX Design",
        "description_uz": "Foydalanuvchi tajribasiga asoslangan zamonaviy interfeyslar.",
        "description_ru": "Современные интерфейсы на основе UX-исследований.",
        "description_en": "Modern interfaces grounded in UX research.",
        "what_we_do_uz": ["Wireframe", "Prototip", "Dizayn tizimi", "Foydalanuvchi testi"],
        "what_we_do_ru": ["Wireframes", "Прототипы", "Дизайн-система", "Юзабилити-тесты"],
        "what_we_do_en": ["Wireframes", "Prototypes", "Design system", "Usability testing"],
    },
    {
        "name_uz": "SEO",
        "name_ru": "SEO",
        "name_en": "SEO",
        "description_uz": "Qidiruv tizimlarida yuqori o'rinlarga chiqish.",
        "description_ru": "Вывод в топ поисковых систем.",
        "description_en": "Climbing search-engine rankings.",
        "what_we_do_uz": ["Texnik audit", "Kalit so'zlar", "Tashqi havolalar", "Hisobotlar"],
        "what_we_do_ru": ["Технический аудит", "Ключевые слова", "Линкбилдинг", "Отчёты"],
        "what_we_do_en": ["Technical audit", "Keywords", "Link building", "Reporting"],
    },
    {
        "name_uz": "Brending",
        "name_ru": "Брендинг",
        "name_en": "Branding",
        "description_uz": "Brendning yagona vizual tilini yaratish.",
        "description_ru": "Создание единого визуального языка бренда.",
        "description_en": "Crafting a coherent visual brand language.",
        "what_we_do_uz": ["Logotip", "Brendbuk", "Reklama materiallari", "Qadoqlash"],
        "what_we_do_ru": ["Логотип", "Брендбук", "Реклама", "Упаковка"],
        "what_we_do_en": ["Logo", "Brand book", "Marketing assets", "Packaging"],
    },
]


# (category_index, service_type_indices, payload)
PROJECTS = [
    (
        0,  # Landing
        [0, 2],  # Web Development + UI/UX
        {
            "name_uz": "Acme Landing",
            "name_ru": "Лендинг Acme",
            "name_en": "Acme Landing",
            "description_uz": "Konversiyaga yo'naltirilgan tezkor landing sahifa.",
            "description_ru": "Быстрый лендинг с фокусом на конверсию.",
            "description_en": "Fast, conversion-focused landing page.",
            "tasks_uz": ["UI/UX dizayn", "Frontend", "Animatsiyalar", "Tahlil sozlamalari"],
            "tasks_ru": ["UI/UX-дизайн", "Фронтенд", "Анимации", "Аналитика"],
            "tasks_en": ["UI/UX design", "Frontend", "Motion", "Analytics setup"],
            "website_url": "https://acme.example",
            "date": date(2025, 9, 15),
            "color": (52, 152, 219),
        },
    ),
    (
        1,  # E-commerce
        [0, 2, 3],  # Web Dev + UI/UX + SEO
        {
            "name_uz": "Bozor Online",
            "name_ru": "Bozor Online",
            "name_en": "Bozor Online",
            "description_uz": "1500+ mahsulotli marketpleys; to'lov va yetkazib berish bilan.",
            "description_ru": "Маркетплейс на 1500+ товаров с оплатой и доставкой.",
            "description_en": "Marketplace with 1500+ products, payments and shipping.",
            "tasks_uz": ["Katalog", "Savat", "To'lov integratsiyasi", "Admin paneli"],
            "tasks_ru": ["Каталог", "Корзина", "Платёжная интеграция", "Админ-панель"],
            "tasks_en": ["Catalog", "Cart", "Payment integration", "Admin dashboard"],
            "website_url": "https://bozor.example",
            "date": date(2025, 7, 2),
            "color": (231, 76, 60),
        },
    ),
    (
        2,  # Corporate
        [0, 4],  # Web Dev + Branding
        {
            "name_uz": "Sharq Bank korporativ sayti",
            "name_ru": "Корпоративный сайт Sharq Bank",
            "name_en": "Sharq Bank corporate site",
            "description_uz": "Bank uchun ko'p tilli korporativ sayt va xabarlar tizimi.",
            "description_ru": "Многоязычный корпоративный сайт банка с новостным разделом.",
            "description_en": "Multilingual corporate website with newsroom for the bank.",
            "tasks_uz": ["Axborot arxitekturasi", "CMS", "Xabarlar bo'limi", "Mobil moslashuv"],
            "tasks_ru": ["Информационная архитектура", "CMS", "Новостной раздел", "Адаптивность"],
            "tasks_en": ["Information architecture", "CMS", "Newsroom", "Responsive design"],
            "website_url": "https://sharq.example",
            "date": date(2025, 5, 20),
            "color": (39, 174, 96),
        },
    ),
    (
        3,  # SMM
        [1, 4],  # SMM + Branding
        {
            "name_uz": "ChoyXona SMM",
            "name_ru": "SMM для ChoyXona",
            "name_en": "ChoyXona SMM",
            "description_uz": "Restoran tarmog'i uchun 3 oylik SMM kampaniyasi.",
            "description_ru": "3-месячная SMM-кампания для сети ресторанов.",
            "description_en": "3-month SMM campaign for a restaurant chain.",
            "tasks_uz": ["Kontent rejasi", "Foto-video", "Reklama", "Tahlil"],
            "tasks_ru": ["Контент-план", "Фото и видео", "Реклама", "Аналитика"],
            "tasks_en": ["Content plan", "Photo & video", "Ads", "Analytics"],
            "website_url": "",
            "date": date(2025, 3, 10),
            "color": (243, 156, 18),
        },
    ),
    (
        4,  # Mobile
        [0, 2],  # Web Dev + UI/UX
        {
            "name_uz": "Taxi Plus mobil ilovasi",
            "name_ru": "Мобильное приложение Taxi Plus",
            "name_en": "Taxi Plus mobile app",
            "description_uz": "iOS va Android uchun taksi buyurtma berish ilovasi.",
            "description_ru": "Приложение заказа такси для iOS и Android.",
            "description_en": "Taxi booking app for iOS and Android.",
            "tasks_uz": ["UI/UX", "Geolokatsiya", "Push xabarlar", "To'lovlar"],
            "tasks_ru": ["UI/UX", "Геолокация", "Push-уведомления", "Платежи"],
            "tasks_en": ["UI/UX", "Geolocation", "Push notifications", "Payments"],
            "website_url": "https://taxiplus.example",
            "date": date(2024, 12, 1),
            "color": (155, 89, 182),
        },
    ),
]


# (project_index, payload)
REVIEWS = [
    (
        0,
        {
            "name_uz": "Jasur Aliyev",
            "name_ru": "Джасур Алиев",
            "name_en": "Jasur Aliyev",
            "comment_uz": "Tezkor va sifatli ish. Konversiya 2 baravar oshdi.",
            "comment_ru": "Быстро и качественно. Конверсия выросла в 2 раза.",
            "comment_en": "Fast and high quality. Conversion doubled.",
        },
    ),
    (
        1,
        {
            "name_uz": "Madina Karimova",
            "name_ru": "Мадина Каримова",
            "name_en": "Madina Karimova",
            "comment_uz": "Marketpleys belgilangan muddatda topshirildi. Komandaga rahmat!",
            "comment_ru": "Маркетплейс сдан в срок. Спасибо команде!",
            "comment_en": "Marketplace delivered on schedule. Thanks to the team!",
        },
    ),
    (
        2,
        {
            "name_uz": "Bekzod Toshmatov",
            "name_ru": "Бекзод Тошматов",
            "name_en": "Bekzod Toshmatov",
            "comment_uz": "Korporativ sayt bizning brendimiz darajasiga loyiq bo'ldi.",
            "comment_ru": "Корпоративный сайт получился на уровне нашего бренда.",
            "comment_en": "The corporate site lives up to our brand.",
        },
    ),
    (
        3,
        {
            "name_uz": "Nilufar Yusupova",
            "name_ru": "Нилуфар Юсупова",
            "name_en": "Nilufar Yusupova",
            "comment_uz": "Obunachilar 3 oyda 5 baravar ko'paydi. Professional yondashuv.",
            "comment_ru": "Подписчики за 3 месяца выросли в 5 раз. Профессионально.",
            "comment_en": "Followers grew 5× in 3 months. Truly professional.",
        },
    ),
    (
        4,
        {
            "name_uz": "Rustam Sodiqov",
            "name_ru": "Рустам Содиков",
            "name_en": "Rustam Sodiqov",
            "comment_uz": "Ilovamiz App Store va Google Play'da yaxshi reytinglarga erishdi.",
            "comment_ru": "Приложение получило отличные оценки в App Store и Google Play.",
            "comment_en": "Our app earned strong ratings on App Store and Google Play.",
        },
    ),
]


def make_placeholder_image(label: str, color: tuple[int, int, int]) -> ContentFile:
    """Generate a simple solid-color PNG with a centered label."""
    width, height = 800, 500
    img = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.load_default()
    except Exception:  # pragma: no cover
        font = None
    bbox = draw.textbbox((0, 0), label, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    draw.text(
        ((width - text_w) / 2, (height - text_h) / 2),
        label,
        fill=(255, 255, 255),
        font=font,
    )
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return ContentFile(buffer.getvalue(), name=f"{label.lower().replace(' ', '_')}.png")


class Command(BaseCommand):
    help = "Seed the database with 5 demo rows for each model."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing rows before inserting demo data.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write(self.style.WARNING("Deleting existing rows…"))
            Review.objects.all().delete()
            PortfolioProject.objects.all().delete()
            ServiceType.objects.all().delete()
            Category.objects.all().delete()

        if Category.objects.exists() or ServiceType.objects.exists() or PortfolioProject.objects.exists():
            self.stdout.write(self.style.WARNING(
                "Database already has data. Re-run with --flush to reset."
            ))
            return

        self.stdout.write("Creating categories…")
        categories = [Category.objects.create(**c) for c in CATEGORIES]

        self.stdout.write("Creating service types…")
        services = [ServiceType.objects.create(**s) for s in SERVICE_TYPES]

        self.stdout.write("Creating portfolio projects…")
        projects = []
        for cat_idx, svc_idxs, payload in PROJECTS:
            color = payload.pop("color")
            image = make_placeholder_image(payload["name_en"], color)
            project = PortfolioProject.objects.create(
                category=categories[cat_idx],
                image=image,
                **payload,
            )
            project.service_types.set([services[i] for i in svc_idxs])
            projects.append(project)

        self.stdout.write("Creating reviews…")
        for project_idx, payload in REVIEWS:
            Review.objects.create(project=projects[project_idx], **payload)

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(categories)} categories, {len(services)} service types, "
            f"{len(projects)} projects, {len(REVIEWS)} reviews."
        ))
