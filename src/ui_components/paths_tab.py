"""Paths tab component with live updates and search functionality."""

from typing import Dict, Any, Optional, Callable
import asyncio
from nicegui import ui
from .ui_utils import create_ui_element


class SearchState:
    """Encapsulates search and filter state for the paths tab."""

    def __init__(self, rebuild_func: Callable):
        self.query: str = ""
        self.type_filter: str = "all"
        self.debounce_timer: Optional[asyncio.Task] = None
        self.rebuild_func = rebuild_func

    async def debounced_update(self, delay: float = 0.5) -> None:
        """Debounce UI updates to reduce overhead."""
        if self.debounce_timer:
            self.debounce_timer.cancel()

        self.debounce_timer = asyncio.create_task(asyncio.sleep(delay))
        try:
            await self.debounce_timer
            self.rebuild_func()
        except asyncio.CancelledError:
            pass

    def set_query(self, query: str):
        self.query = query
        asyncio.create_task(self.debounced_update())

    def set_type_filter(self, type_filter: str):
        self.type_filter = type_filter
        asyncio.create_task(self.debounced_update())


def add_new_stream(data: Dict[str, Any], container, rebuild_func: Callable) -> None:
    """Dialog to add a new stream with live update."""
    with ui.dialog() as dialog, ui.card():
        ui.label("Добавить новый поток").classes("text-h6 mb-4")

        stream_name = ui.input(
            "Имя потока (Stream Name)", placeholder="например: camera01"
        ).props("autofocus outlined")
        stream_type = ui.select(
            ["Source", "RunOnDemand"], label="Тип потока (Stream Type)", value="Source"
        ).props("outlined")

        def handle_add():
            name = stream_name.value
            stype = stream_type.value

            if not name or not stype:
                ui.notify("Имя и тип потока обязательны!", color="negative")
                return

            if name in data.get("paths.json", {}):
                ui.notify("Поток с таким именем уже существует!", color="negative")
                return

            # Ensure paths.json exists
            if "paths.json" not in data:
                data["paths.json"] = {}

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
            ui.notify(f'Поток "{name}" добавлен!', color="positive")

            # Live update - rebuild the container
            container.clear()
            rebuild_func(container, data)

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Отмена", on_click=dialog.close).props("flat")
            ui.button("Добавить", on_click=handle_add, icon="add", color="positive")

    dialog.open()


def clone_stream(
    data: Dict[str, Any], source_name: str, container, rebuild_func: Callable
) -> None:
    """Dialog to clone an existing stream."""
    with ui.dialog() as dialog, ui.card():
        ui.label(f"Клонировать поток: {source_name}").classes("text-h6 mb-4")

        new_name = ui.input(
            "Новое имя потока",
            placeholder=f"{source_name}_copy",
            value=f"{source_name}_copy",
        ).props("autofocus outlined")

        def handle_clone():
            name = new_name.value

            if not name:
                ui.notify("Имя потока обязательно!", color="negative")
                return

            if name in data.get("paths.json", {}):
                ui.notify("Поток с таким именем уже существует!", color="negative")
                return

            # Clone the configuration
            source_config = data["paths.json"][source_name]
            data["paths.json"][name] = source_config.copy()

            dialog.close()
            ui.notify(
                f'Поток "{name}" создан как копия "{source_name}"!', color="positive"
            )

            # Live update
            container.clear()
            rebuild_func(container, data)

        with ui.row().classes("w-full justify-end gap-2 mt-4"):
            ui.button("Отмена", on_click=dialog.close).props("flat")
            ui.button(
                "Клонировать",
                on_click=handle_clone,
                icon="content_copy",
                color="primary",
            )

    dialog.open()


