"""
Right Panel: AI Decision Feed & Qwen World-Model Intelligence Panel.
Clean Recommended Action Card with yellow border outline removed surrounding the recommendation & hold readout.
"""

from PySide6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QWidget, QProgressBar, QTextEdit
)
from PySide6.QtGui import QFont, QColor
from PySide6.QtCore import Qt

class AIFeedPanel(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("AIFeedPanel")
        self.setStyleSheet("""
            #AIFeedPanel {
                background-color: #0d1321;
                border: 1px solid rgba(0, 240, 255, 0.2);
                border-radius: 8px;
                padding: 6px;
            }
            .panel-header {
                font-size: 12px;
                font-weight: 800;
                color: #00f0ff;
                letter-spacing: 1.2px;
                margin-bottom: 2px;
            }
            .action-card {
                background: #131c2e;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 6px;
            }
            .action-title {
                font-size: 14px;
                font-weight: 900;
                color: #00f0ff;
                letter-spacing: 0.8px;
            }
            .sub-lbl {
                font-size: 9px;
                color: #94a3b8;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                font-weight: 800;
            }
            .explanation-card {
                background: rgba(19, 28, 46, 0.8);
                border: 1px solid rgba(0, 240, 255, 0.15);
                border-radius: 6px;
                padding: 6px 10px;
            }
            .exp-text {
                font-size: 11px;
                color: #e2e8f0;
                line-height: 1.3;
            }
            QProgressBar {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 4px;
                background-color: #090d16;
                height: 10px;
                text-align: center;
                color: transparent;
            }
            QProgressBar::chunk {
                background-color: #00ff88;
                border-radius: 3px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Title Header
        lbl_head = QLabel("AI DECISION FEED")
        lbl_head.setProperty("class", "panel-header")
        layout.addWidget(lbl_head)

        # 1. Recommended Action Card (Clean layout - yellow outline removed)
        self.action_card = QWidget()
        self.action_card.setProperty("class", "action-card")
        ac_layout = QHBoxLayout(self.action_card)
        ac_layout.setContentsMargins(10, 6, 10, 6)
        ac_layout.setSpacing(8)

        lbl_ac_tag = QLabel("RECOMMENDED ACTION:")
        lbl_ac_tag.setProperty("class", "sub-lbl")
        
        self.lbl_action_val = QLabel("CONTINUE")
        self.lbl_action_val.setProperty("class", "action-title")

        ac_layout.addWidget(lbl_ac_tag)
        ac_layout.addWidget(self.lbl_action_val)
        ac_layout.addStretch()

        layout.addWidget(self.action_card)

        # 2. Confidence Score Bar
        conf_box = QWidget()
        cb_layout = QVBoxLayout(conf_box)
        cb_layout.setContentsMargins(0, 0, 0, 0)
        cb_layout.setSpacing(2)

        conf_hdr = QWidget()
        ch_layout = QHBoxLayout(conf_hdr)
        ch_layout.setContentsMargins(0, 0, 0, 0)
        lbl_conf = QLabel("CONFIDENCE SCORE")
        lbl_conf.setProperty("class", "sub-lbl")
        self.lbl_conf_val = QLabel("99.1%")
        self.lbl_conf_val.setStyleSheet("font-size: 11px; font-weight: 800; color: #00ff88;")
        ch_layout.addWidget(lbl_conf)
        ch_layout.addStretch()
        ch_layout.addWidget(self.lbl_conf_val)

        self.progress_conf = QProgressBar()
        self.progress_conf.setValue(99)

        cb_layout.addWidget(conf_hdr)
        cb_layout.addWidget(self.progress_conf)
        layout.addWidget(conf_box)

        # 3. Qwen Physics Reasoning Explanation Box
        exp_box = QWidget()
        exp_box.setProperty("class", "explanation-card")
        eb_layout = QVBoxLayout(exp_box)
        eb_layout.setContentsMargins(8, 6, 8, 6)
        eb_layout.setSpacing(2)

        lbl_exp_tag = QLabel("QWEN WORLD-MODEL REASONING")
        lbl_exp_tag.setProperty("class", "sub-lbl")
        
        self.lbl_explanation = QLabel("Nominal flight parameters detected. Aerodynamic wind vector within stability margin.")
        self.lbl_explanation.setWordWrap(True)
        self.lbl_explanation.setProperty("class", "exp-text")

        eb_layout.addWidget(lbl_exp_tag)
        eb_layout.addWidget(self.lbl_explanation)

        # Risk Chip
        risk_box = QWidget()
        rb_layout = QHBoxLayout(risk_box)
        rb_layout.setContentsMargins(0, 4, 0, 0)
        
        lbl_risk_tag = QLabel("RISK LEVEL:")
        lbl_risk_tag.setProperty("class", "sub-lbl")
        
        self.lbl_risk_chip = QLabel("LOW")
        self.lbl_risk_chip.setAlignment(Qt.AlignCenter)
        self.lbl_risk_chip.setStyleSheet("background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid #00ff88; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:4px;")

        rb_layout.addWidget(lbl_risk_tag)
        rb_layout.addWidget(self.lbl_risk_chip)
        rb_layout.addStretch()

        eb_layout.addWidget(risk_box)
        layout.addWidget(exp_box)

        # 4. Compact Low-Profile Live Log Stream Box
        lbl_log_tag = QLabel("LIVE LOG STREAM")
        lbl_log_tag.setProperty("class", "sub-lbl")
        layout.addWidget(lbl_log_tag)

        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        self.txt_logs.setMaximumHeight(85)  # Compact height limit
        self.txt_logs.setStyleSheet("""
            QTextEdit {
                background-color: #090d16;
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-radius: 4px;
                color: #00f0ff;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9px;
                padding: 4px;
            }
        """)
        layout.addWidget(self.txt_logs)
        layout.addStretch()

    def update_ai_feed(self, data):
        if not data:
            return

        action = data.get("ai_action", "Continue")
        conf = data.get("ai_confidence", 99.0)
        exp = data.get("ai_explanation", "")
        risk = data.get("risk_level", "LOW")
        logs = data.get("ai_logs", [])

        # 1. Action Card Text Readout (Clean background without yellow border outline)
        self.lbl_action_val.setText(action.upper())
        self.action_card.setStyleSheet("background: #131c2e; border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 6px;")

        if action == "Continue":
            self.lbl_action_val.setStyleSheet("font-size: 14px; font-weight: 900; color: #00ff88;")
        elif action in ["Reroute", "Reprioritize Waypoint"]:
            self.lbl_action_val.setStyleSheet("font-size: 14px; font-weight: 900; color: #00f0ff;")
        elif action == "Hold":
            self.lbl_action_val.setStyleSheet("font-size: 14px; font-weight: 900; color: #ffaa00;")
        else: # Return Early
            self.lbl_action_val.setStyleSheet("font-size: 14px; font-weight: 900; color: #ff3366;")

        # 2. Confidence Score & Bar
        self.lbl_conf_val.setText(f"{conf:.1f}%")
        self.progress_conf.setValue(int(conf))

        # 3. Explanation text
        self.lbl_explanation.setText(exp)

        # 4. Risk Level Chip
        self.lbl_risk_chip.setText(risk)
        if risk == "LOW":
            self.lbl_risk_chip.setStyleSheet("background: rgba(0,255,136,0.2); color: #00ff88; border: 1px solid #00ff88; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:4px;")
        elif risk == "MEDIUM":
            self.lbl_risk_chip.setStyleSheet("background: rgba(255,170,0,0.2); color: #ffaa00; border: 1px solid #ffaa00; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:4px;")
        else:
            self.lbl_risk_chip.setStyleSheet("background: rgba(255,51,102,0.25); color: #ff3366; border: 1px solid #ff3366; font-weight:bold; font-size:11px; padding:2px 8px; border-radius:4px;")

        # 5. Timeline Logs Stream
        self.txt_logs.setText("\n".join(logs))
        self.txt_logs.verticalScrollBar().setValue(self.txt_logs.verticalScrollBar().maximum())
