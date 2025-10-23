"""RTSP tab component with detailed settings."""

from typing import Dict, Any
from nicegui import ui
from .ui_utils import create_ui_element


def build_rtsp_tab(container: ui.element, data: Dict[str, Any]):
    """Builds the RTSP tab with organized sections for better readability."""
    rtsp_data = data.get("values_rtsp.json", {})

    if not rtsp_data:
        ui.label("RTSP configuration (values_rtsp.json) not found.").classes(
            "text-negative"
        )
        return

    with container:
        # --- General Settings ---
        with ui.card().classes("w-full mb-4"):
            with ui.card_section():
                ui.label("General RTSP Settings").classes("text-lg font-bold")
            create_ui_element("rtsp", rtsp_data.get("rtsp"), rtsp_data)
            create_ui_element(
                "rtspEncryption", rtsp_data.get("rtspEncryption"), rtsp_data
            )
            create_ui_element(
                "rtspTransports", rtsp_data.get("rtspTransports"), rtsp_data
            )
            create_ui_element(
                "rtspAuthMethods", rtsp_data.get("rtspAuthMethods"), rtsp_data
            )

        # --- Network Addresses and Ports ---
        with ui.card().classes("w-full mb-4"):
            with ui.card_section():
                ui.label("Network Addresses and Ports").classes("text-lg font-bold")
            with ui.row().classes("w-full"):
                create_ui_element(
                    "rtspAddress", rtsp_data.get("rtspAddress"), rtsp_data
                )
                create_ui_element(
                    "rtspsAddress", rtsp_data.get("rtspsAddress"), rtsp_data
                )
            with ui.row().classes("w-full"):
                create_ui_element("rtpAddress", rtsp_data.get("rtpAddress"), rtsp_data)
                create_ui_element(
                    "rtcpAddress", rtsp_data.get("rtcpAddress"), rtsp_data
                )

        # --- Multicast Settings ---
        with ui.card().classes("w-full mb-4"):
            with ui.card_section():
                ui.label("Multicast Settings").classes("text-lg font-bold")
            create_ui_element(
                "multicastIPRange", rtsp_data.get("multicastIPRange"), rtsp_data
            )
            with ui.row().classes("w-full"):
                create_ui_element(
                    "multicastRTPPort", rtsp_data.get("multicastRTPPort"), rtsp_data
                )
                create_ui_element(
                    "multicastRTCPPort", rtsp_data.get("multicastRTCPPort"), rtsp_data
                )
            with ui.row().classes("w-full"):
                create_ui_element(
                    "multicastSRTPPort", rtsp_data.get("multicastSRTPPort"), rtsp_data
                )
                create_ui_element(
                    "multicastSRTCPPort", rtsp_data.get("multicastSRTCPPort"), rtsp_data
                )

        # --- Security (TLS/SSL) ---
        with ui.card().classes("w-full mb-4"):
            with ui.card_section():
                ui.label("Security (TLS/SSL)").classes("text-lg font-bold")
            create_ui_element(
                "rtspServerKey", rtsp_data.get("rtspServerKey"), rtsp_data
            )
            create_ui_element(
                "rtspServerCert", rtsp_data.get("rtspServerCert"), rtsp_data
            )

        # --- Advanced / Other ---
        with ui.card().classes("w-full"):
            with ui.card_section():
                ui.label("Advanced").classes("text-lg font-bold")
            create_ui_element(
                "rtspUDPReadBufferSize",
                rtsp_data.get("rtspUDPReadBufferSize"),
                rtsp_data,
            )
