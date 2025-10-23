import json
from pathlib import Path

import yaml

from src.core.keys import TAB_KEYS, NAMES_TAB


def pop_keys_to_dict(source_dict, keys_list):
    """
    Извлекает (с удалением) ключи из source_dict в новый словарь.
    """
    new_dict = {}
    for key in keys_list:
        if key in source_dict:
            new_dict[key] = source_dict.pop(key)
    return new_dict


def save_json_data(data, file_path):
    """
    Сохраняет данные в .json файл, если данные не пустые.
    """
    if not data:
        print(f"Нет данных для {file_path.name}, файл не создан.")
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Успешно сохранен: {file_path}")
    except Exception as e:
        print(f"ОШИБКА сохранения {file_path}: {e}")


def main():
    base_dir = Path(__file__).parent.parent.parent
    config_file_path = base_dir / "work/orig/mediamtx01.yml"
    output_dir = base_dir / "work/json/"
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        print(f"Читаем файл конфигурации: {config_file_path}")
        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            print("Файл пуст или не является корректным YAML.")
            return

        print("Файл успешно прочитан. Начинаем разделение данных...")
        extracted_data = {}
        for tab_key, keys_or_name in TAB_KEYS.items():
            if isinstance(keys_or_name, list):
                extracted_data[tab_key] = pop_keys_to_dict(config_data, keys_or_name)
            elif isinstance(keys_or_name, str):
                extracted_data[tab_key] = config_data.pop(keys_or_name, None)

        # Всё, что осталось — это app_data
        extracted_data["APP"] = config_data

        print(f"Сохраняем JSON в директорию: {output_dir}\n")

        for tab_key, data in extracted_data.items():
            filename = output_dir / f"{NAMES_TAB[tab_key]}.json"
            save_json_data(data, filename)

        print("\nЗадача выполнена.")

    except FileNotFoundError:
        print(f"ОШИБКА: Файл не найден по пути: {config_file_path}")
    except yaml.YAMLError as e:
        print(f"ОШИБКА: Не удалось распарсить YAML файл: {e}")
    except Exception as e:
        print(f"ОШИБКА: Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
