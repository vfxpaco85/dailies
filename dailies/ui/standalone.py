import sys

from PySide6.QtWidgets import QApplication

from dailies.ui.ui import DailiesUI
from dailies.environment import Environment
from dailies.preset import load_presets_from_folder

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load environment
    environment = Environment()

    # Load presets
    presets = load_presets_from_folder()

    # Initialize the UI
    dailies_ui = DailiesUI(environment=environment, presets=presets)

    # Show the UI window
    dailies_ui.show()

    # Start the event loop
    sys.exit(app.exec())
