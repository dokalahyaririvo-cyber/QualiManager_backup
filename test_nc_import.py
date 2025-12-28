# -*- coding: utf-8 -*-
"""Test simple pour voir si nc_page peut être importé."""

import sys
print("Python path:", sys.path)
print("\nTentative d'import de flet_app.nc_page...")

try:
    from flet_app.nc_page import NCPage
    print("✅ Import réussi!")
    print(f"NCPage class: {NCPage}")
except Exception as e:
    print(f"❌ Erreur d'import: {type(e).__name__}")
    print(f"Message: {e}")
    import traceback
    traceback.print_exc()

print("\nVérification des autres modules...")
try:
    from flet_app.components import create_card
    print("✅ components OK")
except Exception as e:
    print(f"❌ components: {e}")

try:
    from flet_app.components_advanced import StatusBadge
    print("✅ components_advanced OK")
except Exception as e:
    print(f"❌ components_advanced: {e}")

try:
    from flet_app.theme import Theme
    print("✅ theme OK")
except Exception as e:
    print(f"❌ theme: {e}")

input("\nAppuyez sur Entrée pour quitter...")
