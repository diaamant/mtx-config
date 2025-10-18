import json
import os
import shutil
from pathlib import Path
from nicegui import ui
import yaml
from utils.json_utils import load_data, save_data as save_data_core

# Define paths
WORK_DIR = Path("work")
JSON_DIR = WORK_DIR / "json"
YAML_FILE = WORK_DIR / "mediamtx01.yml"
YAML_BACKUP_FILE = WORK_DIR / "mediamtx01.yml.bak"

# Tab names mapping
TAB_NAMES = {
    "values_app.json": "App (Основные)",
    "auth.json": "Auth",
    "values_rtsp.json": "RTSP",
    "values_webrtc.json": "WebRTC",
    "values_hls.json": "HLS",
    "values_rtmp.json": "RTMP",
    "values_srt.json": "SRT",
    "values_pathDefaults.json": "Path Defaults",
    "paths.json": "Paths",
}

# Data storage
data = load_data()


def save_and_notify():
    """Wrapper to call core save function and show UI notification."""
    try:
        save_data_core(data)
        ui.notify("Конфигурация успешно сохранена!", color="positive")
    except Exception as e:
        ui.notify(f"Ошибка при сохранении: {e}", color="negative")


def create_ui_element(key, value, parent_dict):
    """Dynamically create a UI element based on the value's type."""
    if isinstance(value, bool):
        ui.checkbox(key).bind_value(parent_dict, key)
    elif isinstance(value, list):
        # Using textarea for lists as it's simpler to manage for various list types.
        ui.textarea(key, value="\n".join(map(str, value))).on(
            "change", lambda e: parent_dict.update({key: e.value.splitlines()})
        )
    elif isinstance(value, int):
        ui.number(key).bind_value(parent_dict, key)
    elif isinstance(value, str):
        ui.input(key).bind_value(parent_dict, key)
    else:
        ui.label(f"{key}: (Unsupported type: {type(value).__name__})")


def add_new_stream():
    """Dialog to add a new stream."""
    with ui.dialog() as dialog, ui.card():
        stream_name = ui.input("Имя потока (Stream Name)").props("autofocus")
        stream_type = ui.select(
            ["Source", "RunOnDemand"], label="Тип потока (Stream Type)"
        )

        def handle_add():
            name = stream_name.value
            stype = stream_type.value
            if not name or not stype:
                ui.notify("Имя и тип потока обязательны!", color="negative")
                return

            if name in data["paths.json"]:
                ui.notify("Поток с таким именем уже существует!", color="negative")
                return

            if stype == "Source":
                data["paths.json"][name] = {
                    "source": "rtsp://",
                    "rtspTransport": "udp",
                    "sourceOnDemand": False,
                }
            elif stype == "RunOnDemand":
                data["paths.json"][name] = {
                    "runOnDemand": "ffmpeg",
                    "runOnDemandRestart": False,
                    "runOnDemandStartTimeout": "10s",
                }

            dialog.close()
            ui.notify(
                f'Поток "{name}" добавлен. Перезагрузите вкладку Paths.',
                color="positive",
            )
            # This is a simple way to refresh the tab content. A more complex solution
            # would involve dynamically adding the UI elements without a full refresh.
            paths_tab_content.clear()
            build_paths_tab(paths_tab_content)

        ui.button("Добавить", on_click=handle_add)
        ui.button("Отмена", on_click=dialog.close)

    dialog.open()


def build_paths_tab(container):
    """Build the content of the 'Paths' tab."""
    with container:
        ui.checkbox(
            "Включить раздел Paths в mediamtx.yml",
            value=data.get("paths.json_enabled", True),
        ).bind_value(data, "paths.json_enabled")
        ui.separator()
        ui.button("Добавить поток", icon="add", on_click=add_new_stream)

        paths_data = data.get("paths.json", {})
        if not paths_data:
            ui.label("Нет настроенных потоков.")
            return

        for stream_name, stream_config in sorted(paths_data.items()):
            with ui.expansion(stream_name, icon="settings_ethernet").classes("w-full"):
                with ui.row().classes("w-full justify-between items-center"):
                    ui.label(stream_name).classes("text-lg")

                    def delete_stream(name):
                        def perform_delete():
                            del data["paths.json"][name]
                            ui.notify(
                                f'Поток "{name}" удален. Перезагрузите вкладку Paths.',
                                color="warning",
                            )
                            paths_tab_content.clear()
                            build_paths_tab(paths_tab_content)

                        with ui.dialog() as dialog, ui.card():
                            ui.label(f'Вы уверены, что хотите удалить поток "{name}"?')
                            with ui.row().classes("w-full justify-end"):
                                ui.button(
                                    "Удалить",
                                    on_click=lambda: (perform_delete(), dialog.close()),
                                )
                                ui.button("Отмена", on_click=dialog.close)
                        dialog.open()

                    ui.button(
                        icon="delete",
                        on_click=lambda name=stream_name: delete_stream(name),
                    ).props("flat color=negative")

                with ui.card_section():
                    for key, value in stream_config.items():
                        create_ui_element(key, value, stream_config)


# --- Main UI Setup ---

with ui.header().classes("bg-primary"):
    ui.label("Mediamtx Configuration Editor").classes("text-2xl")
    ui.space()
    ui.button("Сохранить", on_click=save_and_notify, icon="save", color="positive")

with ui.tabs().classes("w-full") as tabs:
    # Create tabs in a specific order
    sorted_files = sorted(
        [key for key in data.keys() if not key.endswith("_enabled")],
        key=lambda x: list(TAB_NAMES.keys()).index(x) if x in TAB_NAMES else 999,
    )
    for filename in sorted_files:
        if filename in TAB_NAMES:
            ui.tab(TAB_NAMES[filename])

with ui.tab_panels(tabs, value=list(TAB_NAMES.values())[0]).classes("w-full"):
    for filename in sorted_files:
        if filename in TAB_NAMES:
            with ui.tab_panel(TAB_NAMES[filename]):
                ui.label(f"Настройки для {filename}").classes("text-h6")
                if filename == "paths.json":
                    # Special handling for paths
                    paths_tab_content = ui.column().classes("w-full")
                    build_paths_tab(paths_tab_content)
                else:
                    # Generic handling for other JSON files
                    ui.checkbox(
                        "Включить раздел в mediamtx.yml",
                        value=data.get(f"{filename}_enabled", True),
                    ).bind_value(data, f"{filename}_enabled")
                    ui.separator()
                    config_data = data.get(filename, {})
                    for key, value in sorted(config_data.items()):
                        create_ui_element(key, value, config_data)


ui.run()
