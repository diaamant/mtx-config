from nicegui import ui

def create_ui_element(key, value, parent_dict):
    """Dynamically create a UI element based on the value's type."""
    if isinstance(value, bool):
        ui.checkbox(key).bind_value(parent_dict, key)
    elif isinstance(value, list):
        # Using textarea for lists as it's simpler to manage for various list types.
        ui.textarea(key, value='\n'.join(map(str, value))).on('change', lambda e: parent_dict.update({key: e.value.splitlines()}))
    elif isinstance(value, int):
        ui.number(key).bind_value(parent_dict, key)
    elif isinstance(value, str):
        ui.input(key).bind_value(parent_dict, key)
    else:
        ui.label(f"{key}: (Unsupported type: {type(value).__name__})")
