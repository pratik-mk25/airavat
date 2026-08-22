"""
Main Window for AIRAVAT Ground Control Station (GCS).
Layout Architecture:
- Top: Header Bar (Branding, Status, Mode, Progress, Battery, Wind, Risk)
- Upper Workspace (77% Height): 3-Panel Splitter
  - Left (40% Width): Live Optical Camera Feed (Decreased Camera Size)
  - Center (35% Width): Mission Map View
  - Right (25% Width): AI Decision Feed (Added Box to the Right of the Map!)
- Lower Workspace (23% Height): Telemetry Metrics Box & 3 Live Sparkline Line Charts
- Bottom Bar: Interactive Controls Bar
"""

import os
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QIcon

from ui.header_widget import HeaderWidget
from ui.camera_panel import CameraPanel
from ui.map_panel import MapPanel
from ui.telemetry_panel import TelemetryPanel
from ui.ai_feed_panel import AIFeedPanel
from ui.control_panel import ControlPanel
from airavat_core.simulation_engine import SimulationEngine

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AIRAVAT Ground Control Station")
        self.resize(1700, 1000)

        # Set Window Icon
        logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "logo.png"))
        if os.path.exists(logo_path):
            self.setWindowIcon(QIcon(logo_path))

        # Global Dark Tactical Styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #060911;
            }
            QSplitter::handle {
                background-color: rgba(0, 240, 255, 0.25);
                height: 4px;
                width: 4px;
            }
        """)

        # Main Container
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Header Bar
        self.header = HeaderWidget(self)
        main_layout.addWidget(self.header)

        # 2. Main Vertical Splitter (77% Top Workspace / 23% Bottom Telemetry)
        main_vertical_splitter = QSplitter(Qt.Vertical)
        main_vertical_splitter.setHandleWidth(4)

        # ----------------------------------------------------
        # UPPER WORKSPACE (77% HEIGHT): 3-BOX SPLITTER
        # Box 1 (Left): Live Camera Feed (Decreased size)
        # Box 2 (Center): Mission Map View
        # Box 3 (Right): AI Decision Feed (Placed on the right of the Map!)
        # ----------------------------------------------------
        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setHandleWidth(4)

        self.camera_panel = CameraPanel(self)
        top_splitter.addWidget(self.camera_panel)

        self.map_panel = MapPanel(self)
        top_splitter.addWidget(self.map_panel)

        self.ai_panel = AIFeedPanel(self)
        top_splitter.addWidget(self.ai_panel)

        # Width ratios: Camera (40%), Map (35%), AI Decision Feed (25%)
        top_splitter.setSizes([680, 595, 425])
        top_splitter.setStretchFactor(0, 4)
        top_splitter.setStretchFactor(1, 35)
        top_splitter.setStretchFactor(2, 25)
        
        main_vertical_splitter.addWidget(top_splitter)

        # ----------------------------------------------------
        # LOWER WORKSPACE (23% HEIGHT): TELEMETRY METRICS & CHARTS BOX
        # ----------------------------------------------------
        self.telemetry_panel = TelemetryPanel(self)
        main_vertical_splitter.addWidget(self.telemetry_panel)

        # Set 77% / 23% height ratio
        main_vertical_splitter.setSizes([770, 230])
        main_vertical_splitter.setStretchFactor(0, 3)
        main_vertical_splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(main_vertical_splitter, stretch=1)

        # 3. Bottom Controls Panel
        self.control_panel = ControlPanel(self)
        main_layout.addWidget(self.control_panel)

        # 4. Simulation Engine Initialization
        self.sim_engine = SimulationEngine()
        self.sim_engine.telemetry_updated.connect(self.on_telemetry_update)

        # Connect Control Panel signals to Simulation Engine
        self.control_panel.start_pause_clicked.connect(self.sim_engine.toggle_start_pause)
        self.control_panel.reset_clicked.connect(self.sim_engine.reset_mission)
        self.control_panel.inject_wind_clicked.connect(self.sim_engine.inject_wind)
        self.control_panel.inject_obstacle_clicked.connect(self.sim_engine.inject_obstacle)
        self.control_panel.low_battery_clicked.connect(self.sim_engine.trigger_low_battery)
        self.control_panel.toggle_mode_clicked.connect(self.sim_engine.toggle_mode)

        # Start Simulation Loop
        self.sim_engine.start()

    @Slot(dict)
    def on_telemetry_update(self, data):
        """Dispatches real-time telemetry payload to all UI panels."""
        self.header.update_header(data)
        self.camera_panel.update_camera(data)
        self.map_panel.update_map(data)
        self.telemetry_panel.update_telemetry(data)
        self.ai_panel.update_ai_feed(data)
        self.control_panel.update_control_state(data.get("is_paused", True))

    def closeEvent(self, event):
        """Cleanup threads on application exit."""
        self.sim_engine.stop()
        event.accept()
