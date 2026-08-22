"""
Main Entry Point for AIRAVAT Ground Control Station (GCS).
Runs on Ubuntu (Linux) and Windows with PySide6.
"""

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from ui.main_window import MainWindow

def main():
    # Enable High DPI Scaling & GPU acceleration attributes
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    app.setApplicationName("AIRAVAT Ground Control Station")
    app.setOrganizationName("AIRAVAT Physical AI Team")

    # Set App Icon
    logo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "assets", "logo.png"))
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
