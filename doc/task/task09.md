

### 1. Тестирование Функционала: Импорт и Экспорт
- **Задача:** Скорректировать и провести тест MtxConfigManager.import_config(content)
- **Исходные данные:**  
  - тест: tests/test_import_export.py
  - YAML:  /tests/yml_test/mediamtx01.yml 
  - JSON:  /tests/json_test/*.json
- **Запуск тестирования:**
   source .venv/bin/activate
   python -m pytest tests/test_import_export.py -v
- **Результаты:**  На данный момент импорт производится неверно: 
  - В /tests/json_test_wrong/*.json - неверный импорт
  - В /tests/json_test/*.json - правильный импорт произведенный /utils/read_config.py
- **Реализация:** Исправить YAMLClient.import_config 
  На данный момент он делает простую конвертацию конфига без разбивки по TAB_NAMES (core/config.py) как это делается в /utils/read_config.py