# Приложение по хранению и обработке ациклических графов

Сервис реализован как микросервисное приложение, состоящее из:
FastAPI-сервиса: Обрабатывает HTTP-запросы, реализует бизнес-логику.

PostgreSQL: Хранит данные о графах (узлы, связи, метаинформацию).

Docker-контейнеров: Обеспечивают изолированное и воспроизводимое окружение.

## Общие принципы работы
- **REST API** на FastAPI для управления графами (узлы/ребра)
- Хранение данных в PostgreSQL с нормализованной структурой:
  - Таблицы `graphs`, `nodes`, `edges`
  - Внешние ключи и индексы для связей
- Изолированное Docker-окружение:
  - Отдельные контейнеры для API и БД
  - Автоматическая инициализация схемы БД при старте

## Особенности
1. **Оптимизация запросов**:
   - Использование CTE для рекурсивных запросов
   - Составные индексы для часто используемых полей

2. **Безопасность**:
   - Изоляция БД во внутренней Docker-сети
   - Валидация входных данных через Pydantic

3. **Тестирование**:
   - Интеграционные тесты с фикстурами pytest

# Запуск приложения с помощью Docker

Это руководство поможет вам запустить приложение в Docker-контейнерах.

## Требования
- Установленный [Docker](https://docs.docker.com/get-docker/)
- Установленный [Docker Compose](https://docs.docker.com/compose/install/)

## Быстрый старт

### 1. Клонируйте репозиторий
```bash
git clone [https://github.com/your-username/your-repo.git](https://github.com/l1nked-char/YADROImpulse_testovoe2025.git)
cd YADROImpulse_testovoe2025
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
