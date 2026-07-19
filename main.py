import flet as ft
import json
import os
from datetime import datetime

DATA_FILE = "data_bola.json"

def format_ariary(montant):
    return f"{int(montant):,}".replace(",", ".") + " Ar"

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: 
                data = json.load(f)
                if "total_entree" not in data: data["total_entree"] = 0.0
                if "total_sortie" not in data: data["total_sortie"] = 0.0
                return data
        except: pass
    return {"solde_initial": 0.0, "solde_actuel": 0.0, "history": [], "total_entree": 0.0, "total_sortie": 0.0}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

def main(page: ft.Page):
    page.title = "SUIVI FINANCIERE"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.START
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    data = load_data()

    lbl_solde = ft.Text(format_ariary(data.get('solde_actuel', 0)), size=32, weight="bold", color="#60A5FA")
    lbl_entree_total = ft.Text(format_ariary(data.get('total_entree', 0)), color="#10B981", weight="bold")
    lbl_sortie_total = ft.Text(format_ariary(data.get('total_sortie', 0)), color="#EF4444", weight="bold")

    txt_solde_initial = ft.TextField(label="Nouveau Montant Initial (Ar)", keyboard_type="number", width=350)
    txt_motif = ft.Dropdown(label="Motif", width=350, options=[
        ft.dropdown.Option("CREDIT"), ft.dropdown.Option("FRAIS"), ft.dropdown.Option("GOUTTER"),
        ft.dropdown.Option("DEVOIR SABATH"), ft.dropdown.Option("SANTE"),
        ft.dropdown.Option("NOM"), ft.dropdown.Option("PLUS")
    ])
    txt_motif_perso = ft.TextField(label="Motif perso", width=350, visible=False)
    txt_montant = ft.TextField(label="Montant en Ar", keyboard_type="number", width=350)

    def delete_transaction(index):
        actual_index = (len(data["history"]) - 1) - index
        item = data["history"].pop(actual_index)
        if item.get("type") == "entree":
            data["solde_actuel"] -= item["montant"]
            data["total_entree"] -= item["montant"]
        else:
            data["solde_actuel"] += item["montant"]
            data["total_sortie"] -= item["montant"]
        save_data(data)
        update_ui()

    def update_ui():
        lbl_solde.value = format_ariary(data.get('solde_actuel', 0))
        lbl_entree_total.value = format_ariary(data.get('total_entree', 0))
        lbl_sortie_total.value = format_ariary(data.get('total_sortie', 0))
        tableau.rows.clear()
        history = data.get("history", [])
        for i in range(len(history) - 1, -1, -1):
            t = history[i]
            tableau.rows.append(ft.DataRow(cells=[
                ft.DataCell(ft.Text(t.get("date", ""))), 
                ft.DataCell(ft.Text(t.get("motif", ""))), 
                ft.DataCell(ft.Text(format_ariary(t.get("montant", 0)))),
                ft.DataCell(ft.TextButton("X", on_click=lambda e, i=i: delete_transaction(i)))
            ]))
        page.update()

    def add_transaction(is_entree):
        try:
            val = float(txt_montant.value)
            motif = txt_motif_perso.value if txt_motif.value == "PLUS" else txt_motif.value
            if is_entree:
                data["solde_actuel"] += val
                data["total_entree"] += val
            else:
                data["solde_actuel"] -= val
                data["total_sortie"] += val
            data["history"].append({"date": datetime.now().strftime("%d/%m/%Y"), "motif": motif or "N/A", "montant": val, "type": "entree" if is_entree else "sortie"})
            save_data(data)
            
            # Fafana ny sanda
            txt_montant.value = ""
            txt_motif_perso.value = ""
            txt_motif_perso.visible = False
            txt_motif.value = None
            
            update_ui()
        except: pass

    txt_motif.on_change = lambda e: (setattr(txt_motif_perso, "visible", txt_motif.value == "PLUS"), page.update())

    tableau = ft.DataTable(columns=[ft.DataColumn(ft.Text("Date")), ft.DataColumn(ft.Text("Motif")), ft.DataColumn(ft.Text("Mnt")), ft.DataColumn(ft.Text("X"))], rows=[])

    page.add(
        ft.Container(content=ft.Column([
            ft.Text("SOLDE FINAL", color="grey"), lbl_solde,
            ft.Row([ft.Column([ft.Text("ENTRÉE", color="#10B981"), lbl_entree_total], horizontal_alignment="center"),
                    ft.Column([ft.Text("SORTIE", color="#EF4444"), lbl_sortie_total], horizontal_alignment="center")], alignment="spaceEvenly")
        ], horizontal_alignment="center"), bgcolor="#1F2937", padding=20, border_radius=10, width=380),
        ft.Divider(),
        txt_solde_initial, 
        ft.ElevatedButton(
            "METTRE À JOUR SOLDE", 
            on_click=lambda e: (
                data.update({"solde_actuel": float(txt_solde_initial.value or 0), "total_entree": 0.0, "total_sortie": 0.0, "history": []}),
                setattr(txt_solde_initial, "value", ""),
                save_data(data), 
                update_ui()
            ), 
            bgcolor="blue", color="white"
        ),
        ft.Divider(),
        txt_motif, txt_motif_perso, txt_montant,
        ft.Row([ft.ElevatedButton("ENTRÉE", on_click=lambda e: add_transaction(True), bgcolor="#10B981", color="white", width=160),
                ft.ElevatedButton("SORTIE", on_click=lambda e: add_transaction(False), bgcolor="#EF4444", color="white", width=160)], alignment="center"),
        ft.Text("Historique"), ft.Container(content=tableau, width=400)
    )
    update_ui()

ft.app(target=main)
