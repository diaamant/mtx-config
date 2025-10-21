"""UI utility functions for creating form elements."""

from typing import Any, Dict, Union
from nicegui import ui

el_classes = "flex-grow min-w-0"
el_props = "dense outlined"


def create_ui_checkbox(key: str, value: Any, parent_dict: Dict[str, Any]):
    ui.checkbox().bind_value(parent_dict, key).classes(el_classes)


def create_ui_int(key: str, value: Any, parent_dict: Dict[str, Any]):
    ui.number(value=value, min=0).bind_value(parent_dict, key).props(el_props).classes(
        el_classes
    )


def create_ui_str(key: str, value: Any, parent_dict: Dict[str, Any]):
    # Use textarea for long strings
    if len(value) > 100:
        ui.textarea(value=value, placeholder=f"Введите {key}").bind_value(
            parent_dict, key
        ).props(el_props).classes(el_classes)
    else:
        ui.input(value=value, placeholder=f"Введите {key}").bind_value(
            parent_dict, key
        ).props(el_props).classes(el_classes)


def create_ui_list(key: str, value: Any, parent_dict: Dict[str, Any]):
    # Handle lists with proper filtering of empty lines
    ui.textarea(
        value="\n".join(map(str, value)),
        placeholder="Введите значения, каждое с новой строки",
    ).on(
        "change",
        lambda e, k=key: parent_dict.update(
            {k: [line for line in e.value.splitlines() if line.strip()]}
        ),
    ).props(el_props).classes(el_classes)


def create_ui_dict(key: str, value: Any, parent_dict: Dict[str, Any]):
    # Handle dictionaries recursively
    with ui.expansion(key, icon="schema").classes("w-full border rounded-lg"):
        with ui.column().classes("w-full p-2"):
            for sub_key, sub_value in value.items():
                create_ui_element(sub_key, sub_value, value)


def create_ui_element(key: str, value: Any, parent_dict: Dict[str, Any]) -> None:
    """Create a horizontal key:value UI pair with top-aligned label using NiceGUI.

    Args:
        key: Configuration key name
        value: Configuration value (can be bool, int, str, list)
        parent_dict: Parent dictionary to bind the value to
    """
    with ui.row().classes("w-full items-start gap-2 mb-1"):
        # Label with tooltip
        label_element = ui.label(f"{key}:").classes(
            "text-sm font-medium text-gray-700 self-start whitespace-nowrap min-w-[200px]"
        )

        # Add tooltip for common parameters
        tooltip_text = get_parameter_tooltip(key)
        if tooltip_text:
            label_element.tooltip(tooltip_text)

        if value is None:
            ui.label("None").classes(el_classes)
        elif isinstance(value, bool):
            create_ui_checkbox(key, value, parent_dict)
        elif isinstance(value, list):
            create_ui_list(key, value, parent_dict)
        elif isinstance(value, int):
            create_ui_int(key, value, parent_dict)
        elif isinstance(value, str):
            create_ui_str(key, value, parent_dict)
        elif isinstance(value, dict):
            create_ui_dict(key, value, parent_dict)


def get_parameter_tooltip(param_name: str) -> str:
    """Get tooltip text for common configuration parameters.

    Args:
        param_name: Parameter name

    Returns:
        Tooltip text or empty string if no tooltip available
    """
    tooltips = {
        "source": "URL источника потока (rtsp://, rtmp://, http://)",
        "rtspTransport": "Протокол транспорта RTSP: udp, tcp или auto",
        "sourceOnDemand": "Запускать источник только при подключении клиента",
        "runOnDemand": "Команда для запуска по требованию (например, ffmpeg, gstreamer)",
        "runOnDemandRestart": "Перезапускать процесс при завершении",
        "runOnReadyRestart": "Перезапускать процесс когда поток готов",
        "runOnDemandStartTimeout": "Таймаут запуска (формат: 10s, 5m, 1h)",
        "rtsp": "Включить RTSP сервер",
        "rtspAddress": "Адрес RTSP сервера (например: :8554)",
        "rtspEncryption": "Шифрование: no, optional, strict",
        "webrtc": "Включить WebRTC сервер",
        "hls": "Включить HLS сервер",
        "hlsVariant": "Вариант HLS: lowLatency или fmp4",
        "hlsSegmentDuration": "Длительность сегмента HLS",
        "authMethod": "Метод аутентификации: internal, jwt, http",
        "logLevel": "Уровень логирования: debug, info, warn, error",
    }
    return tooltips.get(param_name, "")
