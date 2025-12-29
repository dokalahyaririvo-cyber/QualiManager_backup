"""Fix ALL remaining Border.only() instances in flet_app directory"""

import re
import os

def fix_border_only_in_file(filepath):
    """Fix Border.only() patterns in a file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Pattern 1: border=ft.Border.only(bottom=...) -> border=ft.Border(bottom=...)
        content = re.sub(
            r'border\s*=\s*ft\.Border\.only\(bottom\s*=\s*',
            r'border=ft.Border(bottom=',
            content
        )
        
        # Pattern 2: border=ft.Border.only(right=...) -> border=ft.Border(right=...)
        content = re.sub(
            r'border\s*=\s*ft\.Border\.only\(right\s*=\s*',
            r'border=ft.Border(right=',
            content
        )
        
        # Pattern 3: border=ft.Border.only(left=...) -> border=ft.Border(left=...)
        content = re.sub(
            r'border\s*=\s*ft\.Border\.only\(left\s*=\s*',
            r'border=ft.Border(left=',
            content
        )
        
        # Pattern 4: border=ft.Border.only(top=...) -> border=ft.Border(top=...)
        content = re.sub(
            r'border\s*=\s*ft\.Border\.only\(top\s*=\s*',
            r'border=ft.Border(top=',
            content
        )
        
        # Pattern 5: ) if ... else ft.Border.only(bottom=...)
        content = re.sub(
            r'\)\s+if\s+([^\s]+)\s+else\s+ft\.Border\.only\(bottom\s*=\s*',
            r') if \1 else ft.Border(bottom=',
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
                if fix_border_only_in_file(filepath):
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
