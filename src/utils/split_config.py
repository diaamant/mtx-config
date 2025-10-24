# split_config.py

import json
import yaml
import argparse
from pathlib import Path
from typing import Dict, Any, List, Union

from src.core.keys import TAB_KEYS, NAMES_TAB
from src.core.log import logger


def pop_keys_to_dict(
    source_dict: Dict[str, Any], keys_list: List[str]
) -> Dict[str, Any]:
    """
    Извлекает (с удалением) ключи из source_dict в новый словарь
    с использованием словарного включения.
    """
    return {key: source_dict.pop(key) for key in keys_list if key in source_dict}


def save_json_data(data: Dict[str, Any], file_path: Path) -> None:
    """
    Сохраняет данные в .json файл, если данные не пустые.
    """
    if not data:
        logger.warning(f"Нет данных для {file_path.name}, файл не создан.")
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logger.info(f"Успешно сохранен: {file_path}")
    except (IOError, TypeError) as e:
        logger.error(f"ОШИБКА сохранения {file_path}: {e}")


def split_config(config_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Разделяет основной словарь конфигурации на части согласно TAB_KEYS.
    """
    extracted_data = {}
    for tab_key, keys_or_name in TAB_KEYS.items():
        if isinstance(keys_or_name, list):
            # Извлекаем группу ключей
            extracted_data[tab_key] = pop_keys_to_dict(config_data, keys_or_name)
        elif isinstance(keys_or_name, str):
            # Извлекаем один ключ (как pathDefaults или paths)
            extracted_data[tab_key] = config_data.pop(keys_or_name, None)

    # Всё, что осталось в config_data — это app_data
    extracted_data["APP"] = config_data
    return extracted_data


def main():
    try:
        script_path = Path(__file__).resolve()  # .resolve() делает путь абсолютным
    except NameError:
        # FAllback для интерактивных сред (например, Jupyter)
        script_path = Path.cwd()
    # Рассчитываем пути относительно расположения этого скрипта
    # (Path(__file__).parent.parent.parent) - поднимаемся на 3 уровня
    default_base_dir = script_path.parent.parent.parent
    # default_config_file = default_base_dir / "work/orig/mediamtx01.yml"
    default_config_file = default_base_dir / "work/mediamtx01.yml"
    default_output_dir = default_base_dir / "work/json/"

    # --- 2. Настройка argparse ---
    parser = argparse.ArgumentParser(
        description="Разделяет YAML файл конфигурации MediaMTX на отдельные JSON файлы.",
        # Форматирование, чтобы help-сообщения выглядели лучше
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "-c",
        "--config-file",
        type=Path,
        dest="config_file",  # Имя переменной в args
        default=default_config_file,
        help="Путь к исходному YAML файлу конфигурации.",
    )

    parser.add_argument(
        "-o",
        "--output-dir",
        type=Path,
        dest="output_dir",  # Имя переменной в args
        default=default_output_dir,
        help="Директория для сохранения результирующих JSON файлов.",
    )

    args = parser.parse_args()

    # --- 3. Используем значения (либо по умолчанию, либо от пользователя) ---
    config_file_path: Path = args.config_file
    output_dir: Path = args.output_dir

    # Создаем директорию вывода, если ее нет
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        logger.info(f"Читаем файл конфигурации: {config_file_path}")
        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            logger.warning("Файл пуст или не является корректным YAML.")
            return

        logger.info("Файл успешно прочитан. Начинаем разделение данных...")
        extracted_data = split_config(config_data)

        logger.info(f"Сохраняем JSON в директорию: {output_dir}\n")

        for tab_key, data in extracted_data.items():
            filename = output_dir / f"{NAMES_TAB[tab_key]}.json"
            save_json_data(data, filename)

        logger.info("\nЗадача выполнена.")

    except FileNotFoundError:
        logger.error(f"ОШИБКА: Файл не найден по пути: {config_file_path}")
    except yaml.YAMLError as e:
        logger.error(f"ОШИБКА: Не удалось распарсить YAML файл: {e}")
    except Exception as e:
        logger.error(f"ОШИБКА: Произошла непредвиденная ошибка: {e}", exc_info=True)


if __name__ == "__main__":
    main()
