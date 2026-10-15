import re

with open('frontend/src/pages/GuidedFormPage.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Let's inspect imports and add any missing dependencies or icons
print("Loaded GuidedFormPage.jsx successfully, length:", len(content))
