import flet as ft
import json
import os
from datetime import datetime

DATA_FILE = "data_bola.json"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            return {"solde_initial": 0.0, "solde_actuel": 0.0, "history": []}
    return {"solde_initial": 0.0, "solde_actuel": 0.0, "history": []}

def save_data(solde_init, solde_act, history):
    data = {"solde_initial": solde_init, "solde_actuel": solde_act, "history": history}
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def main(page: ft.Page):
    page.title = "TOJONIRINA - Gestion Financière"
    page.window_width = 460
    page.window_height = 850
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    
    # --- CHANGEMENT EN MODE SOMBRE ---
    page.theme_mode = ft.ThemeMode.DARK

    # Chargement des données
    user_data = load_data()
    page.data = {
        "solde_initial": user_data.get("solde_initial", 0.0),
        "solde_actuel": user_data.get("solde_actuel", 0.0),
        "history": user_data.get("history", [])
    }

    # --- COMPOSANTS GRAPHIQUES ---
    lohateny = ft.Text("Gestion Financière", size=28, weight=ft.FontWeight.BOLD, color="#60A5FA") # Bleu clair pour le mode sombre
    
    # Textes du Dashboard
    lbl_brut = ft.Text("0 Ar", size=16, weight=ft.FontWeight.BOLD, color="#60A5FA")
    lbl_entree = ft.Text("0 Ar", size=16, weight=ft.FontWeight.BOLD, color="#4ADE80") # Vert clair
    lbl_sortie = ft.Text("0 Ar", size=16, weight=ft.FontWeight.BOLD, color="#F87171") # Rouge clair
    lbl_solde_actuel = ft.Text("Solde Actuel : 0 Ar", size=22, weight=ft.FontWeight.BOLD, color="white")

    # --- DASHBOARD SOMBRE ---
    dashboard = ft.Container(
        content=ft.Column([
            ft.Container(content=lbl_solde_actuel, alignment=ft.Alignment(0, 0), padding=5),
            ft.Divider(color="#4B5563"),
            ft.Row([
                ft.Column([ft.Text("INITIAL (BRUT)", size=11, color="#9CA3AF", weight=ft.FontWeight.W_500), lbl_brut], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.VerticalDivider(color="#4B5563"),
                ft.Column([ft.Text("TOTAL ENTRÉES", size=11, color="#9CA3AF", weight=ft.FontWeight.W_500), lbl_entree], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                ft.VerticalDivider(color="#4B5563"),
                ft.Column([ft.Text("TOTAL SORTIES", size=11, color="#9CA3AF", weight=ft.FontWeight.W_500), lbl_sortie], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ], alignment=ft.MainAxisAlignment.SPACE_EVENLY, height=50)
        ]),
        bgcolor="#1F2937", # Fond gris foncé (Anthracite)
        border_radius=15,
        padding=15,
        border=ft.Border(
            top=ft.BorderSide(1, "#374151"),
            bottom=ft.BorderSide(1, "#374151"),
            left=ft.BorderSide(1, "#374151"),
            right=ft.BorderSide(1, "#374151")
        ),
        width=400,
        margin=10
    )
    
    # --- 1. SECTION MODIFIER SOLDE INITIAL ---
    txt_initial = ft.TextField(
        label="Nouveau Montant Brut (Ar)", 
        value=str(page.data["solde_initial"]) if page.data["solde_initial"] > 0 else "",
        keyboard_type=ft.KeyboardType.NUMBER, 
        width=230,
        dense=True
    )
    
    def definir_solde_initial(e):
        if not txt_initial.value:
            fampandrenesana.value = "Veuillez entrer le montant brut initial !"
            fampandrenesana.color = "#F87171"
            page.update()
            return
        try:
            vola_brut = float(txt_initial.value)
        except ValueError:
            fampandrenesana.value = "Le montant doit être un nombre valide !"
            fampandrenesana.color = "#F87171"
            page.update()
            return
        
        mouvement_avant = page.data["solde_actuel"] - page.data["solde_initial"]
        page.data["solde_initial"] = vola_brut
        page.data["solde_actuel"] = vola_brut + mouvement_avant
        
        save_data(page.data["solde_initial"], page.data["solde_actuel"], page.data["history"])
        fampandrenesana.value = "Solde initial mis à jour !"
        fampandrenesana.color = "#60A5FA"
        charger_historique()
        page.update()

    bokotra_initial = ft.ElevatedButton("MODIFIER BRUT", on_click=definir_solde_initial, bgcolor="#3B82F6", color="white")
    row_initial = ft.Row([txt_initial, bokotra_initial], alignment=ft.MainAxisAlignment.CENTER)

    # --- 2. SECTION TRANSACTIONS ---
    txt_motif = ft.Dropdown(
        label="Motif / Description",
        hint_text="Choisissez un motif...",
        width=380,
        options=[
            ft.dropdown.Option("Frais"),
            ft.dropdown.Option("Goûter"),
            ft.dropdown.Option("Salaire"),
            ft.dropdown.Option("Achat"),
            ft.dropdown.Option("Divers"),
        ]
    )
    
    txt_montant = ft.TextField(label="Montant (Ar)", keyboard_type=ft.KeyboardType.NUMBER, width=380)
    fampandrenesana = ft.Text("", size=14, color="#F87171")

    # --- 3. SECTION TABLEAU ---
    tableau_transactions = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Date", weight=ft.FontWeight.BOLD, color="#9CA3AF")),
            ft.DataColumn(ft.Text("Motif", weight=ft.FontWeight.BOLD, color="#9CA3AF")),
            ft.DataColumn(ft.Text("Montant", weight=ft.FontWeight.BOLD, color="#9CA3AF")),
            ft.DataColumn(ft.Text("Type", weight=ft.FontWeight.BOLD, color="#9CA3AF")),
        ],
        rows=[],
        column_spacing=25
    )

    zone_tableau = ft.Column(controls=[tableau_transactions], scroll=ft.ScrollMode.AUTO, height=200, width=400)

    def charger_historique():
        t_entree = 0.0
        t_sortie = 0.0
        for t in page.data["history"]:
            if t["type"] == "entree":
                t_entree += t["montant"]
            elif t["type"] == "sortie":
                t_sortie += t["montant"]

        lbl_brut.value = f"{page.data['solde_initial']} Ar"
        lbl_entree.value = f"{t_entree} Ar"
        lbl_sortie.value = f"{t_sortie} Ar"
        lbl_solde_actuel.value = f"Solde Actuel : {page.data['solde_actuel']} Ar"
        lbl_solde_actuel.color = "#4ADE80" if page.data['solde_actuel'] >= 0 else "#F87171"

        tableau_transactions.rows.clear()
        for t in reversed(page.data["history"]):
            loko = "#4ADE80" if t["type"] == "entree" else "#F87171"
            marika = "+" if t["type"] == "entree" else "-"
            date_trans = t.get("date", "")
            
            tableau_transactions.rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(date_trans, size=12, color="white")),
                        ft.DataCell(ft.Text(t["motif"], size=12, color="white")),
                        ft.DataCell(ft.Text(f"{t['montant']} Ar", color=loko, weight=ft.FontWeight.BOLD, size=12)),
                        ft.DataCell(ft.Text(f"{marika} {t['type'].upper()}", color=loko, size=11)),
                    ]
                )
            )
        page.update()

    def gerer_transaction(is_entree):
        if not txt_motif.value or not txt_montant.value:
            fampandrenesana.value = "Veuillez choisir un Motif et remplir le Montant !"
            fampandrenesana.color = "#F87171"
            page.update()
            return
        try:
            valeur_vola = float(txt_montant.value)
        except ValueError:
            fampandrenesana.value = "Le montant doit être un nombre valide !"
            fampandrenesana.color = "#F87171"
            page.update()
            return

        if is_entree:
            page.data["solde_actuel"] += valeur_vola
        else:
            page.data["solde_actuel"] -= valeur_vola

        date_aujourdhui = datetime.now().strftime("%d/%m/%Y")

        page.data["history"].append({
            "date": date_aujourdhui,
            "motif": txt_motif.value,
            "montant": valeur_vola,
            "type": "entree" if is_entree else "sortie"
        })

        save_data(page.data["solde_initial"], page.data["solde_actuel"], page.data["history"])
        
        charger_historique()
        fampandrenesana.value = f"Succès : '{txt_motif.value}' enregistré !"
        fampandrenesana.color = "#60A5FA"
        txt_motif.value = None
        txt_montant.value = ""
        page.update()

    bokotra_entree = ft.ElevatedButton("ENTRÉE", on_click=lambda e: gerer_transaction(is_entree=True), bgcolor="#10B981", color="white", width=170)
    bokotra_sortie = ft.ElevatedButton("SORTIE", on_click=lambda e: gerer_transaction(is_entree=False), bgcolor="#EF4444", color="white", width=170)

    # --- ENREGISTREMENT SUR LA PAGE ---
    page.add(
        ft.Container(content=lohateny, margin=5),
        
        dashboard,
        fampandrenesana,
        ft.Divider(color="#374151"),
        
        ft.Text("Modifier le Solde Initial (Montant Brut) :", weight=ft.FontWeight.BOLD, color="#60A5FA", size=13),
        row_initial,
        ft.Divider(color="#374151"),
        
        ft.Text("Nouvelle Transaction :", weight=ft.FontWeight.BOLD, color="#60A5FA", size=13),
        txt_motif,
        txt_montant,
        ft.Container(margin=2),
        ft.Row([bokotra_entree, bokotra_sortie], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(color="#374151"),
        
        ft.Text("Historique des transactions :", weight=ft.FontWeight.BOLD, size=15, color="white"),
        zone_tableau
    )

    charger_historique()

# --- CORRECTION DE LA LIGNE CI-DESSOUS ---
ft.app(target=main, assets_dir="assets")
