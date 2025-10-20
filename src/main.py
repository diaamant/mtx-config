from nicegui import ui

from src.core.log import logger
from src.mtx_manager import MtxConfigManager
from ui_components.generic_tab import build_generic_tab
from ui_components.paths_tab import build_paths_tab
from ui_components.preview_tab import build_preview_tab
from utils.yaml_utils import save_data as save_data_core

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

# Centralized manager for all configuration data
config_manager = MtxConfigManager()


def save_and_notify() -> None:
    """Wrapper to call core save function and show UI notification."""
    try:
        save_data_core(config_manager.data)
        ui.notify("Конфигурация успешно сохранена!", color="positive")
        logger.info("Configuration saved successfully")
        # Update preview after save
        config_manager.update_preview()
    except Exception as e:
        logger.error(f"Save failed: {e}", exc_info=True)
        ui.notify(f"Ошибка при сохранении: {e}", color="negative", timeout=5000)


def validate_config() -> None:
    """Validate current configuration and show results."""
    errors = config_manager.validate_all()

    if errors:
        error_count = sum(len(e) for e in errors.values())
        ui.notify(f"Ошибки валидации: {error_count}", color="negative", timeout=5000)
        for location, errs in errors.items():
            for err in errs:
                logger.error(f"Validation error in {location}: {err}")
    else:
        ui.notify("Валидация пройдена успешно!", color="positive")
        logger.info("Validation passed")


# --- Main UI Setup ---
config_manager.load_data()
config_manager.update_preview()

with ui.header().classes("bg-primary"):
    ui.label("Mediamtx Configuration Editor").classes("text-2xl font-bold")
    ui.space()
    ui.button(
        "Валидация", on_click=validate_config, icon="check_circle", color="info"
    ).classes("mr-2")
    ui.button(
        "Предпросмотр",
        on_click=config_manager.update_preview,
        icon="visibility",
        color="accent",
    ).classes("mr-2")
    ui.button("Сохранить", on_click=save_and_notify, icon="save", color="positive")


with ui.tabs().classes("w-full") as tabs:
    # Create tabs in a specific order
    sorted_files = sorted(
        [key for key in config_manager.data.keys() if not key.endswith("_enabled")],
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
                    build_paths_tab(paths_tab_content, config_manager.data)
            else:
                build_generic_tab(tab_name, filename, config_manager.data)

    # Preview tab panel
    with ui.tab_panel("Preview"):
        build_preview_tab(config_manager.preview_content, config_manager.update_preview)


# Keyboard shortcuts
ui.keyboard(lambda e: save_and_notify() if e.key == "s" and e.modifiers.ctrl else None)

logger.info("Application started")
ui.run(port=8080, title="Mediamtx Configuration Editor")
