"""Auth tab component with detailed user management."""

from typing import Dict, Any
from nicegui import ui
from .ui_utils import create_ui_element
import json


def build_auth_tab(container: ui.element, auth_data: Dict[str, Any]):
    """Build the content of the 'Auth' tab with special handling for internal users."""

    if not auth_data:
        ui.label("Auth configuration (auth) not found.").classes("text-negative")
        return

    def rebuild_users_list():
        """Clear and rebuild the UI for the internal users list."""
        users_container.clear()
        users = auth_data.get("authInternalUsers", [])

        with users_container:
            if not users:
                ui.label("No internal users defined.").classes("text-grey-6 p-4")
                return

            for i, user_config in enumerate(users):
                user_label = user_config.get("user", f"User {i + 1}")
                with ui.expansion(user_label, icon="person").classes(
                    "w-full mb-2 border rounded-lg"
                ):
                    # --- User and Password ---
                    with ui.row().classes("w-full gap-4 p-2"):
                        ui.input(label="User").bind_value(user_config, "user").classes(
                            "flex-1"
                        ).on(
                            "change",
                            lambda e, u=user_config: u.update({"user": e.value}),
                        )
                        ui.input(
                            label="Password", password=True, password_toggle_button=True
                        ).bind_value(user_config, "pass").classes("flex-1")

                    # --- IPs ---
                    ui.label("IPs").classes("text-sm font-medium px-2")
                    ips_str = "\n".join(user_config.get("ips", []))
                    ui.textarea(
                        value=ips_str, placeholder="One IP or CIDR per line"
                    ).on(
                        "change",
                        lambda e, u=user_config: u.update(
                            {
                                "ips": [
                                    line
                                    for line in e.value.splitlines()
                                    if line.strip()
                                ]
                            }
                        ),
                    ).props("outlined dense").classes("w-full px-2")

                    # --- Permissions ---
                    ui.label("Permissions (JSON format)").classes(
                        "text-sm font-medium px-2"
                    )
                    try:
                        permissions_str = json.dumps(
                            user_config.get("permissions", []), indent=2
                        )
                    except TypeError:
                        permissions_str = "[]"

                    ui.textarea(value=permissions_str).on(
                        "change",
                        lambda e, u=user_config: u.update(
                            {"permissions": json.loads(e.value)}
                        ),
                    ).props("outlined dense").classes("w-full px-2")

                    # --- Actions ---
                    with ui.row().classes("w-full justify-end p-2"):
                        ui.button(
                            "Delete User",
                            on_click=lambda _, idx=i: delete_user(idx),
                            color="negative",
                            icon="delete",
                        ).props("flat dense")

    def add_user():
        """Add a new blank user to the list and refresh the UI."""
        users = auth_data.setdefault("authInternalUsers", [])
        users.append(
            {
                "user": "new_user",
                "pass": "changeme",
                "ips": ["127.0.0.1", "::1"],
                "permissions": [{"action": "read"}, {"action": "publish"}],
            }
        )
        rebuild_users_list()
        ui.notify("New user added. Please edit the details.", color="positive")

    def delete_user(index: int):
        """Delete a user by index and refresh the UI."""
        users = auth_data.get("authInternalUsers", [])
        if 0 <= index < len(users):
            del users[index]
            rebuild_users_list()
            ui.notify("User deleted.", color="warning")

    with container:
        # --- General Auth Settings ---
        for key, value in auth_data.items():
            if key != "authInternalUsers":
                create_ui_element(key, value, auth_data)

        ui.separator().classes("my-4")

        # --- Internal Users Section ---
        with ui.card().classes("w-full"):
            with ui.card_section():
                ui.label("Internal Users").classes("text-lg font-bold")
                ui.label(
                    "Manage users for the 'internal' authentication method."
                ).classes("text-sm text-grey-7")

            users_container = ui.column().classes("w-full p-2")
            rebuild_users_list()

            with ui.card_actions().classes("w-full justify-end"):
                ui.button(
                    "Refresh",
                    on_click=rebuild_users_list,
                    icon="refresh",
                    color="accent",
                ).tooltip("Refresh the list to reflect name changes")
                ui.button(
                    "Add User", on_click=add_user, icon="person_add", color="positive"
                )
