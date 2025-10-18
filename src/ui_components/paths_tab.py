
from nicegui import ui
from .ui_utils import create_ui_element

def add_new_stream(data, paths_tab_content, build_paths_tab_func):
    """Dialog to add a new stream."""
    with ui.dialog() as dialog, ui.card():
        stream_name = ui.input('Имя потока (Stream Name)').props('autofocus')
        stream_type = ui.select(['Source', 'RunOnDemand'], label='Тип потока (Stream Type)')

        def handle_add():
            name = stream_name.value
            stype = stream_type.value
            if not name or not stype:
                ui.notify('Имя и тип потока обязательны!', color='negative')
                return

            if name in data['paths.json']:
                ui.notify('Поток с таким именем уже существует!', color='negative')
                return

            if stype == 'Source':
                data['paths.json'][name] = {
                    "source": "rtsp://",
                    "rtspTransport": "udp",
                    "sourceOnDemand": False
                }
            elif stype == 'RunOnDemand':
                 data['paths.json'][name] = {
                    "runOnDemand": "ffmpeg",
                    "runOnDemandRestart": False,
                    "runOnDemandStartTimeout": "10s"
                }
            
            dialog.close()
            ui.notify(f'Поток "{name}" добавлен. Перезагрузите вкладку Paths.', color='positive')
            paths_tab_content.clear()
            build_paths_tab_func(paths_tab_content, data)


        ui.button('Добавить', on_click=handle_add)
        ui.button('Отмена', on_click=dialog.close)

    dialog.open()

def build_paths_tab(container, data):
    """Build the content of the 'Paths' tab."""
    with container:
        ui.checkbox('Включить раздел Paths в mediamtx.yml', value=data.get('paths.json_enabled', True)).bind_value(data, 'paths.json_enabled')
        ui.separator()
        ui.button('Добавить поток', icon='add', on_click=lambda: add_new_stream(data, container, build_paths_tab))
        
        paths_data = data.get('paths.json', {})
        if not paths_data:
            ui.label("Нет настроенных потоков.")
            return

        for stream_name, stream_config in sorted(paths_data.items()):
            with ui.expansion(stream_name, icon='settings_ethernet').classes('w-full'):
                with ui.row().classes('w-full justify-between items-center'):
                    ui.label(stream_name).classes('text-lg')
                    def delete_stream(name):
                        def perform_delete():
                            del data['paths.json'][name]
                            ui.notify(f'Поток "{name}" удален. Перезагрузите вкладку Paths.', color='warning')
                            container.clear()
                            build_paths_tab(container, data)

                        with ui.dialog() as dialog, ui.card():
                            ui.label(f'Вы уверены, что хотите удалить поток "{name}"?')
                            with ui.row().classes('w-full justify-end'):
                                ui.button('Удалить', on_click=lambda: (perform_delete(), dialog.close()))
                                ui.button('Отмена', on_click=dialog.close)
                        dialog.open()

                    ui.button(icon='delete', on_click=lambda name=stream_name: delete_stream(name)).props('flat color=negative')

                with ui.card_section():
                    for key, value in stream_config.items():
                        create_ui_element(key, value, stream_config)
