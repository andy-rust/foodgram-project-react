# Foodrgam
### Сайт доступен по ссылке ниже
[Перейти](https://andy-foodgram.ddns.net)

 «Продуктовый помощник»: это сайт, на котором пользователи могут публиковать свои рецепты, добавлять чужие рецепты в избранное и подписываться на публикации других авторов.

Проект реализован на `Django`.
Доступ к данным реализован через API-интерфейс.

## Развертывание проекта

### Развертывание на локальном сервере

- Установите на сервере `docker` и `docker-compose`.

- Создайте файл `/infra/.env`.
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='ключ Django'
```
- Исполните команду `docker-compose up -d --buld`.

- Совершите миграцию `docker-compose exec backend python manage.py migrate`.

- Создайте суперпользователя `docker-compose exec backend python manage.py createsuperuser`.

- Соберите статику `docker-compose exec backend python manage.py collectstatic --no-input`.

- Заполните базу данных ингредиентами и тегами `docker exec -it infra-backend-1 python manage.py loaddata ingredients.json`.

## Автор проекта

[Андрей Литвищенко](https://github.com/andy-rust)
