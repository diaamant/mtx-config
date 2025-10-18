"""Main application file for Mediamtx Configuration Editor."""

import logging
from typing import Dict, Any

import yaml
from nicegui import ui

from ui_components.generic_tab import build_generic_tab
from ui_components.paths_tab import build_paths_tab
from ui_components.preview_tab import build_preview_tab
from utils.json_utils import load_data, save_data as save_data_core

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

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
    "preview": "Preview",
}

# Data storage
data: Dict[str, Any] = {}
preview_content = {"yaml": ""}


def load_config() -> None:
    """Load configuration data."""
    global data
    try:
        data = load_data()
        logger.info("Configuration loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        ui.notify(f"Ошибка загрузки конфигурации: {e}", color="negative", timeout=5000)


def save_and_notify() -> None:
    """Wrapper to call core save function and show UI notification."""
    try:
        save_data_core(data)
        ui.notify("Конфигурация успешно сохранена!", color="positive")
        logger.info("Configuration saved successfully")
        # Update preview after save
        update_preview()
    except Exception as e:
        logger.error(f"Save failed: {e}", exc_info=True)
        ui.notify(f"Ошибка при сохранении: {e}", color="negative", timeout=5000)


def update_preview() -> None:
    """Update preview with current configuration."""
    try:
        # Assemble configuration like save does
        final_config = {}
        for json_file_name, content in data.items():
            if json_file_name.endswith("_enabled"):
                continue
            if not data.get(f"{json_file_name}_enabled", True):
                continue

            if json_file_name == "paths.json":
                if "paths" not in final_config:
                    final_config["paths"] = {}
                final_config["paths"].update(content)
            elif json_file_name.startswith("values_"):
                key = json_file_name.replace("values_", "").replace(".json", "")
                if key == "app":
                    final_config.update(content)
                else:
                    final_config[key] = content
            else:
                key = json_file_name.replace(".json", "")
                final_config[key] = content

        if "paths" not in final_config:
            final_config["paths"] = {}

        preview_content["yaml"] = yaml.dump(
            final_config, default_flow_style=False, sort_keys=False, allow_unicode=True
        )
    except Exception as e:
        logger.error(f"Preview update failed: {e}")
        preview_content["yaml"] = f"Error generating preview: {e}"


def validate_config() -> None:
    """Validate current configuration and show results."""
    errors = []
    warnings = []

    # Basic validation
    if "paths.json" in data:
        paths = data["paths.json"]
        for stream_name, stream_config in paths.items():
            # Check for required fields based on type
            if "source" in stream_config:
                if not stream_config["source"]:
                    errors.append(f"Stream '{stream_name}': source is empty")
                elif not stream_config["source"].startswith(
                    ("rtsp://", "rtmp://", "http://", "https://")
                ):
                    warnings.append(
                        f"Stream '{stream_name}': source URL format may be invalid"
                    )

            if "runOnDemand" in stream_config:
                if not stream_config["runOnDemand"]:
                    errors.append(f"Stream '{stream_name}': runOnDemand is empty")

            # Check timeout format
            if "runOnDemandStartTimeout" in stream_config:
                timeout = stream_config["runOnDemandStartTimeout"]
                if timeout and not any(timeout.endswith(x) for x in ["s", "m", "h"]):
                    warnings.append(
                        f"Stream '{stream_name}': timeout format should end with s/m/h"
                    )

    # Show results
    if errors:
        ui.notify(f"Ошибки валидации: {len(errors)}", color="negative", timeout=5000)
        for err in errors[:5]:  # Show first 5
            logger.error(f"Validation error: {err}")
    elif warnings:
        ui.notify(f"Предупреждения: {len(warnings)}", color="warning", timeout=3000)
        for warn in warnings[:5]:
            logger.warning(f"Validation warning: {warn}")
    else:
        ui.notify("Валидация пройдена успешно!", color="positive")
        logger.info("Validation passed")


# --- Main UI Setup ---
load_config()

with ui.header().classes("bg-primary"):
    ui.label("Mediamtx Configuration Editor").classes("text-2xl font-bold")
    ui.space()
    ui.button(
        "Валидация", on_click=validate_config, icon="check_circle", color="info"
    ).classes("mr-2")
    ui.button(
        "Предпросмотр", on_click=update_preview, icon="visibility", color="accent"
    ).classes("mr-2")
    ui.button("Сохранить", on_click=save_and_notify, icon="save", color="positive")

with ui.tabs().classes("w-full") as tabs:
    # Create tabs in a specific order
    sorted_files = sorted(
        [key for key in data.keys() if not key.endswith("_enabled")],
        key=lambda x: list(TAB_NAMES.keys()).index(x) if x in TAB_NAMES else 999,
    )
    for filename in sorted_files:
        if filename in TAB_NAMES:
            ui.tab(
                TAB_NAMES[filename],
                icon="settings" if filename != "paths.json" else "stream",
            )

    # Add Preview tab
    preview_tab = ui.tab("Preview", icon="code")

with ui.tab_panels(tabs, value=list(TAB_NAMES.values())[0]).classes("w-full"):
    for filename in sorted_files:
        if filename in TAB_NAMES:
            tab_name = TAB_NAMES[filename]
            if filename == "paths.json":
                with ui.tab_panel(tab_name):
                    paths_tab_content = ui.column().classes("w-full")
                    build_paths_tab(paths_tab_content, data)
            else:
                build_generic_tab(tab_name, filename, data)

    # Preview tab panel
    with ui.tab_panel("Preview"):
        build_preview_tab(preview_content, update_preview)

# Keyboard shortcuts
ui.keyboard(lambda e: save_and_notify() if e.key == "s" and e.modifiers.ctrl else None)

logger.info("Application started")
ui.run(port=8080, title="Mediamtx Configuration Editor")
