from nicegui import ui
from nicegui.events import UploadEventArguments

from src.core.config import get_settings
from src.core.keys import TAB_NAMES
from src.core.log import logger
from src.service.mtx_manager import MtxConfigManager
from src.ui_components.auth_tab import build_auth_tab
from src.ui_components.generic_tab import build_generic_tab
from src.ui_components.paths_tab import build_paths_tab
from src.ui_components.preview_tab import build_preview_tab
from src.ui_components.rtsp_tab import build_rtsp_tab

# Centralized manager for all configuration data
config_manager = MtxConfigManager()


def create_main_page():
    @ui.page("/")
    def main_page():
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
                        with ui.expansion(location, icon="error", value=True).classes(
                            "w-full"
                        ):
                            for err in errs:
                                ui.label(err).classes("text-sm text-red-800 ml-4")

                with ui.row().classes("w-full justify-end mt-4"):
                    ui.button("Закрыть", on_click=dialog.close).props("flat")

            dialog.open()

        def export_config() -> None:
            """Export current configuration to a file."""
            try:
                # Get YAML content from config manager
                yaml_content = config_manager.export_config()

                # Create a download link
                ui.download.content(
                    content=yaml_content,
                    filename="mediamtx_config.yaml",
                )

                ui.notify("Конфигурация успешно экспортирована!", color="positive")
                logger.info("Configuration exported successfully")

            except Exception as e:
                logger.error(f"Export failed: {e}", exc_info=True)
                ui.notify(f"Ошибка при экспорте: {e}", color="negative", timeout=5000)

        async def handle_import(upload_event: UploadEventArguments) -> None:
            """Handle file upload for import.

            Args:
                upload_event: UploadEventArguments object containing file information
            """
            try:
                # Check if content exists
                if not hasattr(upload_event, "file") or not upload_event.file:
                    ui.notify("Файл не загружен или пустой", color="warning")
                    return

                # 2. Использовать await для чтения байтов и затем декодировать
                content_bytes = await upload_event.file.read()
                content = content_bytes.decode("utf-8")

                # 1. Import configuration (updates in-memory manager)
                config_manager.import_config(content)

                # 2. (Важно) Save the imported data to disk *before* reloading
                config_manager.save_data()

                # 3. Update preview
                config_manager.update_preview()

                ui.notify(
                    "Конфигурация успешно импортирована! Перезагрузка...",
                    color="positive",
                )
                logger.info("Configuration imported successfully. Reloading UI.")

                # 4. Force page reload to reflect changes
                ui.navigate.to("/")

            except UnicodeDecodeError as e:
                logger.error(f"Failed to decode file content: {e}")
                ui.notify(
                    "Ошибка кодировки файла. Поддерживается только UTF-8",
                    color="negative",
                    timeout=5000,
                )
            except Exception as e:
                logger.error(f"Import failed: {e}", exc_info=True)
                ui.notify(f"Ошибка при импорте: {e}", color="negative", timeout=5000)

        # --- Main UI Setup ---
        config_manager.load_data()
        config_manager.update_preview()

        with ui.header().classes("bg-primary"):
            ui.label("Mediamtx Configuration Editor").classes("text-2xl font-bold")
            ui.space()

            ui.upload(
                on_upload=handle_import,
                auto_upload=True,
                multiple=False,
            ).props('accept=".yaml,.yml" icon="upload" color="accent"').classes(
                "mr-2"
            ).tooltip("Импорт конфигурации")

            # Export button
            with (
                ui.button(icon="download", color="accent")
                .classes("mr-2")
                .tooltip("Экспорт конфигурации") as export_btn
            ):
                export_btn.on("click", export_config)
                ui.label("Экспорт")

            ui.button(
                "Сохранить", on_click=save_and_notify, icon="save", color="positive"
            ).tooltip("Сохранить конфигурацию")

        with ui.tabs().classes("w-full") as tabs:
            # Create tabs in a specific order
            sorted_files = sorted(
                [
                    key
                    for key in config_manager.data.keys()
                    if not key.endswith("_enabled")
                ],
                key=lambda x: list(TAB_NAMES.keys()).index(x)
                if x in TAB_NAMES
                else 999,
            )
            for filename in sorted_files:
                if filename in TAB_NAMES:
                    ui.tab(
                        TAB_NAMES[filename],
                        icon="settings" if filename != "paths" else "stream",
                    )

            # Add Preview tab
            preview_tab = ui.tab("Preview", icon="code")

        with ui.tab_panels(tabs, value=list(TAB_NAMES.values())[0]).classes("w-full"):
            for filename in sorted_files:
                if filename in TAB_NAMES:
                    tab_name = TAB_NAMES[filename]
                    if filename == "auth":
                        with ui.tab_panel(tab_name):
                            auth_tab_content = ui.column().classes("w-full")
                            auth_data = config_manager.data.get("auth", {})
                            build_auth_tab(auth_tab_content, auth_data)
                    elif filename == "rtsp":
                        with ui.tab_panel(tab_name):
                            rtsp_tab_content = ui.column().classes("w-full")
                            with rtsp_tab_content:
                                ui.checkbox(
                                    "Включить раздел Paths в mediamtx.yml",
                                    value=config_manager.get("paths_enabled", True),
                                ).bind_value(config_manager.data, "paths_enabled")
                                ui.separator()
                            build_rtsp_tab(rtsp_tab_content, config_manager.data)
                    elif filename == "paths":
                        with ui.tab_panel(tab_name):
                            paths_tab_content = ui.column().classes("w-full")
                            paths_data = config_manager.data.get("paths", {})
                            build_paths_tab(paths_tab_content, paths_data)
                    else:
                        build_generic_tab(tab_name, filename, config_manager.data)

            # Preview tab panel
            with ui.tab_panel("Preview"):
                build_preview_tab(
                    config_manager.preview_content, config_manager.update_preview
                )

        # Keyboard shortcuts
        ui.keyboard(
            lambda e: save_and_notify() if e.key == "s" and e.modifiers.ctrl else None
        )
