"""Paths tab component with live updates and search functionality."""

from typing import Dict, Any, Optional, Callable
import asyncio
from nicegui import ui
from .ui_utils import create_ui_element


# Global search filter state
search_filter_state = {"query": "", "type_filter": "all"}

# Debounce timer for search
search_debounce_timer = None


async def debounced_search_update(rebuild_func: Callable, delay: float = 0.3) -> None:
    """Debounced search update to reduce UI binding overhead."""
    global search_debounce_timer

    # Cancel previous timer if exists
    if search_debounce_timer:
        search_debounce_timer.cancel()

    # Create new timer
    search_debounce_timer = asyncio.create_task(asyncio.sleep(delay))

    try:
        await search_debounce_timer
        # Timer completed, perform update
        rebuild_func()
    except asyncio.CancelledError:
        # Timer was cancelled, do nothing
        pass


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
    """Build the content of the 'Paths' tab with search and filter."""

    def get_stream_type(config: Dict[str, Any]) -> str:
        """Determine stream type from configuration."""
        if "source" in config:
            return "Source"
        elif "runOnDemand" in config:
            return "RunOnDemand"
        return "Unknown"

    def filter_streams(
        query: str, type_filter: str, paths_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Filter streams based on search query and type."""
        filtered = {}
        for name, config in paths_data.items():
            # Type filter
            if type_filter != "all":
                stream_type = get_stream_type(config)
                if stream_type != type_filter:
                    continue

            # Name search
            if query and query.lower() not in name.lower():
                continue

            filtered[name] = config
        return filtered

    def rebuild_streams_list():
        """Rebuild the streams list with current filter - optimized version."""
        streams_container.clear()

        paths_data = data.get("paths.json", {})
        if not paths_data:
            with streams_container:
                ui.label("Нет настроенных потоков.").classes(
                    "text-grey-6 text-center p-8"
                )
            return

        # Apply filters
        filtered_paths = filter_streams(
            search_filter_state["query"], search_filter_state["type_filter"], paths_data
        )

        if not filtered_paths:
            with streams_container:
                ui.label("Потоки не найдены по заданным критериям.").classes(
                    "text-grey-6 text-center p-8"
                )
            return

        # Limit displayed streams to prevent too many bindings (pagination-like)
        max_displayed = 50
        stream_names = sorted(filtered_paths.keys())

        if len(stream_names) > max_displayed:
            with streams_container:
                ui.label(f"Найдено {len(stream_names)} потоков. Отображаются первые {max_displayed}:").classes(
                    "text-grey-6 text-center p-4 mb-4"
                )

                # Show first N streams
                displayed_names = stream_names[:max_displayed]
        else:
            displayed_names = stream_names

        with streams_container:
            for stream_name in displayed_names:
                stream_config = filtered_paths[stream_name]
                stream_type = get_stream_type(stream_config)

                # Color-code by type
                icon_name = "videocam" if stream_type == "Source" else "play_arrow"
                badge_color = "teal" if stream_type == "Source" else "orange"

                with ui.expansion(stream_name, icon=icon_name).classes("w-full mb-2"):
                    # Header with actions
                    with ui.row().classes("w-full justify-between items-center mb-2"):
                        with ui.row().classes("items-center gap-2"):
                            ui.label(stream_name).classes("text-lg font-bold")
                            ui.badge(stream_type, color=badge_color).classes("text-xs")

                        with ui.row().classes("gap-1"):
                            ui.button(
                                icon="content_copy",
                                on_click=lambda n=stream_name: clone_stream(
                                    data, n, container, build_paths_tab
                                ),
                            ).props("flat dense").tooltip("Клонировать")

                            ui.button(
                                icon="delete",
                                on_click=lambda n=stream_name: delete_stream_dialog(n),
                            ).props("flat dense color=negative").tooltip("Удалить")

                    ui.separator()

                    # Configuration fields - use optimized display
                    with ui.column().classes("w-full gap-2 p-2"):
                        # Group fields to reduce individual bindings
                        fields_per_group = 5
                        for i in range(0, len(stream_config), fields_per_group):
                            with ui.row().classes("w-full gap-2"):
                                for key in list(stream_config.keys())[i:i + fields_per_group]:
                                    value = stream_config[key]
                                    with ui.column().classes("flex-1"):
                                        ui.label(f"{key}:").classes("text-sm font-medium")
                                        if isinstance(value, (str, int, bool)):
                                            ui.label(str(value)).classes("text-sm text-grey-7")
                                        elif isinstance(value, (list, dict)):
                                            ui.label(f"[{type(value).__name__}]").classes("text-sm text-grey-5")
                                        else:
                                            ui.label(str(value)).classes("text-sm text-grey-7")

    def delete_stream_dialog(name: str) -> None:
        """Show delete confirmation dialog."""

        def perform_delete():
            if "paths.json" in data and name in data["paths.json"]:
                del data["paths.json"][name]
                ui.notify(f'Поток "{name}" удален!', color="warning")
                container.clear()
                build_paths_tab(container, data)
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

    # Build UI
    with container:
        # Header section
        ui.checkbox(
            "Включить раздел Paths в mediamtx.yml",
            value=data.get("paths.json_enabled", True),
        ).bind_value(data, "paths.json_enabled")

        ui.separator()

        # Toolbar
        with ui.row().classes("w-full items-center gap-2 mb-4"):
            search_input = (
                ui.input(
                    placeholder="Поиск потоков...", value=search_filter_state["query"]
                )
                .props("outlined dense")
                .classes("flex-grow")
            )
            search_input.on(
                "input",
                lambda e: (
                    search_filter_state.update({"query": e.value}),
                    asyncio.create_task(debounced_search_update(lambda: rebuild_streams_list())),
                ),
            )

            type_select = (
                ui.select(
                    ["all", "Source", "RunOnDemand"],
                    label="Тип",
                    value=search_filter_state["type_filter"],
                )
                .props("outlined dense")
                .classes("w-40")
            )
            type_select.on(
                "update",
                lambda e: (
                    search_filter_state.update({"type_filter": e.value}),
                    asyncio.create_task(debounced_search_update(lambda: rebuild_streams_list())),
                ),
            )

            ui.button(
                "Добавить поток",
                icon="add",
                on_click=lambda: add_new_stream(data, container, build_paths_tab),
                color="positive",
            )

        # Statistics
        paths_data = data.get("paths.json", {})
        total_streams = len(paths_data)
        source_count = sum(1 for cfg in paths_data.values() if "source" in cfg)
        demand_count = sum(1 for cfg in paths_data.values() if "runOnDemand" in cfg)

        with ui.row().classes("w-full gap-2 mb-4"):
            with ui.card().tight().classes("flex-1"):
                with ui.card_section().classes("text-center"):
                    ui.label(str(total_streams)).classes("text-h4 text-primary")
                    ui.label("Всего потоков").classes("text-caption text-grey-7")

            with ui.card().tight().classes("flex-1"):
                with ui.card_section().classes("text-center"):
                    ui.label(str(source_count)).classes("text-h4 text-teal")
                    ui.label("Source").classes("text-caption text-grey-7")

            with ui.card().tight().classes("flex-1"):
                with ui.card_section().classes("text-center"):
                    ui.label(str(demand_count)).classes("text-h4 text-orange")
                    ui.label("RunOnDemand").classes("text-caption text-grey-7")

        # Streams list container
        streams_container = ui.column().classes("w-full")

        # Initial render
        rebuild_streams_list()