def build_paths_tab(container, data: Dict[str, Any]) -> None:
    """Build the content of the 'Paths' tab with search, filter, and grouping."""

    def get_stream_type(config: Dict[str, Any]) -> str:
        """Determine stream type from configuration."""
        if "source" in config:
            return "Source"
        elif "runOnDemand" in config:
            return "RunOnDemand"
        return "Unknown"

    def rebuild_streams_list():
        """Rebuild the streams list with current filters and grouping."""
        streams_container.clear()

        paths_data = data.get("paths.json", {})
        if not paths_data:
            with streams_container:
                ui.label("Нет настроенных потоков.").classes(
                    "text-grey-6 text-center p-8"
                )
            return

        # Apply filters
        filtered_paths = {
            name: config
            for name, config in paths_data.items()
            if (search_state.query.lower() in name.lower())
            and (
                search_state.type_filter == "all"
                or get_stream_type(config) == search_state.type_filter
            )
        }

        if not filtered_paths:
            with streams_container:
                ui.label("Потоки не найдены по заданным критериям.").classes(
                    "text-grey-6 text-center p-8"
                )
            return

        # Group streams by type
        grouped_streams = {"Source": {}, "RunOnDemand": {}, "Unknown": {}}
        for name, config in filtered_paths.items():
            stream_type = get_stream_type(config)
            grouped_streams[stream_type][name] = config

        with streams_container:
            for stream_type, streams in grouped_streams.items():
                if not streams:
                    continue

                with ui.column().classes("w-full mb-4"):
                    ui.label(f"{stream_type} Streams ({len(streams)})").classes(
                        "text-lg font-semibold text-primary border-b-2 border-primary pb-1"
                    )
                    for stream_name, stream_config in sorted(streams.items()):
                        icon_name = (
                            "videocam" if stream_type == "Source" else "play_arrow"
                        )
                        with ui.expansion(stream_name, icon=icon_name).classes(
                            "w-full mb-2"
                        ):
                            # Header with actions
                            with ui.row().classes(
                                "w-full justify-between items-center"
                            ):
                                ui.label(stream_name).classes("text-lg font-bold")
                                with ui.row().classes("gap-1"):
                                    ui.button(
                                        icon="content_copy",
                                        on_click=lambda n=stream_name: clone_stream(
                                            data, n, container, build_paths_tab
                                        ),
                                    ).props("flat dense").tooltip("Клонировать")
                                    ui.button(
                                        icon="delete",
                                        on_click=lambda n=stream_name: delete_stream_dialog(
                                            n
                                        ),
                                    ).props(
                                        "flat dense color=negative"
                                    ).tooltip("Удалить")

                            ui.separator()
                            # Editable configuration fields
                            with ui.column().classes("w-full gap-1 p-2"):
                                for key, value in stream_config.items():
                                    create_ui_element(key, value, stream_config)

    def delete_stream_dialog(name: str) -> None:
        """Show delete confirmation dialog."""

        def perform_delete():
            if "paths.json" in data and name in data["paths.json"]:
                del data["paths.json"][name]
                ui.notify(f'Поток "{name}" удален!', color="warning")
                rebuild_streams_list()  # Just rebuild the list
            dialog.close()

        with ui.dialog() as dialog, ui.card():
            ui.label(f'Удалить поток "{name}"?').classes("text-h6 mb-2")
            ui.label("Это действие нельзя отменить.").classes("text-grey-7 mb-4")
            with ui.row().classes("w-full justify-end gap-2"):
                ui.button("Отмена", on_click=dialog.close).props("flat")
                ui.button(
                    "Удалить", on_click=perform_delete, color="negative", icon="delete"
                )
        dialog.open()

    # --- UI Build ---
    search_state = SearchState(rebuild_streams_list)

    with container:
        ui.checkbox(
            "Включить раздел Paths в mediamtx.yml",
            value=data.get("paths.json_enabled", True),
        ).bind_value(data, "paths.json_enabled")
        ui.separator()

        # Toolbar
        with ui.row().classes("w-full items-center gap-2 mb-4"):
            ui.input(
                placeholder="Поиск потоков...", on_change=lambda e: search_state.set_query(e.value)
            ).props("outlined dense").classes("flex-grow")
            ui.select(
                ["all", "Source", "RunOnDemand"],
                label="Тип",
                value="all",
                on_change=lambda e: search_state.set_type_filter(e.value),
            ).props("outlined dense").classes("w-40")
            ui.button(
                "Добавить поток",
                icon="add",
                on_click=lambda: add_new_stream(data, container, build_paths_tab),
                color="positive",
            )

        # Statistics cards (can be removed or kept as is)
        # ...

        # Streams list container
        streams_container = ui.column().classes("w-full")
        rebuild_streams_list()
