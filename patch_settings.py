import re

with open("/Users/danny/Desktop/OpenJarvis/frontend/src/pages/SettingsPage.tsx", "r") as f:
    settings_code = f.read()

with open("/Users/danny/Desktop/OpenJarvis/frontend/src/components/Chat/SystemPanel.tsx", "r") as f:
    system_code = f.read()

# We don't really need to do it with a python script, I can just use replace_file_content.
