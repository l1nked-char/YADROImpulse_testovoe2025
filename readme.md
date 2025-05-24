# Приложение по хранению и обработке ациклических графов

Сервис реализован как микросервисное приложение, состоящее из:
FastAPI-сервиса: Обрабатывает HTTP-запросы, реализует бизнес-логику.
PostgreSQL: Хранит данные о графах (узлы, связи, метаинформацию).
Docker-контейнеров: Обеспечивают изолированное и воспроизводимое окружение.

# Запуск приложения с помощью Docker

Это руководство поможет вам запустить приложение в Docker-контейнерах.

## Требования
- Установленный [Docker](https://docs.docker.com/get-docker/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

## Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Запустите контейнеры
```bash
docker-compose up -d --build
```
### 4. Проверьте статус контейнеров
```bash
docker-compose ps
```
#### Команды управления
Остановка контейнеров
```bash
docker-compose down
```
Пересборка и запуск
```bash
docker-compose up -d --build --force-recreate
```
Просмотр логов
```bash
# Логи приложения
docker-compose logs -f web
# Логи базы данных
docker-compose logs -f db
```
Удаление всех данных
```bash
docker-compose down -v
```
### Доступ к приложению
API: http://localhost:8080
Документация Swagger: http://localhost:8080/docs
База данных PostgreSQL: localhost:5432

Тестирование
Для запуска тестов выполните:
```bash
docker-compose run --rm tests
```
Структура проекта
```
.
├── src/             # Исходный код приложения
├── tests/           # Тесты
├── docker-compose.yml
├── Dockerfile
├── Dockerfile.test
└── requirements.txt
```
