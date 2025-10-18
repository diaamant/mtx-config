from nicegui import ui
from utils.json_utils import load_data, save_data as save_data_core
from ui_components.generic_tab import build_generic_tab
from ui_components.paths_tab import build_paths_tab

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
    "paths.json": "Paths"
}

# Data storage
data = load_data()

def save_and_notify():
    """Wrapper to call core save function and show UI notification."""
    try:
        save_data_core(data)
        ui.notify('Конфигурация успешно сохранена!', color='positive')
    except Exception as e:
        ui.notify(f'Ошибка при сохранении: {e}', color='negative')

# --- Main UI Setup ---

with ui.header().classes('bg-primary'):
    ui.label('Mediamtx Configuration Editor').classes('text-2xl')
    ui.space()
    ui.button('Сохранить', on_click=save_and_notify, icon='save', color='positive')

with ui.tabs().classes('w-full') as tabs:
    # Create tabs in a specific order
    sorted_files = sorted([key for key in data.keys() if not key.endswith('_enabled')], key=lambda x: list(TAB_NAMES.keys()).index(x) if x in TAB_NAMES else 999)
    for filename in sorted_files:
        if filename in TAB_NAMES:
            ui.tab(TAB_NAMES[filename])

with ui.tab_panels(tabs, value=list(TAB_NAMES.values())[0]).classes('w-full'):
    for filename in sorted_files:
        if filename in TAB_NAMES:
            tab_name = TAB_NAMES[filename]
            if filename == 'paths.json':
                with ui.tab_panel(tab_name):
                    paths_tab_content = ui.column().classes('w-full')
                    build_paths_tab(paths_tab_content, data)
            else:
                build_generic_tab(tab_name, filename, data)

ui.run()