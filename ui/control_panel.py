"""
Bottom Panel: Interactive Controls & Simulation Injectors Bar.
Provides action buttons for Mission Control (Start/Pause, Reset), Simulation Injectors (Wind, Obstacle, Battery), and Mode Toggle.
"""

from PySide6.QtWidgets import QFrame, QHBoxLayout, QPushButton, QLabel, QWidget
from PySide6.QtCore import Signal, Qt

class ControlPanel(QFrame):
    # Signals emitted when buttons are clicked
    start_pause_clicked = Signal()
    reset_clicked = Signal()
    inject_wind_clicked = Signal()
    inject_obstacle_clicked = Signal()
    low_battery_clicked = Signal()
    toggle_mode_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ControlPanel")
        self.setStyleSheet("""
            #ControlPanel {
                background-color: #0b0f19;
                border-top: 1.5px solid rgba(0, 240, 255, 0.25);
                min-height: 60px;
                max-height: 60px;
                padding: 0px 16px;
            }
            QPushButton {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: 800;
                border-radius: 6px;
                padding: 8px 16px;
                letter-spacing: 0.5px;
            }
            .btn-start {
                background-color: rgba(0, 255, 136, 0.15);
                color: #00ff88;
                border: 1.5px solid #00ff88;
            }
            .btn-start:hover {
                background-color: rgba(0, 255, 136, 0.35);
            }
            .btn-pause {
                background-color: rgba(255, 170, 0, 0.15);
                color: #ffaa00;
                border: 1.5px solid #ffaa00;
            }
            .btn-reset {
                background-color: rgba(148, 163, 184, 0.15);
                color: #e2e8f0;
                border: 1.5px solid #64748b;
            }
            .btn-reset:hover {
                background-color: rgba(148, 163, 184, 0.3);
            }
            .btn-injector {
                background-color: rgba(0, 240, 255, 0.12);
                color: #00f0ff;
                border: 1.5px solid #00f0ff;
            }
            .btn-injector:hover {
                background-color: rgba(0, 240, 255, 0.28);
            }
            .btn-warning {
                background-color: rgba(255, 51, 102, 0.15);
                color: #ff3366;
                border: 1.5px solid #ff3366;
            }
            .btn-warning:hover {
                background-color: rgba(255, 51, 102, 0.35);
            }
            .btn-toggle {
                background-color: rgba(168, 85, 247, 0.15);
                color: #c084fc;
                border: 1.5px solid #a855f7;
            }
            .btn-toggle:hover {
                background-color: rgba(168, 85, 247, 0.35);
            }
            .ctrl-group-title {
                font-size: 10px;
                color: #64748b;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-right: 6px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(12)

        # 1. Mission Control Section
        lbl_mc = QLabel("MISSION CONTROL:")
        lbl_mc.setProperty("class", "ctrl-group-title")
        layout.addWidget(lbl_mc)

        self.btn_start = QPushButton("START MISSION")
        self.btn_start.setProperty("class", "btn-start")
        self.btn_start.clicked.connect(self.start_pause_clicked.emit)
        layout.addWidget(self.btn_start)

        self.btn_reset = QPushButton("RESET")
        self.btn_reset.setProperty("class", "btn-reset")
        self.btn_reset.clicked.connect(self.reset_clicked.emit)
        layout.addWidget(self.btn_reset)

        # Divider
        layout.addWidget(self._create_divider())

        # 2. Simulation Injectors Section
        lbl_inj = QLabel("SIMULATION INJECTORS:")
        lbl_inj.setProperty("class", "ctrl-group-title")
        layout.addWidget(lbl_inj)

        self.btn_wind = QPushButton("⚡ INJECT WIND")
        self.btn_wind.setProperty("class", "btn-injector")
        self.btn_wind.clicked.connect(self.inject_wind_clicked.emit)
        layout.addWidget(self.btn_wind)

        self.btn_obstacle = QPushButton("⚠️ INJECT OBSTACLE")
        self.btn_obstacle.setProperty("class", "btn-injector")
        self.btn_obstacle.clicked.connect(self.inject_obstacle_clicked.emit)
        layout.addWidget(self.btn_obstacle)

        self.btn_battery = QPushButton("🔋 LOW BATTERY EVENT")
        self.btn_battery.setProperty("class", "btn-warning")
        self.btn_battery.clicked.connect(self.low_battery_clicked.emit)
        layout.addWidget(self.btn_battery)

        # Divider
        layout.addWidget(self._create_divider())

        # 3. Mode Toggles
        self.btn_mode = QPushButton("🔄 TOGGLE: BASELINE / AIRAVAT")
        self.btn_mode.setProperty("class", "btn-toggle")
        self.btn_mode.clicked.connect(self.toggle_mode_clicked.emit)
        layout.addWidget(self.btn_mode)

        layout.addStretch()

    def _create_divider(self):
        div = QFrame()
        div.setFrameShape(QFrame.VLine)
        div.setStyleSheet("color: rgba(255, 255, 255, 0.12);")
        return div

    def update_control_state(self, is_paused):
        if is_paused:
            self.btn_start.setText("START MISSION")
            self.btn_start.setStyleSheet("background-color: rgba(0, 255, 136, 0.15); color: #00ff88; border: 1.5px solid #00ff88;")
        else:
            self.btn_start.setText("PAUSE MISSION")
            self.btn_start.setStyleSheet("background-color: rgba(255, 170, 0, 0.15); color: #ffaa00; border: 1.5px solid #ffaa00;")
