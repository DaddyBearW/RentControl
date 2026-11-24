# RentControl

Веб-приложение для управления арендой оборудования: каталог, бронирование на даты, расчёт стоимости, выдача, возврат и контроль просрочек.

## Стек

- Frontend: React 18, TypeScript, Vite.
- Backend: Python 3.12, FastAPI, SQLAlchemy.
- Database: PostgreSQL 16.
- Авторизация: JWT, роли `customer`, `manager`, `admin`.
- Инфраструктура: Docker Compose, GitHub Actions, Pytest.
- Архитектура: монолитный backend с разделением на API, модели, схемы, сервисные/инфраструктурные компоненты; frontend — отдельное приложение.

## Быстрый запуск через Docker

1. Установите Docker Desktop и запустите его.
2. В корне проекта скопируйте `.env.example` в `.env`.
3. Измените `POSTGRES_PASSWORD`, `SECRET_KEY`, `ADMIN_EMAIL` и `ADMIN_PASSWORD` на собственные значения.
4. Выполните:

```bash
docker compose up --build -d
```

5. Создайте администратора и демонстрационные записи:

```bash
docker compose exec backend python -m app.seed
```

6. Откройте:
   - Frontend: http://localhost:5173
   - REST API: http://localhost:8000
   - Swagger: http://localhost:8000/docs
   - Health check: http://localhost:8000/api/health

Войдите с данными из `ADMIN_EMAIL` и `ADMIN_PASSWORD` в `.env`. Не используйте демонстрационный пароль в реальном развёртывании.

## Запуск на этом компьютере (Windows)

Проект развёрнут двумя способами. **Порты у них одинаковые (`8000` и `5173`), поэтому одновременно запускайте только один вариант.**

### Вариант 1 — Docker (проверено, работает)

Docker Desktop установлен в пользовательский каталог `C:\Users\Mosen\AppData\Local\Programs\DockerDesktop` (без прав администратора, WSL2-бэкенд). Образы собраны, три контейнера запущены.

| Контейнер | Образ | Порт на хосте |
|---|---|---|
| `rentcontrol-db` | `postgres:16-alpine` | внутренний 5432 |
| `rentcontrol-api` | `rentcontrol-backend` | `8000` |
| `rentcontrol-web` | `rentcontrol-frontend` (nginx) | `5173` |

```powershell
cd D:\projects\RentControl
docker compose up --build -d                    # собрать и запустить
docker compose exec backend python -m app.seed  # админ + демо-каталог (идемпотентно)
docker compose ps                               # статус
docker compose logs -f backend                  # логи API
docker compose down                             # остановить (данные сохраняются)
docker compose down -v                          # остановить и удалить БД
```


### Адреса

- Frontend: http://localhost:5173
- Swagger: http://localhost:8000/docs
- Health check: http://localhost:8000/api/health

### Пересоздать локальную SQLite-базу

```powershell
cd backend
Remove-Item rentcontrol.db
.\.venv\Scripts\python.exe -m app.seed
```

## Исправления, внесённые при проверке

| Проблема | Проявление | Исправление |
|---|---|---|
| Вход под `admin@rentcontrol.local` возвращал `422` | `pydantic.EmailStr` отвергает домены специального назначения (`.local`), поэтому войти под документированным администратором было невозможно | `backend/app/schemas.py`: собственный валидатор `Email` — проверяет синтаксис и нормализует регистр, но не запрещает `.local` |
| `npm run build` падал с `TS2339: Property 'env' does not exist on type 'ImportMeta'` | Отсутствовали типы Vite, из-за чего падала и production-сборка, и сборка Docker-образа frontend | добавлен `frontend/src/vite-env.d.ts` с `/// <reference types="vite/client" />` |
| `python -m app.seed` игнорировал `.env` | Скрипт читал только переменные окружения, поэтому локально создавался администратор с паролем по умолчанию | `backend/app/core/config.py` + `seed.py`: добавлены `ADMIN_EMAIL`/`ADMIN_PASSWORD` в `Settings`, seed берёт их из `.env` |


## Роли и права

| Возможность | Клиент (`customer`) | Менеджер (`manager`) | Администратор (`admin`) |
|---|---:|---:|---:|
| Просмотр каталога | Да | Да | Да |
| Создание аренды | Да | Да | Да |
| Просмотр своих аренд | Да | Да | Да |
| Просмотр всех аренд | Нет | Да | Да |
| Добавление/изменение оборудования | Нет | Да | Да |
| Выдача и возврат оборудования | Нет | Да | Да |
| Удаление (деактивация) оборудования | Нет | Нет | Да |
| Управление ролями пользователей | Нет | Нет | Да |

Первый зарегистрированный пользователь не становится администратором автоматически. Для начальной настройки запустите `python -m app.seed` внутри backend (или `docker compose exec backend python -m app.seed`). Скрипт создаёт администратора и демо-каталог; при повторном запуске обновляет пароль и роль указанного администратора.

## REST API

| Метод | Endpoint | Назначение |
|---|---|---|
| POST | `/api/auth/register` | Регистрация |
| POST | `/api/auth/login` | Вход |
| GET | `/api/auth/me` | Текущий пользователь |
| GET | `/api/equipment` | Каталог, поиск `?q=`, фильтр `?category=` |
| GET | `/api/equipment/{id}` | Карточка оборудования |
| POST | `/api/equipment` | Добавить оборудование (manager/admin) |
| PATCH | `/api/equipment/{id}` | Изменить оборудование (manager/admin) |
| DELETE | `/api/equipment/{id}` | Деактивировать (admin) |
| POST | `/api/rentals` | Создать бронирование |
| GET | `/api/rentals` | Список доступных пользователю аренд |
| PATCH | `/api/rentals/{id}/issue` | Оформить выдачу (manager/admin) |
| PATCH | `/api/rentals/{id}/return` | Оформить возврат (manager/admin) |
| GET | `/api/admin/users` | Пользователи (admin) |
| PATCH | `/api/admin/users/{id}/role` | Изменить роль (admin) |
| GET | `/api/admin/stats` | Сводная статистика (manager/admin) |

Swagger содержит интерактивную документацию всех маршрутов.

## Правила аренды

- Даты начала и окончания включаются в период аренды. Один календарный день стоит как минимум одну дневную ставку.
- Проверяется доступное количество экземпляров с учётом пересечения периодов активных бронирований.
- Итоговая стоимость = количество календарных дней × цена за день.
- Просрочка определяется при запросе списка аренд, если дата окончания прошла, а аренда не возвращена.
- Возврат доступен менеджеру или администратору.

## Тесты

Из корня проекта:

```bash
cd backend
pip install -r requirements.txt
PYTHONPATH=. pytest ../tests -v
```

Тесты используют отдельную временную SQLite-базу и не затрагивают рабочие данные.

## CI/CD

GitHub Actions запускает backend-тесты и сборку frontend при push и pull request в `main`/`master`. Отдельный workflow `deploy.yml` выполняет CD на VPS при push в `main` или вручную. Для его включения добавьте в GitHub Actions Secrets значения `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` и `VPS_DEPLOY_PATH`; на сервере предварительно клонируйте репозиторий, создайте `.env` и установите Docker Compose. Workflow обновит код, пересоберёт контейнеры и выполнит seed-команду.

## Варианты развёртывания

1. Локально: SQLite + Uvicorn + Vite для разработки.
2. Docker Compose: frontend, backend и PostgreSQL на одном компьютере или VPS.
3. VPS/облако: Docker Compose за Nginx с HTTPS (например, через Let's Encrypt); PostgreSQL можно оставить контейнерным или вынести в управляемую БД.


