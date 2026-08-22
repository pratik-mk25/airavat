"""
Top Left Panel: Live Camera Feed with ZOOM: [-] 1.0x [+] Controls and Top Cardinal Compass Bar (N, E, S, W).
Standardized typography matching Wind Speed badge (11px, font-weight: 800).
"""

import time
import math
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QWidget
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QFont
from PySide6.QtCore import Qt

class CameraFeedWidget(QWidget):
    """FPV Camera Feed with Top Horizontal Compass Bar (N, E, W, S)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.zoom_level = 1.0
        self.yaw = 45.0   # Current compass heading angle in degrees

    def set_zoom(self, zoom):
        self.zoom_level = max(1.0, min(10.0, zoom))
        self.update()

    def update_telemetry(self, yaw):
        self.yaw = yaw % 360.0
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = self.width()
        h = self.height()

        # 1. Optical Viewport Background (Clean Camera Stream)
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0.0, QColor(10, 20, 32))
        grad.setColorAt(0.5, QColor(16, 28, 44))
        grad.setColorAt(1.0, QColor(8, 14, 24))
        
        painter.setBrush(QBrush(grad))
        painter.setPen(QPen(QColor(0, 240, 255, 40), 1))
        painter.drawRoundedRect(0, 0, w, h, 8, 8)

        # ----------------------------------------------------
        # 2. TOP HORIZONTAL COMPASS TAPE (N, NE, E, SE, S, SW, W, NW & Degrees)
        # ----------------------------------------------------
        compass_y = 22
        painter.setPen(QPen(QColor(0, 240, 255, 120), 1))
        painter.drawLine(40, compass_y, w - 40, compass_y)
        
        # Center Marker Index Line
        painter.setPen(QPen(QColor(0, 255, 136, 220), 2))
        painter.drawLine(int(w / 2), compass_y - 6, int(w / 2), compass_y + 8)

        # Cardinal Direction Mapping
        cardinals = {
            0: "N", 45: "NE", 90: "E", 135: "SE",
            180: "S", 225: "SW", 270: "W", 315: "NW"
        }

        painter.setFont(QFont("Consolas", 8, QFont.Bold))
        center_x = w / 2

        for deg in range(0, 360, 15):
            diff = (deg - self.yaw + 540) % 360 - 180
            if abs(diff) <= 60:
                px = center_x + (diff * 4.5)
                if 40 <= px <= w - 40:
                    label = cardinals.get(deg, f"{deg}°")
                    is_cardinal = deg in cardinals
                    
                    tick_len = 6 if is_cardinal else 3
                    painter.setPen(QPen(QColor(0, 255, 136) if is_cardinal else QColor(0, 240, 255, 160), 1))
                    painter.drawLine(int(px), compass_y, int(px), compass_y - tick_len)

                    if is_cardinal:
                        painter.setPen(QColor(0, 255, 136))
                    else:
                        painter.setPen(QColor(148, 163, 184))
                    
                    painter.drawText(int(px) - 10, compass_y - 8, 20, 12, Qt.AlignCenter, label)

        # ----------------------------------------------------
        # 3. Subtle Center Reticle Crosshair
        # ----------------------------------------------------
        cx, cy = w / 2, h / 2
        painter.setPen(QPen(QColor(0, 240, 255, 80), 1, Qt.DashLine))
        painter.drawLine(int(cx - 20), int(cy), int(cx + 20), int(cy))
        painter.drawLine(int(cx), int(cy - 20), int(cx), int(cy + 20))

        # Magnification Text in Bottom Left
        if self.zoom_level > 1.0:
            painter.setPen(QColor(0, 240, 255))
            painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
            painter.drawText(20, h - 16, f"ZOOM: {self.zoom_level:.1f}X")


class CameraPanel(QFrame):
    """Top Left Camera Panel with ZOOM: [-] 1.0x [+] Controls."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CameraPanel")
        self.current_zoom = 1.0

        self.setStyleSheet("""
            #CameraPanel {
                background-color: #0d1321;
                border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 8px;
                padding: 4px;
            }
            .panel-header {
                font-size: 12px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 1.2px;
            }
            .zoom-title-lbl {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 0.8px;
            }
            .btn-zoom {
                background-color: rgba(13, 19, 33, 0.85);
                color: #00f0ff;
                border: 1.5px solid #00f0ff;
                border-radius: 4px;
                padding: 2px 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 800;
            }
            .btn-zoom:hover {
                background-color: rgba(0, 240, 255, 0.25);
            }
            .zoom-readout {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 11px;
                font-weight: 800;
                color: #00ff88;
                padding: 0px 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(4)

        # Top Bar Container with Title (Left) and ZOOM Controls (Right Corner)
        top_bar = QWidget()
        tb_layout = QHBoxLayout(top_bar)
        tb_layout.setContentsMargins(4, 2, 4, 2)
        tb_layout.setSpacing(6)

        lbl_head = QLabel("LIVE CAMERA FEED")
        lbl_head.setProperty("class", "panel-header")

        # Zoom Controls Box
        zoom_box = QWidget()
        zb_layout = QHBoxLayout(zoom_box)
        zb_layout.setContentsMargins(0, 0, 0, 0)
        zb_layout.setSpacing(4)

        lbl_zoom_text = QLabel("ZOOM:")
        lbl_zoom_text.setProperty("class", "zoom-title-lbl")

        self.btn_zoom_out = QPushButton("−")
        self.btn_zoom_out.setProperty("class", "btn-zoom")
        self.btn_zoom_out.setToolTip("Zoom Out")
        self.btn_zoom_out.clicked.connect(self.zoom_out)

        self.lbl_zoom_val = QLabel("1.0x")
        self.lbl_zoom_val.setProperty("class", "zoom-readout")

        self.btn_zoom_in = QPushButton("+")
        self.btn_zoom_in.setProperty("class", "btn-zoom")
        self.btn_zoom_in.setToolTip("Zoom In")
        self.btn_zoom_in.clicked.connect(self.zoom_in)

        zb_layout.addWidget(lbl_zoom_text)
        zb_layout.addWidget(self.btn_zoom_out)
        zb_layout.addWidget(self.lbl_zoom_val)
        zb_layout.addWidget(self.btn_zoom_in)

        tb_layout.addWidget(lbl_head)
        tb_layout.addStretch()
        tb_layout.addWidget(zoom_box)

        layout.addWidget(top_bar)

        # Camera Viewport Widget
        self.camera_feed = CameraFeedWidget(self)
        layout.addWidget(self.camera_feed, stretch=1)

    def zoom_in(self):
        """Increases zoom level up to 10.0x."""
        self.current_zoom = min(10.0, self.current_zoom + 0.5)
        self._update_zoom_display()

    def zoom_out(self):
        """Decreases zoom level down to 1.0x."""
        self.current_zoom = max(1.0, self.current_zoom - 0.5)
        self._update_zoom_display()

    def _update_zoom_display(self):
        self.lbl_zoom_val.setText(f"{self.current_zoom:.1f}x")
        self.camera_feed.set_zoom(self.current_zoom)

    def update_camera(self, data):
        if not data:
            return
        yaw = data.get("drone_yaw", 45.0)
        self.camera_feed.update_telemetry(yaw)
