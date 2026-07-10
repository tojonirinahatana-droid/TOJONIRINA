import flet as ft
import sqlite3

def init_db():
    conn = sqlite3.connect("fitantanana_bola.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS fifanakalozana (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            antony TEXT,
            vola REAL,
            karazana TEXT,
            sokajy TEXT
        )
    """)
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "TOJONIRINA - Fitantanana Bola"
    page.theme_mode = ft.ThemeMode.DARK
    page.scroll = ft.ScrollMode.AUTO
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    init_db()

    # Variables ho an'ny karazana voafidy (Par défaut: Miditra)
    # Ny fampiasana dikan-teny tsotra toy izao dia misoroka ny hadisoana rehetra
    karazana_iditra = ft.Text("Karazana voafidy : ENTREE (Vola Miditra)", color=ft.Colors.GREEN_ACCENT, weight=ft.FontWeight.BOLD)
    karazana_state = "Miditra"
    sokajy_state = "PLUS"

    # Saha fampidirana tsotra
    antony_input = ft.TextField(label="Antony mivantana", width=300, border_radius=10)
    vola_input = ft.TextField(label="Isan'ny vola (Ariary)", width=300, border_radius=10, keyboard_type=ft.KeyboardType.NUMBER)
    
    # Safidy ho an'ny SORTIE (Désignation)
    sokajy_dropdown = ft.Dropdown(
        width=300,
        visible=False,
        options=[
            ft.dropdown.Option("CREDIT"),
            ft.dropdown.Option("FRAIS"),
            ft.dropdown.Option("GOUTTER"),
            ft.dropdown.Option("DEVOIR"),
            ft.dropdown.Option("SANTE"),
            ft.dropdown.Option("RIZ"),
            ft.dropdown.Option("NOM"),
            ft.dropdown.Option("PLUS"),
        ]
    )
    sokajy_label = ft.Text("Sokajy (Désignation SORTIE) :", visible=False)

    # Rehefa tsindrina ny bokotra ENTREE
    def set_entree(e):
        nonlocal karazana_state
        karazana_state = "Miditra"
        karazana_iditra.value = "Karazana voafidy : ENTREE (Vola Miditra)"
        karazana_iditra.color = ft.Colors.GREEN_ACCENT
        sokajy_dropdown.visible = False
        sokajy_label.visible = False
        page.update()

    # Rehefa tsindrina ny bokotra SORTIE
    def set_sortie(e):
        nonlocal karazana_state
        karazana_state = "Mivoaka"
        karazana_iditra.value = "Karazana voafidy : SORTIE (Vola Mivoaka)"
        karazana_iditra.color = ft.Colors.RED_ACCENT
        sokajy_dropdown.visible = True
        sokajy_label.visible = True
        page.update()

    # Bokotra roa hifidianana ny Karazana (Tsy mampiasa Radio intsony!)
    btn_entree = ft.ElevatedButton(text="ENTREE", on_click=set_entree)
    btn_base_sortie = ft.ElevatedButton(text="SORTIE", on_click=set_sortie)

    # Ireo soratra eo amin'ny Dashboard
    entree_text = ft.Text("Total ENTREE : 0 Ar", size=16, color=ft.Colors.GREEN_ACCENT_400, weight=ft.FontWeight.W_500)
    sortie_text = ft.Text("Total SORTIE : 0 Ar", size=16, color=ft.Colors.RED_ACCENT_400, weight=ft.FontWeight.W_500)
    vola_final_text = ft.Text("Vola Sisa (FINALE) : 0 Ar", size=22, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_ACCENT)
    
    lisitra_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, height=200, width=350)

    def kajy_solde_sy_lisitra():
        lisitra_column.controls.clear()
        conn = sqlite3.connect("fitantanana_bola.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT antony, vola, karazana, sokajy FROM fifanakalozana ORDER BY id DESC")
        except sqlite3.OperationalError:
            cursor.execute("ALTER TABLE fifanakalozana ADD COLUMN sokajy TEXT")
            cursor.execute("SELECT antony, vola, karazana, sokajy FROM fifanakalozana ORDER BY id DESC")
            
        transactions = cursor.fetchall()
        
        total_miditra = 0
        total_mivoaka = 0
        
        for t in transactions:
            antony, vola, karazana, sokajy = t
            sokajy_aseho = f" [{sokajy}]" if (karazana == "Mivoaka" and sokajy) else ""
            
            if karazana == "Miditra":
                total_miditra += vola
                loko = ft.Colors.GREEN_400
                marika = "+"
            else:
                total_mivoaka += vola
                loko = ft.Colors.RED_400
                marika = "-"
                
            lisitra_column.controls.add(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{antony}{sokajy_aseho}", weight=ft.FontWeight.BOLD, expand=True),
                            ft.Text(f"{marika} {vola:,} Ar", color=loko, weight=ft.FontWeight.BOLD)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    padding=10,
                    border_radius=8,
                    bgcolor=ft.Colors.SURFACE_CONTAINER
                )
            )
            
        entree_text.value = f"Total ENTREE : +{total_miditra:,} Ar"
        sortie_text.value = f"Total SORTIE : -{total_mivoaka:,} Ar"
        
        vola_sisa = total_miditra - total_mivoaka
        vola_final_text.value = f"Vola Sisa (FINALE) : {vola_sisa:,} Ar"
        
        if vola_sisa >= 0:
            vola_final_text.color = ft.Colors.BLUE_ACCENT
        else:
            vola_final_text.color = ft.Colors.RED_400
            
        conn.close()
        page.update()

    def ampidiro_bola(e):
        if not antony_input.value or not vola_input.value:
            return
        
        try:
            vola_nampidirina = float(vola_input.value)
        except ValueError:
            return
            
        sokajy_fandaniana = sokajy_dropdown.value if karazana_state == "Mivoaka" else "PLUS"
        if not sokajy_fandaniana:
            sokajy_fandaniana = "PLUS"
            
        conn = sqlite3.connect("fitantanana_bola.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO fifanakalozana (antony, vola, karazana, sokajy) VALUES (?, ?, ?, ?)",
            (antony_input.value, vola_nampidirina, karazana_state, sokajy_fandaniana)
        )
        conn.commit()
        conn.close()
        
        antony_input.value = ""
        vola_input.value = ""
        
        kajy_solde_sy_lisitra()

    # Ny bokotra lehibe handefasana ny kajy rehetra
    bokotra_hampiditra = ft.ElevatedButton(
        text="Tahiry & Kajy",
        on_click=ampidiro_bola
    )

    kajy_solde_sy_lisitra()

    page.add(
        ft.Container(
            content=ft.Column(
                [
                    ft.Text("TOJONIRINA - Fitantanana Vola", size=24, weight=ft.FontWeight.BOLD),
                    ft.Divider(height=10, color=ft.Colors.TRANSPARENT),
                    
                    ft.Container(
                        content=ft.Column([
                            entree_text,
                            sortie_text,
                            ft.Divider(height=5, color=ft.Colors.WHITE24),
                            vola_final_text
                        ]),
                        padding=15,
                        border_radius=10,
                        bgcolor=ft.Colors.SURFACE_CONTAINER_HIGH,
                        width=350
                    ),
                    
                    ft.Divider(height=15),
                    antony_input,
                    ft.Text("Safidio ny karazana :", weight=ft.FontWeight.BOLD),
                    ft.Row([btn_entree, btn_base_sortie], alignment=ft.MainAxisAlignment.CENTER),
                    karazana_iditra,
                    sokajy_label,
                    sokajy_dropdown,  
                    vola_input,
                    bokotra_hampiditra,
                    ft.Divider(height=15),
                    ft.Text("Ireo fidirana sy fivoahana farany :", size=16, weight=ft.FontWeight.W_500),
                    lisitra_column
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=20,
            alignment=ft.alignment.center
        )
    )

if __name__ == "__main__":
    ft.app(target=main)