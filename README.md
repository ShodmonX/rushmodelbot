# rushmodelbot V0.1.1 Foundation

Minimal, clean Telegram bot + FastAPI + PostgreSQL stack (webhook only, asyncpg).

## Quick start (dev)

1) `.env` yarating:

```
cp .env.example .env
```

2) `.env` ichida quyidagilarni to'ldiring:

- `BOT_TOKEN`
- `NGROK_AUTHTOKEN`
- `APP_ENV=dev`

3) Dev profil bilan ishga tushiring (ngrok avtomatik):

```
docker compose --profile dev up --build
```

4) Migratsiyalarni ishga tushiring:

```
docker compose run --rm api alembic upgrade head
```

Webhook avtomatik o'rnatiladi, qo'lda set qilish shart emas.

## Quickstart (Makefile)

```
make up
make migrate
make ngrok-url
make logs
```

## Prod rejim

1) `.env` ichida `APP_ENV=prod` va `WEBHOOK_HOST=https://your-domain` ni belgilang.
2) Ishga tushiring:

```
docker compose up --build -d
```

## Test scenario

1) Teacher ro'yxatdan o'tadi.
2) Teacher profilda referral link oladi.
3) Student referral link orqali /start qiladi.
4) Student ro'yxatdan o'tadi va teacherga bog'lanadi.
5) Teacher `👥 O‘quvchilarim` bo'limida ro'yxatni ko'radi.

## Endpointlar

- API health: `GET http://localhost:8000/health`
- Bot webhook: `POST http://localhost:8080/tg/webhook`
- Ngrok API (dev): `http://localhost:4040/api/tunnels`

## Notes

- Bot polling ishlatilmaydi, faqat webhook.
- Admin roli UI'da yo'q, faqat `.env` orqali tekshiriladi.
- Database driver: `asyncpg`.

## Admin notifications

- Yangi lead birinchi marta yaratilganda adminlarga xabar boradi.
- User ro'yxatdan o'tishni tugatganda adminlarga xabar boradi.
- Adminlar `.env` dagi `ADMIN_TELEGRAM_IDS` orqali aniqlanadi.

## Lead tracking

- /start bosilganda user ma'lumotlari `user_leads` jadvaliga yoziladi.
- /start qayta bosilsa lead yangilanadi, yangi notification yuborilmaydi.
- Ro'yxatdan o'tganda `user_leads.is_registered=true` va `registered_at` belgilanadi.

## V1.0 Test Flow

- Teacher: `📝 New Test` -> shablon tanlash -> sarlavha -> material (ixtiyoriy) -> Y1/Y2/O kalitlari -> publish.
- Student: `✅ Join Test` -> kod -> Y1/Y2/O javoblari -> submit -> natija.
- Teacher `📋 My Tests` bo'limida status va urinishlar sonini ko'radi.
