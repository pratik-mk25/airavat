"""
Mission Map & Digital Twin View Widget.
Embeds high-resolution WebGL/Leaflet Digital Twin map inside PySide6 via QWebEngineView.
Standardized typography for Wind Speed badge matching Zoom Controls (11px, font-weight: 800).
"""

import os
import json
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import QUrl, Slot
from PySide6.QtWebEngineWidgets import QWebEngineView

class MapPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("MapPanel")
        self.setStyleSheet("""
            #MapPanel {
                background-color: #0d1321;
                border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 8px;
            }
            .panel-header {
                font-size: 12px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 1.2px;
            }
            .wind-badge {
                background: rgba(13, 19, 33, 0.85);
                border: 1.5px solid rgba(0, 240, 255, 0.4);
                border-radius: 4px;
                padding: 2px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 0.8px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(2)

        # Header Bar Container: Title (Left) + Wind Speed Vector (Right Corner - Standardized 11px font)
        top_bar = QWidget()
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(4, 2, 4, 2)

        lbl_head = QLabel("MISSION MAP VIEW")
        lbl_head.setProperty("class", "panel-header")

        self.lbl_wind_vector = QLabel("💨 WIND: 4.2 m/s")
        self.lbl_wind_vector.setProperty("class", "wind-badge")

        tb_layout.addWidget(lbl_head)
        tb_layout.addStretch()
        tb_layout.addWidget(self.lbl_wind_vector)

        layout.addWidget(top_bar)

        # WebEngine View for rendering 3D Digital Twin Map
        self.web_view = QWebEngineView(self)
        
        # Load local map_template.html
        asset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "map_template.html"))
        if os.path.exists(asset_path):
            self.web_view.load(QUrl.fromLocalFile(asset_path))
        else:
            print(f"[MAP_PANEL] Asset path not found: {asset_path}")

        layout.addWidget(self.web_view, stretch=1)

    @Slot(dict)
    def update_map(self, telemetry):
        """Passes real-time telemetry frame to JavaScript map renderer."""
        if not telemetry:
            return
        
        # Update Wind Speed readout in header bar (OUTSIDE map outline)
        wind_data = telemetry.get("wind", {})
        wind_speed = wind_data.get("speed", 4.2)
        self.lbl_wind_vector.setText(f"💨 WIND: {wind_speed:.1f} m/s")

        # Convert dictionary to JSON string safely
        json_data = json.dumps(telemetry)
        # Execute JS update function
        js_code = f"if (window.updateMapData) {{ window.updateMapData({json_data}); }}"
        self.web_view.page().runJavaScript(js_code)
