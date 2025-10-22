from nicegui import ui

from src.core.config import get_settings
from src.core.log import logger
from src.mtx_manager import MtxConfigManager
from ui_components.auth_tab import build_auth_tab
from ui_components.generic_tab import build_generic_tab
from ui_components.paths_tab import build_paths_tab
from ui_components.preview_tab import build_preview_tab
from ui_components.rtsp_tab import build_rtsp_tab

# Tab names mapping
TAB_NAMES = {
    "values_app.json": "App",
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
    """Wrapper to call save function and show UI notification."""
    try:
        config_manager.save_data()
        ui.notify("Конфигурация успешно сохранена!", color="positive")
        logger.info("Configuration saved successfully")
        # Update preview after save
        config_manager.update_preview()
    except Exception as e:
        logger.error(f"Save failed: {e}", exc_info=True)
        ui.notify(f"Ошибка при сохранении: {e}", color="negative", timeout=5000)


def validate_config() -> None:
    """Validate current configuration and show results in a dialog."""
    errors = config_manager.validate_all()

    if not errors:
        ui.notify("Валидация пройдена успешно!", color="positive")
        logger.info("Validation passed")
        return

    with ui.dialog() as dialog, ui.card().classes("w-full max-w-2xl"):
        ui.label("Ошибки валидации").classes("text-h6 text-negative mb-4")
        error_count = sum(len(e) for e in errors.values())
        ui.label(f"Найдено ошибок: {error_count}").classes("mb-4")

        with ui.scroll_area().classes("h-64 border p-2"):
            for location, errs in errors.items():
                with ui.expansion(location, icon="error", value=True).classes("w-full"):
                    for err in errs:
                        ui.label(err).classes("text-sm text-red-800 ml-4")

        with ui.row().classes("w-full justify-end mt-4"):
            ui.button("Закрыть", on_click=dialog.close).props("flat")

    dialog.open()


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
            elif filename == "auth.json":
                with ui.tab_panel(tab_name):
                    auth_tab_content = ui.column().classes("w-full")
                    build_auth_tab(auth_tab_content, config_manager.data)
            elif filename == "values_rtsp.json":
                with ui.tab_panel(tab_name):
                    rtsp_tab_content = ui.column().classes("w-full")
                    build_rtsp_tab(rtsp_tab_content, config_manager.data)
            else:
                build_generic_tab(tab_name, filename, config_manager.data)

    # Preview tab panel
    with ui.tab_panel("Preview"):
        build_preview_tab(config_manager.preview_content, config_manager.update_preview)


# Keyboard shortcuts
ui.keyboard(lambda e: save_and_notify() if e.key == "s" and e.modifiers.ctrl else None)


logger.info("Application started")
settings = get_settings()

ui.run(
    port=settings.app_port,
    host=settings.app_host,
    title="Mediamtx Configuration Editor",
    reload=False,
)
