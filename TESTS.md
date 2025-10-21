# Тестирование mtx-config

## Обзор

Проект включает комплексную систему тестирования, состоящую из трех основных типов тестов:

### Unit тесты
Проверяют отдельные модули и функции приложения:
- **Модели данных** - валидация Pydantic моделей
- **Конфигурационные клиенты** - JSONClient и YAMLClient
- **Утилиты** - функции загрузки/сохранения JSON и YAML через клиентов
- **Настройки** - singleton паттерн и конфигурация

### Playwright E2E тесты
Проверяют пользовательский интерфейс без необходимости запуска сервера:
- **Структура интерфейса** - наличие элементов и навигация
- **Взаимодействие** - фильтры, поиск, кнопки
- **Отзывчивость** - поведение интерфейса при различных действиях

## Запуск тестов

### Unit тесты
```bash
source .venv/bin/activate
python -m pytest tests/test_config_clients.py tests/test_json_utils.py tests/check_models.py -v
```

### Playwright E2E тесты
```bash
source .venv/bin/activate
./run_tests.sh
```

Или вручную:
```bash
source .venv/bin/activate
# Запустить тесты без сервера
python -m pytest tests/test_filters.py -v -m playwright
```

### Все тесты вместе
```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

## Структура тестов

### tests/test_models.py
Тесты для Pydantic моделей валидации:
- Валидация URL источников (RTSP/RTMP/HTTP)
- Проверка форматов timeout (10s, 5m, 1h)
- Валидация методов аутентификации
- Тестирование дополнительных полей

### tests/test_config_clients.py
Тесты для конфигурационных клиентов:
- **JSONClient** - загрузка и сохранение JSON файлов
- **YAMLClient** - сборка и сохранение YAML конфигурации
- **Фабричная функция** - получение клиентов с кэшированием
- Обработка ошибок файловой системы

### tests/test_json_utils.py
Тесты для утилит работы с JSON и YAML через клиентов:
- Загрузка данных с созданием флагов enabled через JSONClient
- Сохранение YAML с созданием бэкапа через YAMLClient
- Пропуск отключенных секций
- Обработка ошибок файловой системы

### tests/test_filters.py
Playwright тесты для интерфейса:
- Проверка структуры HTML элементов
- Тестирование взаимодействия с фильтрами
- Валидация селекторов и инпутов

## Конфигурация тестирования

### pytest.ini
Основная конфигурация pytest с разделением на типы тестов:
- Unit тесты с маркировкой
- Playwright тесты с маркировкой
- Разные настройки для разных типов

### pytest-unit.ini
Конфигурация для unit тестов с отчетом покрытия кода.

### pytest-playwright.ini
Конфигурация для Playwright тестов с настройками браузера.

### run_tests.sh
Автоматический скрипт запуска Playwright тестов без необходимости ручного управления сервером.

## Покрытие кода

После запуска unit тестов откройте `htmlcov/index.html` для просмотра детального отчета о покрытии кода.

## Требования

- **Python 3.13+**
- **Виртуальное окружение** с установленными зависимостями
- **Playwright браузеры** (устанавливаются автоматически)
- **pytest-playwright** для E2E тестирования

## Отладка тестов

### Unit тесты
```bash
# Запуск с подробным выводом
pytest -v -s tests/test_config_clients.py

# Запуск конкретного теста
pytest tests/test_config_clients.py::TestJSONClient::test_load_config_success -v

# С покрытием кода
pytest --cov=src --cov-report=html tests/test_config_clients.py
```

### Playwright тесты
```bash
# Запуск с отладкой браузера
pytest tests/test_filters.py -v -m playwright -s

# Запуск в графическом режиме
pytest tests/test_filters.py -v -m playwright --headed
```

## Результаты последних тестов

- ✅ **Unit тесты**: 35 тестов пройдены (добавлены тесты для клиентов)
- ✅ **Playwright тесты**: 2 теста пройдены
- ✅ **Всего**: 37 тестов пройдены успешно
