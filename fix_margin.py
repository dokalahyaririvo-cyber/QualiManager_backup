"""Correction ft.margin pour Flet 0.28"""
import os
import re

def fix_margin_only(match):
    """Convertit ft.margin.only(...) en une valeur numérique ou Margin()"""
    content = match.group(1)
    
    params = {}
    for param in ['left', 'right', 'top', 'bottom']:
        param_match = re.search(rf'{param}\s*=\s*([^,)]+)', content)
        if param_match:
            params[param] = param_match.group(1).strip()
    
    # Si un seul paramètre, utiliser directement la valeur
    if len(params) == 1 and 'bottom' in params:
        return f"margin={params['bottom']}"
    
    # Sinon construire un Margin()
    parts = []
    for key in ['left', 'top', 'right', 'bottom']:
        val = params.get(key, '0')
        parts.append(val)
    
    return f'margin=ft.Margin({", ".join(parts)})'

def fix_margin_symmetric(match):
    """Convertit ft.margin.symmetric(...) en Margin()"""
    content = match.group(1)
    
    h_match = re.search(r'horizontal\s*=\s*([^,)]+)', content)
    v_match = re.search(r'vertical\s*=\s*([^,)]+)', content)
    
    h = h_match.group(1).strip() if h_match else '0'
    v = v_match.group(1).strip() if v_match else '0'
    
    return f'margin=ft.Margin({h}, {v}, {h}, {v})'

fixed = []
for root, dirs, files in os.walk('./flet_app'):
    for file in files:
        if file.endswith('.py'):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except:
                continue
            
            original = content
            
            # Remplacer ft.margin.only(...)
            content = re.sub(r'margin=ft\.margin\.only\((.*?)\)', fix_margin_only, content)
            
            # Remplacer ft.Margin.only(...) aussi
            content = re.sub(r'margin=ft\.Margin\.only\((.*?)\)', fix_margin_only, content)
            
            # Remplacer ft.margin.symmetric(...)
            content = re.sub(r'margin=ft\.margin\.symmetric\((.*?)\)', fix_margin_symmetric, content)
            
            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed.append(filepath)
                print(f"✅ {filepath}")

print(f"\n🎉 {len(fixed)} fichiers corrigés")
