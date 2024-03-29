# Foodrgam
### Сайт доступен по ссылке ниже
[Перейти](https://andy-foodgram.ddns.net)

 «Продуктовый помощник»: это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

## Автор проекта

[Андрей Литвищенко](https://github.com/andy-rust)

Технологии, которые используются в проекте:
- Python 3.11.4
- Django 3.2
- Django REST framework 3.14.0

### Развертывание проекта

## Запуск проекта

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:andy-rust/foodgram-project-react.git
```
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
source venv/scripts/activate
```

Обновить pip и установить зависимости

```
python -m pip install --upgrade pip
pip inistall -r requirements.txt
```

Создать миграции:

```
python manage.py makemigrations
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Развертывание проекта на сервере c помощью Docker

- Установите на сервере `docker` и `docker-compose`.

- Перейдите в директорию `/backend/foodgram/` и создайте там файл `/.env`.
```
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
TOKEN='ключ Django'
```
- Сбилдить образы frontend и backend находясь в корневой директории проекта
```
docker build -t username/foodgram_frontend:latest frontend/
docker build -t username/foodgram_backend:latest backend/
```

- Перейдите в директорию `infra/` и по очереди выполните следующие команды
```
- docker-compose up -d --buld
- docker-compose exec backend python manage.py migrate
- docker-compose exec backend python manage.py createsuperuser
- docker-compose exec backend python manage.py collectstatic --no-input
```

- Заполните базу данных ингредиентами
`docker exec -it infra-backend-1 python manage.py loaddata ingredients.json`.
