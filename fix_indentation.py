# -*- coding: utf-8 -*-
"""
Script pour corriger l'indentation de la méthode _build_dashboard_tab
"""

def fix_indentation():
    file_path = "flet_app/nc_page.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Trouver la ligne de début de _build_dashboard_tab (ligne ~6100)
    start_line = None
    end_line = None
    
    for i, line in enumerate(lines):
        if 'def _build_dashboard_tab(self):' in line:
            start_line = i
            print(f"Trouvé _build_dashboard_tab à la ligne {i+1}")
        elif start_line and 'def _build_risk_matrix(self, all_ncs):' in line:
            end_line = i
            print(f"Trouvé _build_risk_matrix à la ligne {i+1}")
            break
    
    if not start_line or not end_line:
        print("Méthodes non trouvées!")
        return
    
    # Trouver où commence le code non indenté (après les prints)
    code_start = None
    for i in range(start_line, end_line):
        if '# === 1. CALCUL KPI ALERTES & SANTÉ ===' in lines[i]:
            code_start = i
            print(f"Code non indenté commence à la ligne {i+1}")
            break
    
    if not code_start:
        print("Début du code non trouvé!")
        return
    
    # Réindenter tout le code entre code_start et la ligne du return (avant except)
    fixed_lines = lines[:code_start]
    
    # Trouver la ligne avec "except Exception as e:" dans _build_dashboard_tab
    except_line = None
    for i in range(code_start, end_line):
        if 'except Exception as e:' in lines[i] and '_build_dashboard_tab' in ''.join(lines[max(0, i-20):i]):
            except_line = i
            print(f"Trouvé except à la ligne {i+1}")
            break
    
    if not except_line:
        print("Exception handler non trouvé, on va jusqu'à la fin")
        except_line = end_line
    
    # Réindenter les lignes entre code_start et except_line
    for i in range(code_start, except_line):
        line = lines[i]
        # Ajouter 4 espaces d'indentation (un niveau de plus)
        if line.strip():  # Si la ligne n'est pas vide
            fixed_lines.append('    ' + line)
        else:
            fixed_lines.append(line)
    
    # Ajouter le reste du fichier
    fixed_lines.extend(lines[except_line:])
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fichier corrigé! {len(fixed_lines)} lignes au total")
    print(f"   - Lignes réindentées: {except_line - code_start}")

if __name__ == '__main__':
    fix_indentation()
