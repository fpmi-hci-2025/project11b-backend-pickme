# PickMe Backend

Backend API для социальной сети PickMe с гибкой приватностью.

## Технологии

- Python 3.12
- Django 5.1
- Django REST Framework
- PostgreSQL
- Docker

## Локальный запуск

### С Docker (рекомендуется)

```bash
# Клонировать репозиторий
git clone https://github.com/your-org/pickme-backend.git
cd pickme-backend

# Запустить
docker-compose up -d

# API доступно на http://localhost:8000
# Документация: http://localhost:8000/api/docs/
```

## Тестирование

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=apps --cov-report=html
```

## API Endpoints

### Аутентификация
- `POST /api/auth/register/` - Регистрация
- `POST /api/auth/login/` - Вход
- `POST /api/auth/logout/` - Выход
- `POST /api/auth/refresh/` - Обновление токена

### Пользователи
- `GET /api/users/me/` - Текущий пользователь
- `GET /api/users/{id}/` - Профиль пользователя
- `PUT /api/users/{id}/update/` - Обновление профиля
- `POST /api/users/{id}/avatar/` - Загрузка аватара
- `GET /api/users/search/?q=` - Поиск пользователей

### Посты
- `GET /api/posts/` - Лента постов
- `POST /api/posts/` - Создать пост
- `GET /api/posts/{id}/` - Получить пост
- `PUT /api/posts/{id}/` - Обновить пост
- `DELETE /api/posts/{id}/` - Удалить пост
- `GET /api/posts/user/{id}/` - Посты пользователя

### Группы доступа
- `GET /api/friend-groups/` - Список групп
- `POST /api/friend-groups/` - Создать группу
- `GET /api/friend-groups/{id}/` - Детали группы
- `PUT /api/friend-groups/{id}/` - Обновить группу
- `DELETE /api/friend-groups/{id}/` - Удалить группу
- `GET /api/friend-groups/{id}/members/` - Участники группы
- `POST /api/friend-groups/{id}/members/add/` - Добавить участника
- `DELETE /api/friend-groups/{id}/members/{userId}/` - Удалить участника

## Лицензия

MIT
