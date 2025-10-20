# Исправление множественной инициализации Settings

## Проблема

При запуске приложения с NiceGUI настройки (`Settings`) инициализировались **5 раз** вместо одного:

```
env_path - /mnt/data/storeSoft/projPySample/mtx-config/.env
Environment variables loaded from %s /mnt/data/storeSoft/projPySample/mtx-config/.env
Application settings initialized: %s {...}
```

Это повторялось при каждом создании нового процесса/потока NiceGUI для обработки клиентских подключений.

## Причина

В файле `/src/core/config.py` была **инициализация на уровне модуля**:

```python
# Backward compatibility - keep the old settings variable
settings = get_settings()  # ❌ Вызывается при каждом импорте модуля

if settings.DEBUG:
    print(...)  # ❌ Выполняется при каждом импорте
```

Это приводило к тому, что при каждом импорте модуля `src.core.config` создавался новый экземпляр `Settings`, несмотря на наличие singleton паттерна.

## Решение

### 1. Убрана инициализация на уровне модуля

Удалена строка `settings = get_settings()` из глобальной области видимости модуля.

### 2. Debug-вывод перенесен внутрь `get_settings()`

```python
def get_settings() -> Settings:
    """Get or create the singleton settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = Settings()
        _debug_print_settings(_settings_instance)  # ✅ Вызывается только один раз
    return _settings_instance
```

### 3. Обновлены все импорты

Все модули теперь используют `get_settings()` вместо прямого импорта `settings`:

- ✅ `src/config_manager.py` - использует `get_settings()`
- ✅ `src/utils/json_utils.py` - использует `_get_json_dir()` → `get_settings()`
- ✅ `src/utils/yaml_utils.py` - использует `_get_paths()` → `get_settings()`

### 4. Добавлена обратная совместимость

Для старого кода, который импортирует `settings` напрямую, добавлен `__getattr__`:

```python
def __getattr__(name: str):
    if name == "settings":
        warnings.warn(
            "Direct import of 'settings' is deprecated. Use 'get_settings()' instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return get_settings()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
```

## Результат

✅ **Settings инициализируется только один раз** при первом вызове `get_settings()`  
✅ **Singleton паттерн работает корректно** во всех процессах/потоках  
✅ **Обратная совместимость сохранена** с предупреждением о deprecated использовании  
✅ **Debug-вывод появляется только один раз** при первой инициализации  

## Миграция для существующего кода

### Старый способ (deprecated):
```python
from src.core.config import settings

print(settings.app_port)
```

### Новый способ (рекомендуется):
```python
from src.core.config import get_settings

settings = get_settings()
print(settings.app_port)
```

## Тестирование

```bash
# Проверка единственной инициализации
python -c "from src.core.config import get_settings; s = get_settings(); print(f'Port: {s.app_port}')"

# Проверка singleton
python -c "from src.core.config import get_settings; s1 = get_settings(); s2 = get_settings(); print(f'Same: {s1 is s2}')"

# Проверка обратной совместимости (с предупреждением)
python -c "import warnings; warnings.simplefilter('always'); from src.core.config import settings; print(settings.app_port)" 2>&1
```

## Дата изменения

2025-10-20
