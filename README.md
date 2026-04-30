# Senior — Agency Backend

Django + DRF backend for the **Senior** agency website (SMM and Web Development).

## Features

- Full CRUD for `Category`, `ServiceType`, `PortfolioProject`, `Review`
- **Database-level i18n** in three languages — Uzbek (default), Russian, English
- **Live `/statistics/` endpoint** — auto-calculated from the DB on every request, nothing persisted
- Class-based ViewSets, clean app layout (`models / serializers / filters / views / urls / i18n`)
- Filtering (category, service type, date range), search, pagination
- Image uploads (`MEDIA_URL` / `MEDIA_ROOT`)
- Swagger UI + Redoc via `drf-yasg`
- CORS-ready, environment-driven configuration

## Multi-language

Every translatable field is stored as three columns: `<field>_uz`, `<field>_ru`,
`<field>_en`. Uzbek is the primary language and is **required**; Russian and
English are optional and fall back to Uzbek on read.

Language switching via query param:

```
GET /api/v1/projects/?lang=uz   (default)
GET /api/v1/projects/?lang=ru
GET /api/v1/projects/?lang=en
```

Read responses include both the resolved alias (`name`, `description`,
`tasks`, `comment`, `what_we_do`) and all per-language columns:

```json
{
  "id": 1,
  "name": "Loyiha nomi",
  "description": "Tavsif...",
  "tasks": ["UI/UX", "Frontend"],
  "name_uz": "Loyiha nomi", "name_ru": "Название", "name_en": "Project name",
  "description_uz": "...", "description_ru": "...", "description_en": "...",
  "tasks_uz": [...], "tasks_ru": [...], "tasks_en": [...]
}
```

Search and ordering operate on Uzbek (primary) columns only.
Filtering by `category_name` / `service_type_name` matches the Uzbek name.

## Quickstart

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- Swagger UI: <http://localhost:8000/swagger/>
- Redoc:      <http://localhost:8000/redoc/>
- Admin:      <http://localhost:8000/admin/>
- API root:   <http://localhost:8000/api/v1/>

## Endpoints

| Resource          | URL                              | Methods                |
| ----------------- | -------------------------------- | ---------------------- |
| Statistics (live) | `/api/v1/statistics/`            | GET                    |
| Categories        | `/api/v1/categories/`            | GET, POST, PUT, PATCH, DELETE |
| Service Types     | `/api/v1/service-types/`         | GET, POST, PUT, PATCH, DELETE |
| Projects          | `/api/v1/projects/`              | GET, POST, PUT, PATCH, DELETE |
| Project reviews   | `/api/v1/projects/{id}/reviews/` | GET                    |
| Reviews           | `/api/v1/reviews/`               | GET, POST, PUT, PATCH, DELETE |

### Live statistics response

```json
GET /api/v1/statistics/
{
  "total_products": 12,
  "total_service_types": 5
}
```

### Filtering / search examples

```
GET /api/v1/projects/?category=3
GET /api/v1/projects/?category_name=Landing
GET /api/v1/projects/?service_type=2
GET /api/v1/projects/?service_type_name=SMM
GET /api/v1/projects/?search=ecommerce
GET /api/v1/projects/?date_from=2025-01-01&date_to=2025-12-31
GET /api/v1/projects/?ordering=-date
```

## Example requests

### Create a Category

```bash
curl -X POST http://localhost:8000/api/v1/categories/ \
  -H "Content-Type: application/json" \
  -d '{
    "name_uz": "Landing",
    "name_ru": "Лендинг",
    "name_en": "Landing"
  }'
```

### Create a ServiceType

```bash
curl -X POST http://localhost:8000/api/v1/service-types/ \
  -H "Content-Type: application/json" \
  -d '{
    "name_uz": "Veb-ishlab chiqish",
    "name_ru": "Веб-разработка",
    "name_en": "Web Development",
    "description_uz": "Saytlar va veb-ilovalar.",
    "description_ru": "Сайты и веб-приложения.",
    "description_en": "Custom websites and web apps.",
    "what_we_do_uz": ["Landing", "E-commerce", "Admin paneli"],
    "what_we_do_ru": ["Лендинг", "E-commerce", "Админ-панель"],
    "what_we_do_en": ["Landing", "E-commerce", "Admin dashboards"]
  }'
```

### Create a PortfolioProject (multipart, image + FK + multi-select)

```bash
curl -X POST http://localhost:8000/api/v1/projects/ \
  -F "name=Acme Landing" \
  -F "image=@./acme.png" \
  -F "website_url=https://acme.example" \
  -F "category=1" \
  -F "date=2025-09-15" \
  -F 'tasks=["UI/UX", "Frontend", "SEO"]' \
  -F "description=High-converting landing page for Acme." \
  -F "service_types=1" \
  -F "service_types=2"
```

JSON form (when image is omitted):

```json
{
  "name_uz": "Acme Landing",
  "name_ru": "Лендинг Acme",
  "name_en": "Acme Landing",
  "description_uz": "Konversiyaga yo'naltirilgan landing.",
  "description_ru": "Высоко-конверсионный лендинг.",
  "description_en": "High-converting landing page for Acme.",
  "tasks_uz": ["UI/UX", "Frontend", "SEO"],
  "tasks_ru": ["UI/UX", "Фронтенд", "SEO"],
  "tasks_en": ["UI/UX", "Frontend", "SEO"],
  "website_url": "https://acme.example",
  "category": 1,
  "date": "2025-09-15",
  "service_types": [1, 2]
}
```

Project list/detail responses include the nested `category_detail` and
`service_types_detail` objects for read-side convenience.

### Create a Review

```bash
curl -X POST http://localhost:8000/api/v1/reviews/ \
  -H "Content-Type: application/json" \
  -d '{
    "name_uz": "Jasur Aliyev",
    "name_ru": "Джасур Алиев",
    "name_en": "Jasur Aliyev",
    "comment_uz": "Yuqori darajadagi ish, vaqtida yetkazib berildi.",
    "comment_ru": "Отличная работа, всё в срок.",
    "comment_en": "Top-tier work, delivered on time.",
    "project": 1
  }'
```

## Project layout

```
senior-backend/
├── manage.py
├── requirements.txt
├── senior/                # Django project (settings, urls, wsgi)
│   ├── settings.py
│   └── urls.py
└── apps/
    └── core/              # Single domain app
        ├── models.py      # Category, ServiceType, PortfolioProject, Review (with _uz/_ru/_en columns)
        ├── i18n.py        # LANGUAGES, get_request_language, get_translated_field, TranslatedField
        ├── serializers.py
        ├── filters.py
        ├── views.py
        ├── urls.py
        └── admin.py       # Per-language fieldsets in the admin
```
