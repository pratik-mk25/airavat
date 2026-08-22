"""
Bottom Panel: Real-time Telemetry Readouts & Live Sparkline Charts.
Stat cards feature inline readouts where telemetry data is written directly in front of the label.
Features 3 live streaming line charts for:
1. Battery Discharge (%)
2. Wind Speed (m/s)
3. Altitude (m)
"""

from collections import deque
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QGridLayout
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient, QFont, QPainterPath
from PySide6.QtCore import Qt

class SparklineChart(QWidget):
    """High-performance hardware-accelerated 60FPS Line Chart Widget."""
    def __init__(self, title, unit, color="#00f0ff", min_val=0, max_val=100, max_points=60, parent=None):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.line_color = QColor(color)
        self.min_val = min_val
        self.max_val = max_val
        self.max_points = max_points
        self.data = deque([min_val] * max_points, maxlen=max_points)
        self.current_val = min_val
        self.setMinimumHeight(82)

    def add_value(self, val):
        self.current_val = val
        self.data.append(val)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()

        # 1. Background Card
        painter.setBrush(QColor(19, 28, 46, 220))
        painter.setPen(QPen(QColor(255, 255, 255, 20), 1))
        painter.drawRoundedRect(0, 0, w, h, 6, 6)

        # 2. Header Text
        painter.setPen(QColor(148, 163, 184))
        font_t = QFont("Segoe UI", 8, QFont.Bold)
        painter.setFont(font_t)
        painter.drawText(10, 16, self.title.upper())

        # Current Value Display
        painter.setPen(self.line_color)
        font_v = QFont("Segoe UI", 10, QFont.Bold)
        painter.setFont(font_v)
        val_str = f"{self.current_val:.1f} {self.unit}"
        painter.drawText(w - 80, 16, val_str)

        # 3. Chart Area
        margin_top = 22
        margin_bottom = 8
        margin_left = 8
        margin_right = 8
        
        chart_w = w - margin_left - margin_right
        chart_h = h - margin_top - margin_bottom

        if len(self.data) < 2:
            return

        points = []
        step_x = chart_w / (self.max_points - 1)
        
        for i, val in enumerate(self.data):
            norm_y = (val - self.min_val) / max(1.0, (self.max_val - self.min_val))
            norm_y = max(0.0, min(1.0, norm_y))
            
            px = margin_left + (i * step_x)
            py = (margin_top + chart_h) - (norm_y * chart_h)
            points.append((px, py))

        # Fill Under Curve Gradient
        gradient = QLinearGradient(0, margin_top, 0, margin_top + chart_h)
        gradient.setColorAt(0.0, QColor(self.line_color.red(), self.line_color.green(), self.line_color.blue(), 60))
        gradient.setColorAt(1.0, QColor(self.line_color.red(), self.line_color.green(), self.line_color.blue(), 0))
        
        path_fill = QPainterPath()
        path_fill.moveTo(points[0][0], margin_top + chart_h)
        for px, py in points:
            path_fill.lineTo(px, py)
        path_fill.lineTo(points[-1][0], margin_top + chart_h)
        path_fill.closePath()

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawPath(path_fill)

        # Draw Line Stroke
        path_line = QPainterPath()
        path_line.moveTo(points[0][0], points[0][1])
        for px, py in points[1:]:
            path_line.lineTo(px, py)

        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(self.line_color, 1.8))
        painter.drawPath(path_line)

        # Current Point Marker Dot
        last_px, last_py = points[-1]
        painter.setBrush(QBrush(self.line_color))
        painter.setPen(QPen(Qt.white, 1))
        painter.drawEllipse(int(last_px) - 2.5, int(last_py) - 2.5, 5, 5)


class TelemetryPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TelemetryPanel")
        self.setStyleSheet("""
            #TelemetryPanel {
                background-color: #0d1321;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 8px;
                padding: 6px;
            }
            .panel-header {
                font-size: 12px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 1.2px;
            }
            .metric-card {
                background: #131c2e;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
            }
            .metric-lbl {
                font-size: 10px;
                font-weight: 700;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        lbl_head = QLabel("TELEMETRY METRICS & FLIGHT CHARTS")
        lbl_head.setProperty("class", "panel-header")
        layout.addWidget(lbl_head)

        # Main Content Area
        content_row = QWidget()
        row_layout = QHBoxLayout(content_row)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(8)

        # Left 2x3 Metric Cards Grid (Inline Labels & Values)
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(6)

        self.card_speed = self._create_card("SPEED:", "12.8 m/s", "#00f0ff")
        self.card_alt = self._create_card("ALTITUDE:", "45.0 m", "#ffaa00")
        self.card_batt = self._create_card("BATTERY:", "78%", "#00ff88")
        self.card_wind = self._create_card("WIND SPEED:", "8.0 m/s", "#00f0ff")
        self.card_obs = self._create_card("OBSTACLE DIST:", "120.0 m", "#ffaa00")
        self.card_prog = self._create_card("PROGRESS:", "42%", "#00ff88")

        grid.addWidget(self.card_speed, 0, 0)
        grid.addWidget(self.card_alt, 0, 1)
        grid.addWidget(self.card_batt, 1, 0)
        grid.addWidget(self.card_wind, 1, 1)
        grid.addWidget(self.card_obs, 2, 0)
        grid.addWidget(self.card_prog, 2, 1)

        row_layout.addWidget(grid_widget, stretch=1)

        # Right 3 Live Streaming Line Charts Side-by-Side: Battery, Wind Speed, Altitude
        charts_box = QWidget()
        cb_layout = QHBoxLayout(charts_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setSpacing(6)

        self.chart_battery = SparklineChart("Battery Discharge", "%", color="#00ff88", min_val=0, max_val=100)
        self.chart_wind = SparklineChart("Wind Speed", "m/s", color="#00f0ff", min_val=0, max_val=20)
        self.chart_alt = SparklineChart("Altitude", "m", color="#ffaa00", min_val=0, max_val=100)

        cb_layout.addWidget(self.chart_battery)
        cb_layout.addWidget(self.chart_wind)
        cb_layout.addWidget(self.chart_alt)

        row_layout.addWidget(charts_box, stretch=2)
        layout.addWidget(content_row)

    def _create_card(self, label, val_def, val_color):
        """Creates an inline stat card where the data value is written directly in front of the label."""
        card = QWidget()
        card.setProperty("class", "metric-card")
        
        # Horizontal Layout so data value sits directly in front of label
        l = QHBoxLayout(card)
        l.setContentsMargins(8, 5, 8, 5)
        l.setSpacing(6)

        lbl = QLabel(label)
        lbl.setProperty("class", "metric-lbl")
        
        val = QLabel(val_def)
        val.setObjectName("val")
        val.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {val_color};")
        
        l.addWidget(lbl)
        l.addWidget(val)
        l.addStretch()
        return card

    def update_telemetry(self, data):
        if not data:
            return
        
        speed = data.get("speed", 0.0)
        alt = data.get("altitude", 0.0)
        batt = data.get("battery", 0.0)
        wind = data.get("wind_speed", 0.0)
        obs = data.get("obstacle_distance", 0.0)
        prog = data.get("mission_progress", 0.0)

        # Update card text values (written directly in front of label)
        self.card_speed.findChild(QLabel, "val").setText(f"{speed:.1f} m/s")
        self.card_alt.findChild(QLabel, "val").setText(f"{alt:.1f} m")
        
        batt_card = self.card_batt.findChild(QLabel, "val")
        batt_card.setText(f"{batt:.0f}%")
        batt_color = "#00ff88" if batt > 50 else ("#ffaa00" if batt >= 20 else "#ff3366")
        batt_card.setStyleSheet(f"font-size: 13px; font-weight: 800; color: {batt_color};")
        
        self.card_wind.findChild(QLabel, "val").setText(f"{wind:.1f} m/s")
        self.card_obs.findChild(QLabel, "val").setText(f"{obs:.1f} m")
        self.card_prog.findChild(QLabel, "val").setText(f"{prog:.0f}%")

        # Update Live Sparkline Line Charts (Battery, Wind, Altitude)
        self.chart_battery.add_value(batt)
        self.chart_wind.add_value(wind)
        self.chart_alt.add_value(alt)
