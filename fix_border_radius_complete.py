"""Fix BorderRadius to include all 4 corners (required in Flet 0.28)"""

import re
import os

def fix_border_radius_in_file(filepath):
    """Fix BorderRadius patterns to include all 4 corners"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Pattern 1: ft.BorderRadius(top_left=X, top_right=Y) -> add bottom corners with 0
        content = re.sub(
            r'ft\.BorderRadius\(top_left=(\d+),\s*top_right=(\d+)\)',
            r'ft.BorderRadius(\1, \2, 0, 0)',
            content
        )
        
        # Pattern 2: ft.BorderRadius(bottom_left=X, bottom_right=Y) -> add top corners with 0
        content = re.sub(
            r'ft\.BorderRadius\(bottom_left=(\d+),\s*bottom_right=(\d+)\)',
            r'ft.BorderRadius(0, 0, \1, \2)',
            content
        )
        
        # Pattern 3: ft.BorderRadius(top_left=X, bottom_left=Y) -> left corners
        content = re.sub(
            r'ft\.BorderRadius\(top_left=(\d+),\s*bottom_left=(\d+)\)',
            r'ft.BorderRadius(\1, 0, \2, 0)',
            content
        )
        
        # Pattern 4: ft.BorderRadius(top_right=X, bottom_right=Y) -> right corners
        content = re.sub(
            r'ft\.BorderRadius\(top_right=(\d+),\s*bottom_right=(\d+)\)',
            r'ft.BorderRadius(0, \1, 0, \2)',
            content
        )
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Fix all files in flet_app directory"""
    flet_app_dir = "flet_app"
    files_fixed = []
    
    for root, dirs, files in os.walk(flet_app_dir):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_border_radius_in_file(filepath):
                    files_fixed.append(filepath)
                    print(f"✓ Fixed: {filepath}")
    
    if files_fixed:
        print(f"\n✓ Fixed {len(files_fixed)} files:")
        for f in files_fixed:
            print(f"  - {f}")
    else:
        print("No files needed fixing")

if __name__ == "__main__":
    main()
