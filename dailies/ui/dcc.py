from dailies.ui.ui import DailiesUI
from dailies.environment import Environment
from dailies.preset import load_presets_from_folder

# Fetch data from environment variables
environment = Environment()

# Load presets
presets = load_presets_from_folder()

# Initialize the UI
dailies_ui = DailiesUI(environment=environment, presets=presets)

# Show the UI window
dailies_ui.show()
