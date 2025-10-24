from nicegui import ui


def create_health_route():
    @ui.page('/health')
    def health_check():
        ui.label('OK')
