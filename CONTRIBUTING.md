# Contributing to Mediamtx Configuration Editor

Спасибо за интерес к улучшению проекта! 🎉

## Быстрый старт

1. Fork репозитория
2. Создайте feature branch: `git checkout -b feature/amazing-feature`
3. Внесите изменения
4. Запустите тесты: `pytest`
5. Commit изменений: `git commit -m 'Add amazing feature'`
6. Push в branch: `git push origin feature/amazing-feature`
7. Создайте Pull Request

## Стандарты кода

### Python Code Style

- Используйте **type hints** для всех функций и методов
- Следуйте **PEP 8** стандартам
- Добавляйте **docstrings** для всех публичных функций
- Максимальная длина строки: **100 символов**

### Пример хорошего кода

```python
def create_stream(name: str, stream_type: str) -> Dict[str, Any]:
    """Create a new stream configuration.
    
    Args:
        name: Unique stream name
        stream_type: Type of stream ('Source' or 'RunOnDemand')
        
    Returns:
        Dictionary with stream configuration
        
    Raises:
        ValueError: If stream_type is invalid
    """
    if stream_type not in ["Source", "RunOnDemand"]:
        raise ValueError(f"Invalid stream type: {stream_type}")
    
    # Implementation here
    return config
```

## Тестирование

### Обязательно

- Все новые функции должны иметь тесты
- Все тесты должны проходить перед PR
- Стремитесь к coverage > 80%

### Запуск тестов

```bash
# Все тесты
pytest

# С coverage
pytest --cov=src --cov-report=term-missing

# Конкретный файл
pytest tests/test_models.py -v
```

## Линтинг

Используйте `ruff` для проверки кода:

```bash
# Проверка
ruff check src/

# Автоисправление
ruff check --fix src/
```

## Коммиты

### Формат сообщений

Используйте [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <subject>

<body>
```

### Типы

- `feat`: Новая функция
- `fix`: Исправление бага
- `docs`: Изменения в документации
- `style`: Форматирование кода
- `refactor`: Рефакторинг кода
- `test`: Добавление тестов
- `chore`: Обновление зависимостей, конфигурации

### Примеры

```bash
feat(paths): add stream cloning functionality
fix(validation): correct timeout regex pattern
docs(readme): update installation instructions
test(models): add tests for StreamConfig validation
```

## Pull Request Checklist

Перед созданием PR убедитесь:

- [ ] Код следует стандартам проекта
- [ ] Все тесты проходят
- [ ] Добавлены тесты для новой функциональности
- [ ] Обновлена документация (README.md, docstrings)
- [ ] Код прошел линтинг без ошибок
- [ ] PR имеет понятное описание изменений
- [ ] Нет конфликтов с main веткой

## Приоритеты развития

См. `doc/task/task01.md` для списка предложенных улучшений с приоритетами.

### P0 - Критичные
- Исправление багов
- Улучшение валидации
- Повышение стабильности

### P1 - Высокий приоритет
- Новые функции из task01.md
- Улучшение UX
- Оптимизация производительности

### P2 - Средний приоритет
- Дополнительные функции
- Улучшение документации
- Рефакторинг

## Вопросы?

Если у вас есть вопросы:
- Создайте Issue с меткой `question`
- Обсудите в Pull Request
- Свяжитесь с мейнтейнерами

Спасибо за ваш вклад! 🚀
