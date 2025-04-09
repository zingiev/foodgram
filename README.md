# Foodgram

**Foodgram** — это веб-платформа для публикации и обмена кулинарными рецептами. Пользователи могут зарегистрироваться, делиться собственными рецептами, подписываться на других авторов и сохранять понравившиеся рецепты в избранное. Проект помогает собрать свою кулинарную коллекцию и найти вдохновение среди рецептов других пользователей.

## 🌐 Сайт проекта

[https://foodgramz.hopto.org/](https://foodgramz.hopto.org/)

## 👤 Автор

Зингиев Ясин  
[Telegram — t.me/yasinzingiev](https://t.me/yasinzingiev)

## 🛠️ Технологический стек

- Язык программирования: **Python**
- Backend-фреймворк: **Django**, **Django REST Framework**
- Frontend: **React**
- Сервер приложений: **Gunicorn**
- Веб-сервер: **Nginx**
- СУБД: **PostgreSQL**
- Контейнеризация: **Docker**, **Docker Compose**
- Управление окружением: **dotenv**
- CI/CD: **GitHub Actions**

## 🚀 CI/CD

Автоматическое развертывание осуществляется через **GitHub Actions**. При пуше в основную ветку:

- выполняется сборка и публикация Docker-образов,
- обновляется проект на удалённом сервере,
- выполняются миграции и сборка статики.

## 🐳 Локальный запуск с Docker

### 1. Клонировать репозиторий:

```bash
git clone https://github.com/zingiev/foodgram.git
```
### 2.  Переход в папку с docker-compose.yml.
```bash
cd foodgram/
```
### 3. Создать .env файл:
Создайте файл .env в директории со следующим содержанием:
```bash
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=12345
DB_HOST=db
DB_PORT=5432
DEBUG=False
SECRET_KEY=secret_key
ALLOWED_HOSTS=127.0.0.1, localhost
```
### 4. Запустить контейнеры:
```bash
docker-compose up -d --build
```
### 5. Подготовка базы данных:
```bash
# Войти в контейнер backend
docker-compose exec backend bash

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Загрузить ингредиенты
python manage.py load_ingredients data/ingredients.json
```
### 6. Собрать статику:
```bash
python manage.py collectstatic --noinput
cp -r /backend_static/. /backend_static/static/
```
