# -*- coding: utf-8 -*-
"""Conversion finale des snackbars et couleurs restantes"""

filepath = r'f:\Applications\Gestion Qualité\flet_app\lab_page_new.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Snackbars et messages
replacements = [
    ('ft.Colors.GREEN_700', 'Theme.SUCCESS'),
    ('ft.Colors.RED_700', 'Theme.DANGER'),
    ('ft.Colors.BLUE_700', 'Theme.PRIMARY'),
    ('ft.Colors.ORANGE_700', 'Theme.WARNING'),
    ('ft.Colors.PURPLE_700', 'Theme.SECONDARY'),
]

count = 0
for old, new in replacements:
    occurrences = content.count(old)
    if occurrences > 0:
        content = content.replace(old, new)
        count += occurrences
        print(f"  ✓ {occurrences}x: {old} → {new}")

print(f"\n✅ Total: {count} remplacements effectués")

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Conversion finale terminée")
