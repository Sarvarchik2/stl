# STL Auto - Платформа автокредитования

Полное приложение для автокредитования с backend на FastAPI и двумя frontend приложениями на Nuxt 3.

## Структура проекта

```
stl-admin/
├── backend/          # FastAPI backend
├── frontend/         # Клиентское приложение (Nuxt 3)
├── admin/           # Админ панель (Nuxt 3)
└── README.md
```

## Требования

- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (для backend)

## Установка и запуск

### 1. Backend (FastAPI)

```bash
# Перейти в директорию backend
cd backend

# Установить зависимости
pip3 install -r requirements.txt

# Убедиться, что PostgreSQL запущен на порту 5433
# Или изменить DATABASE_URL в .env файле

# Запустить сервер
python3 -m uvicorn app.main:app --reload --port 8000
```

Backend будет доступен по адресу: http://localhost:8000
API документация: http://localhost:8000/docs

### 2. Frontend (Клиентское приложение)

```bash
# Перейти в директорию frontend
cd frontend

# Установить зависимости (если еще не установлены)
npm install

# Запустить dev сервер
npm run dev
```

Frontend будет доступен по адресу: http://localhost:3000

### 3. Admin (Админ панель)

```bash
# Перейти в директорию admin
cd admin

# Установить зависимости (если еще не установлены)
npm install

# Запустить dev сервер (на другом порту)
npm run dev -- --port 3001
```

Админ панель будет доступна по адресу: http://localhost:3001

## Быстрый запуск всех сервисов

Вы можете запустить все три сервиса одновременно в разных терминалах:

**Терминал 1 - Backend:**
```bash
cd backend && python3 -m uvicorn app.main:app --reload --port 8000
```

**Терминал 2 - Frontend:**
```bash
cd frontend && npm run dev
```

**Терминал 3 - Admin:**
```bash
cd admin && npm run dev -- --port 3001
```

## Функциональность

### Frontend (Клиентское приложение)
- ✅ Современный минималистичный дизайн
- ✅ Каталог автомобилей с фильтрацией
- ✅ Регистрация и авторизация
- ✅ Подача заявок на кредит
- ✅ Личный кабинет
- ✅ Адаптивный дизайн для мобильных устройств

### Admin (Админ панель)
- ✅ Дашборд со статистикой
- ✅ Управление автомобилями
- ✅ Управление заявками
- ✅ Управление пользователями
- ✅ Управление платежами
- ✅ Черный список
- ✅ Современный UI с боковой навигацией

### Backend API
- ✅ Аутентификация JWT
- ✅ CRUD операции для автомобилей
- ✅ Управление заявками
- ✅ Управление пользователями
- ✅ Загрузка документов
- ✅ Система платежей
- ✅ Черный список
- ✅ Роли пользователей (admin, owner, client)

## Дизайн

Приложение использует современный минималистичный дизайн с:
- Темная цветовая схема
- Градиентные акценты (индиго/фиолетовый)
- Glassmorphism эффекты
- Плавные анимации и переходы
- Адаптивная верстка
- Современная типографика (Inter)

## API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена

### Автомобили
- `GET /api/v1/cars` - Список автомобилей
- `GET /api/v1/cars/{id}` - Детали автомобиля
- `POST /api/v1/cars` - Создать автомобиль (admin)
- `PUT /api/v1/cars/{id}` - Обновить автомобиль (admin)
- `DELETE /api/v1/cars/{id}` - Удалить автомобиль (admin)

### Заявки
- `GET /api/v1/applications` - Список заявок (admin)
- `GET /api/v1/applications/my` - Мои заявки
- `POST /api/v1/applications` - Создать заявку
- `PUT /api/v1/applications/{id}` - Обновить заявку

### Пользователи
- `GET /api/v1/users/me` - Текущий пользователь
- `GET /api/v1/users` - Список пользователей (admin)
- `PUT /api/v1/users/{id}` - Обновить пользователя

## Переменные окружения

### Backend (.env)
```env
DATABASE_URL=postgresql+asyncpg://postgres:admin123@localhost:5433/postgres
SECRET_KEY=your-secret-key
DEBUG=True
```

### Frontend (.env)
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

### Admin (.env)
```env
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

## Решение проблем

### PostgreSQL не запущен
Убедитесь, что PostgreSQL запущен:
```bash
# macOS
brew services start postgresql@14

# Или проверьте статус
brew services list
```

### Порт уже занят
Если порт 8000, 3000 или 3001 занят:
```bash
# Найти процесс
lsof -ti:8000

# Остановить процесс
kill -9 <PID>
```

### Ошибки установки зависимостей
```bash
# Backend
cd backend
pip3 install --upgrade pip
pip3 install -r requirements.txt

# Frontend/Admin
cd frontend  # или admin
rm -rf node_modules package-lock.json
npm install
```

## Технологии

### Backend
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- JWT Authentication
- Pydantic
- Uvicorn

### Frontend & Admin
- Nuxt 3
- Vue 3
- TypeScript
- Vanilla CSS
- Fetch API

## Лицензия

MIT

## Автор

STL Auto Team
