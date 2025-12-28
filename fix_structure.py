# -*- coding: utf-8 -*-
"""
Script pour corriger la structure de _build_dashboard_tab
Le return doit être suivi de except, puis les autres méthodes au bon niveau
"""

def fix_structure():
    file_path = "flet_app/nc_page.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Trouver le return de _build_dashboard_tab
    return_line = None
    for i, line in enumerate(lines):
        if i > 6200 and i < 6250 and 'return ft.Column(' in line and 'scroll=ft.ScrollMode.AUTO' in ''.join(lines[i:i+5]):
            return_line = i
            print(f"Trouvé return à la ligne {i+1}")
            break
    
    if not return_line:
        print("Return non trouvé!")
        return
    
    # Trouver la fin du return (fermeture de la parenthèse)
    paren_count = 0
    end_return = None
    for i in range(return_line, min(return_line + 20, len(lines))):
        for char in lines[i]:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
        if paren_count == 0:
            end_return = i
            print(f"Fin du return à la ligne {i+1}")
            break
    
    if not end_return:
        print("Fin du return non trouvée!")
        return
    
    # Trouver où commence _create_alert_kpi (fonction mal indentée)
    alert_kpi_line = None
    for i in range(end_return, end_return + 20):
        if 'def _create_alert_kpi' in lines[i]:
            alert_kpi_line = i
            print(f"Trouvé _create_alert_kpi à la ligne {i+1}")
            break
    
    if not alert_kpi_line:
        print("_create_alert_kpi non trouvé!")
        return
    
    # Créer le fichier corrigé
    fixed_lines = lines[:end_return + 1]  # Jusqu'à la fin du return incluse
    
    # Ajouter le bloc except
    fixed_lines.append('\n')
    fixed_lines.append('        except Exception as e:\n')
    fixed_lines.append('            print(f"[NCPage._build_dashboard_tab] ❌ ERREUR: {type(e).__name__}: {e}")\n')
    fixed_lines.append('            import traceback\n')
    fixed_lines.append('            traceback.print_exc()\n')
    fixed_lines.append('            return ft.Column(\n')
    fixed_lines.append('                expand=True,\n')
    fixed_lines.append('                padding=20,\n')
    fixed_lines.append('                controls=[\n')
    fixed_lines.append('                    ft.Text("❌ Erreur lors du chargement du tableau de bord", size=20, weight=ft.FontWeight.BOLD, color="red"),\n')
    fixed_lines.append('                    ft.Text(f"{type(e).__name__}: {str(e)}", size=14),\n')
    fixed_lines.append('                ]\n')
    fixed_lines.append('            )\n')
    fixed_lines.append('\n')
    
    # Maintenant, désindenter toutes les lignes de _create_alert_kpi et autres méthodes qui suivent
    # jusqu'à _build_risk_matrix
    risk_matrix_line = None
    for i in range(alert_kpi_line, len(lines)):
        if '    def _build_risk_matrix(self, all_ncs):' in lines[i]:
            risk_matrix_line = i
            print(f"Trouvé _build_risk_matrix à la ligne {i+1}")
            break
    
    if not risk_matrix_line:
        print("_build_risk_matrix non trouvé!")
        # Ajouter le reste du fichier tel quel
        fixed_lines.extend(lines[alert_kpi_line:])
    else:
        # Désindenter les méthodes entre alert_kpi et risk_matrix (retirer 4 espaces)
        for i in range(alert_kpi_line, risk_matrix_line):
            line = lines[i]
            if line.startswith('        '):  # Si indenté de 8 espaces ou plus
                fixed_lines.append(line[4:])  # Retirer 4 espaces
            else:
                fixed_lines.append(line)
        
        # Ajouter le reste du fichier
        fixed_lines.extend(lines[risk_matrix_line:])
    
    # Sauvegarder
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(fixed_lines)
    
    print(f"✅ Fichier corrigé! {len(fixed_lines)} lignes au total")

if __name__ == '__main__':
    fix_structure()
