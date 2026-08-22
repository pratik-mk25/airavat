"""
Header Widget for AIRAVAT Ground Control Station.
Displays top bar branding with logo image, status badge (LIVE/REPLAY), mode indicator (Baseline/AIRAVAT), and risk level badge.
(PROGRESS, BATTERY, and WIND readouts removed from heading per request).
"""

import os
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QFrame
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class HeaderWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("HeaderFrame")
        self.setStyleSheet("""
            #HeaderFrame {
                background-color: #0b0f19;
                border-bottom: 1.5px solid rgba(0, 240, 255, 0.25);
                min-height: 56px;
                max-height: 56px;
                padding: 0px 16px;
            }
            QLabel {
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            .brand-title {
                font-size: 17px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 2px;
            }
            .brand-subtitle {
                font-size: 14px;
                font-weight: 700;
                color: #00ff88;
                letter-spacing: 1.5px;
            }
            .logo-frame {
                background: #ffffff;
                border: 1.5px solid #00f0ff;
                border-radius: 8px;
                padding: 2px;
            }
            .badge-live {
                background-color: rgba(0, 255, 136, 0.15);
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 700;
                font-size: 11px;
            }
            .badge-mode {
                background-color: rgba(0, 240, 255, 0.15);
                color: #00f0ff;
                border: 1px solid #00f0ff;
                border-radius: 4px;
                padding: 4px 10px;
                font-weight: 700;
                font-size: 11px;
            }
            .badge-risk-low {
                background-color: rgba(0, 255, 136, 0.2);
                color: #00ff88;
                border: 1px solid #00ff88;
                border-radius: 4px;
                padding: 4px 12px;
                font-weight: 800;
                font-size: 11px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 6, 12, 6)
        layout.setSpacing(16)

        # 1. Branding Title: AIRAVAT GROUND CONTROL STATION
        title_box = QWidget()
        tb_layout = QHBoxLayout(title_box)
        tb_layout.setContentsMargins(0, 0, 0, 0)
        tb_layout.setSpacing(10)

        # Logo Image Widget
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
        self.lbl_logo = QLabel()
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.lbl_logo.setPixmap(pixmap)
            self.lbl_logo.setProperty("class", "logo-frame")
        
        lbl_airavat = QLabel("AIRAVAT")
        lbl_airavat.setProperty("class", "brand-title")
        lbl_pipe = QLabel("|")
        lbl_pipe.setStyleSheet("color: #475569; font-size: 18px; font-weight: 300;")
        lbl_gcs = QLabel("GROUND CONTROL STATION")
        lbl_gcs.setProperty("class", "brand-subtitle")
        
        tb_layout.addWidget(self.lbl_logo)
        tb_layout.addWidget(lbl_airavat)
        tb_layout.addWidget(lbl_pipe)
        tb_layout.addWidget(lbl_gcs)
        
        layout.addWidget(title_box)
        layout.addStretch()

        # 2. Status Badge (LIVE / REPLAY)
        self.lbl_status = QLabel("LIVE")
        self.lbl_status.setProperty("class", "badge-live")
        layout.addWidget(self.lbl_status)

        # 3. Mode Badge (Baseline / AIRAVAT)
        self.lbl_mode = QLabel("AIRAVAT MODE")
        self.lbl_mode.setProperty("class", "badge-mode")
        layout.addWidget(self.lbl_mode)

        # 4. Risk Level Badge (LOW / MEDIUM / HIGH / CRITICAL)
        self.lbl_risk = QLabel("RISK: LOW")
        self.lbl_risk.setProperty("class", "badge-risk-low")
        layout.addWidget(self.lbl_risk)

    def update_header(self, telemetry):
        # Update Status Badge
        status = telemetry.get("status", "LIVE")
        self.lbl_status.setText(status)
        if status == "LIVE":
            self.lbl_status.setStyleSheet("background: rgba(0,255,136,0.15); color: #00ff88; border: 1px solid #00ff88; border-radius: 4px; padding: 4px 10px; font-weight: 700; font-size: 11px;")
        else:
            self.lbl_status.setStyleSheet("background: rgba(255,170,0,0.15); color: #ffaa00; border: 1px solid #ffaa00; border-radius: 4px; padding: 4px 10px; font-weight: 700; font-size: 11px;")

        # Update Mode Badge
        mode = telemetry.get("mode", "AIRAVAT")
        self.lbl_mode.setText(f"MODE: {mode}")
        if mode == "AIRAVAT":
            self.lbl_mode.setStyleSheet("background: rgba(0,240,255,0.15); color: #00f0ff; border: 1px solid #00f0ff; border-radius: 4px; padding: 4px 10px; font-weight: 700; font-size: 11px;")
        else:
            self.lbl_mode.setStyleSheet("background: rgba(148,163,184,0.2); color: #94a3b8; border: 1px solid #94a3b8; border-radius: 4px; padding: 4px 10px; font-weight: 700; font-size: 11px;")

        # Update Risk Badge
        risk = telemetry.get("risk_level", "LOW")
        self.lbl_risk.setText(f"RISK: {risk}")
        if risk == "LOW":
            self.lbl_risk.setStyleSheet("background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid #00ff88; border-radius: 4px; padding: 4px 12px; font-weight: 800; font-size: 11px;")
        elif risk == "MEDIUM":
            self.lbl_risk.setStyleSheet("background: rgba(255,170,0,0.2); color: #ffaa00; border: 1px solid #ffaa00; border-radius: 4px; padding: 4px 12px; font-weight: 800; font-size: 11px;")
        else:
            self.lbl_risk.setStyleSheet("background: rgba(255,51,102,0.25); color: #ff3366; border: 1px solid #ff3366; border-radius: 4px; padding: 4px 12px; font-weight: 800; font-size: 11px;")
