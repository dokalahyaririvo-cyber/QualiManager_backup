"""Script pour corriger la syntaxe Padding pour Flet 0.28"""
import os
import re

def fix_padding_symmetric(match):
    """Convertit ft.padding.symmetric(...) en ft.Padding(...)"""
    content = match.group(1)
    
    # Parser les arguments
    h_match = re.search(r'horizontal\s*=\s*(\d+)', content)
    v_match = re.search(r'vertical\s*=\s*(\d+)', content)
    
    # Si format positionnel (x, y)
    pos_match = re.match(r'^\s*(\d+)\s*,\s*(\d+)\s*$', content)
    
    if pos_match:
        h = pos_match.group(1)
        v = pos_match.group(2)
        return f'ft.Padding(left={h}, right={h}, top={v}, bottom={v})'
    elif h_match and v_match:
        h = h_match.group(1)
        v = v_match.group(1)
        return f'ft.Padding(left={h}, right={h}, top={v}, bottom={v})'
    elif h_match:
        h = h_match.group(1)
        return f'ft.Padding(left={h}, right={h}, top=0, bottom=0)'
    elif v_match:
        v = v_match.group(1)
        return f'ft.Padding(left=0, right=0, top={v}, bottom={v})'
    else:
        print(f"Impossible de parser: {match.group(0)}")
        return match.group(0)

def fix_padding_only(match):
    """Convertit ft.padding.only(...) en ft.Padding(...)"""
    content = match.group(1)
    
    params = []
    for param in ['left', 'right', 'top', 'bottom']:
        param_match = re.search(rf'{param}\s*=\s*(\d+)', content)
        if param_match:
            params.append(f'{param}={param_match.group(1)}')
        else:
            params.append(f'{param}=0')
    
    return f'ft.Padding({", ".join(params)})'

def fix_file(filepath):
    """Corrige les padding dans un fichier"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(filepath, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            return False
    
    original = content
    
    # Remplacer ft.padding.symmetric(...)
    content = re.sub(r'ft\.padding\.symmetric\((.*?)\)', fix_padding_symmetric, content)
    
    # Remplacer ft.padding.only(...)
    content = re.sub(r'ft\.padding\.only\((.*?)\)', fix_padding_only, content)
    
    # Remplacer ft.padding.all(x)
    content = re.sub(r'ft\.padding\.all\((\d+)\)', r'ft.Padding(\1, \1, \1, \1)', content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Corrigé: {filepath}")
        return True
    return False

# Parcourir tous les fichiers Python
fixed_count = 0
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith('.py') and not file.startswith('fix_'):
            filepath = os.path.join(root, file)
            if fix_file(filepath):
                fixed_count += 1

print(f"\n🎉 {fixed_count} fichiers corrigés")
