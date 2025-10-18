from nicegui import ui


def create_ui_element(key, value, parent_dict):
    """Create a horizontal key:value UI pair in one row using NiceGUI."""
    with ui.row().classes("w-full items-center no-wrap gap-2"):
        ui.label(f"{key}:").classes("text-sm text-gray-700 whitespace-nowrap")

        el_classes = "flex-grow min-w-0"
        el_props = "dense outlined"

        if isinstance(value, bool):
            ui.checkbox().bind_value(parent_dict, key).classes(el_classes)
        elif isinstance(value, list):
            ui.textarea(value="\n".join(map(str, value))).on(
                "change", lambda e: parent_dict.update({key: e.value.splitlines()})
            ).props(el_props).classes(el_classes)
        elif isinstance(value, int):
            ui.number().bind_value(parent_dict, key).props(el_props).classes(el_classes)
        elif isinstance(value, str):
            ui.input().bind_value(parent_dict, key).props(el_props).classes(el_classes)
        else:
            ui.label(f"Unsupported type: {type(value).__name__}").classes(el_classes)
