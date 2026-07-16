import os
import re
import shutil
from datetime import date
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QScrollArea, QGridLayout, QFrame,
                             QStackedWidget, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QLineEdit, QSpinBox, QFileDialog, QDateEdit,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from database import (get_corsi_professore, get_tutti_corsi_laurea, crea_nuova_materia,
                      get_materiale_corso, get_info_materia, aggiungi_materiale_corso,
                      get_path_materiale, elimina_materiale_corso, cambia_password, DB_PATH)


# --- CLASSE PERSONALIZZATA PER I QUADRATI DEI CORSI ---
class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ==========================================
# POPUP (QDIALOG) PER CREARE LA NUOVA MATERIA
# ==========================================
class DialogNuovaMateria(QDialog):
    def __init__(self, id_professore, parent=None):
        super().__init__(parent)
        self.id_professore = id_professore
        self.setWindowTitle("Crea Nuova Materia")
        self.setFixedSize(450, 250)

        layout = QVBoxLayout(self)

        lbl_titolo = QLabel("Compila i dettagli della nuova materia")
        lbl_titolo.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(lbl_titolo)
        layout.addSpacing(10)

        form_layout = QFormLayout()

        self.combo_corso = QComboBox()
        self.corsi_disponibili = get_tutti_corsi_laurea()
        for c in self.corsi_disponibili:
            self.combo_corso.addItem(c['nome'], c['id_corso'])

        self.input_nome = QLineEdit()
        self.input_nome.setPlaceholderText("Es: Fisica Generale")

        self.input_cfu = QSpinBox()
        self.input_cfu.setRange(1, 18)
        self.input_cfu.setValue(6)

        form_layout.addRow("Corso di Laurea:", self.combo_corso)
        form_layout.addRow("Nome Materia:", self.input_nome)
        form_layout.addRow("Numero CFU:", self.input_cfu)

        layout.addLayout(form_layout)
        layout.addSpacing(15)

        btn_layout = QHBoxLayout()
        btn_salva = QPushButton("SALVA E CREA CARTELLA")
        btn_salva.setStyleSheet(
            "background-color: #20B2AA; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        btn_salva.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salva.clicked.connect(self.salva_materia)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_salva)
        layout.addLayout(btn_layout)

    def salva_materia(self):
        nome_materia = self.input_nome.text().strip()
        cfu = self.input_cfu.value()
        id_corso_laurea = self.combo_corso.currentData()
        nome_corso_laurea = self.combo_corso.currentText()

        if not nome_materia:
            QMessageBox.warning(self, "Attenzione", "Devi inserire il nome della materia.")
            return

        successo, msg = crea_nuova_materia(self.id_professore, nome_materia, cfu, id_corso_laurea)

        if successo:
            def pulisci_stringa(testo):
                return re.sub(r'\W+', '_', testo.lower()).strip('_')

            cartella_corso = pulisci_stringa(nome_corso_laurea)
            cartella_materia = pulisci_stringa(nome_materia)

            base_dir = os.path.dirname(os.path.abspath(__file__))
            path_assoluto = os.path.join(base_dir, "corso", cartella_corso, cartella_materia)

            try:
                os.makedirs(path_assoluto, exist_ok=True)
                QMessageBox.information(self, "Successo",
                                        f"Materia creata con successo!\n\nCartella creata in:\n{path_assoluto}")
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, "Attenzione",
                                    f"Materia salvata nel DB, ma impossibile creare la cartella.\nErrore: {e}")
                self.accept()
        else:
            QMessageBox.critical(self, "Errore Database", f"Impossibile salvare la materia: {msg}")


# ==========================================
# POPUP (QDIALOG) PER LA CREAZIONE APPELLO
# ==========================================
class DialogCreaAppello(QDialog):
    def __init__(self, id_materia, nome_materia, parent=None):
        super().__init__(parent)
        self.id_materia = id_materia
        self.setWindowTitle(f"Crea Appello - {nome_materia}")
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)

        lbl_titolo = QLabel(f"Programma Appello per:<br><b>{nome_materia.upper()}</b>")
        lbl_titolo.setFont(QFont("Arial", 11))
        layout.addWidget(lbl_titolo)
        layout.addSpacing(10)

        form_layout = QFormLayout()

        self.input_data = QDateEdit()
        self.input_data.setCalendarPopup(True)
        self.input_data.setDate(QDate.currentDate())
        self.input_data.setMinimumDate(QDate.currentDate())

        self.input_ora = QLineEdit()
        self.input_ora.setPlaceholderText("Es: 09:30")

        self.combo_aula = QComboBox()
        self.carica_aule_db()

        self.input_desc = QLineEdit()
        self.input_desc.setPlaceholderText("Es: Appello Sessione Estiva")

        form_layout.addRow("Data Esame:", self.input_data)
        form_layout.addRow("Ora Inizio:", self.input_ora)
        form_layout.addRow("Aula:", self.combo_aula)
        form_layout.addRow("Descrizione:", self.input_desc)

        layout.addLayout(form_layout)
        layout.addSpacing(15)

        btn_conferma = QPushButton("CONFERMA E CREA APPELLO")
        btn_conferma.setStyleSheet(
            "background-color: #FF8C00; color: white; font-weight: bold; padding: 10px; border-radius: 4px;")
        btn_conferma.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_conferma.clicked.connect(self.salva_appello)

        layout.addWidget(btn_conferma)

    def carica_aule_db(self):
        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()
            cursore.execute("SELECT ID_AULA, Nome FROM Aula_Appello")
            for r in cursore.fetchall():
                self.combo_aula.addItem(r[1], r[0])
            connessione.close()
        except Exception as e:
            print(f"Errore caricamento aule: {e}")
            self.combo_aula.addItem("Aula Magna (Default)", 1)

    def salva_appello(self):
        data_esame = self.input_data.date().toString("yyyy-MM-dd")
        ora = self.input_ora.text().strip()
        id_aula = self.combo_aula.currentData()
        descrizione = self.input_desc.text().strip()

        if not ora:
            QMessageBox.warning(self, "Attenzione", "Inserisci l'orario di inizio dell'appello.")
            return

        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()

            desc_finale = descrizione if descrizione else f"Appello {data_esame}"
            cursore.execute(
                "INSERT INTO Appello (Data, Ora_Inizio, Ora_Fine, Descrizione, Gruppo, Chiuso, COD_MATERIA, COD_AULA_APPELLO) VALUES (?, ?, ?, ?, ?, FALSE, ?, ?)",
                (data_esame, ora, "12:00:00", desc_finale, False, self.id_materia, id_aula)
            )
            connessione.commit()
            connessione.close()

            QMessageBox.information(self, "Successo", "Appello creato e salvato con successo nel sistema!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Errore DB", f"Impossibile salvare l'appello:\n{e}")


# ==========================================
# POPUP (QDIALOG) PER GESTIRE I TUTOR DEL CORSO
# ==========================================
class DialogGestisciTutor(QDialog):
    def __init__(self, id_materia, nome_materia, parent=None):
        super().__init__(parent)
        self.id_materia = id_materia

        # Recupera il nome del corso di laurea associato alla materia
        info = get_info_materia(id_materia)
        self.nome_corso = info[1] if info and info[0] != "Sconosciuto" else "Corso Generale"

        # Trova l'ID del corso di laurea
        self.id_corso = self._trova_id_corso()

        self.setWindowTitle(f"Gestione Tutor - {self.nome_corso}")
        self.resize(550, 400)

        layout = QVBoxLayout(self)

        lbl_titolo = QLabel(f"Tutor associati al Corso di Laurea:<br><b>{self.nome_corso.upper()}</b>")
        lbl_titolo.setFont(QFont("Arial", 11))
        layout.addWidget(lbl_titolo)
        layout.addSpacing(10)

        # Tabella dei tutor attuali del corso
        self.tabella_tutor = QTableWidget()
        self.tabella_tutor.setColumnCount(3)
        self.tabella_tutor.setHorizontalHeaderLabels(["ID", "NOME", "COGNOME"])
        self.tabella_tutor.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_tutor.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc;")
        layout.addWidget(self.tabella_tutor)

        layout.addSpacing(15)

        # Sezione per aggiungere un nuovo tutor al corso
        aggiungi_layout = QHBoxLayout()
        self.combo_tutor_disponibili = QComboBox()
        self.combo_tutor_disponibili.setStyleSheet("background-color: white; padding: 6px; color: black;")

        btn_aggiungi = QPushButton("➕ AGGIUNGI AL CORSO")
        btn_aggiungi.setStyleSheet(
            "background-color: #20B2AA; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        btn_aggiungi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiungi.clicked.connect(self.associa_tutor)

        aggiungi_layout.addWidget(QLabel("<b>Seleziona Tutor:</b>"))
        aggiungi_layout.addWidget(self.combo_tutor_disponibili)
        aggiungi_layout.addWidget(btn_aggiungi)

        layout.addLayout(aggiungi_layout)

        self.carica_dati_tutor()

    def _trova_id_corso(self):
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COD_CORSO FROM Corso_Materia WHERE COD_MATERIA = ?", (self.id_materia,))
            res = cur.fetchone()
            conn.close()
            return res[0] if res else 1
        except Exception:
            return 1

    def carica_dati_tutor(self):
        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # 1. Carica i tutor già associati a questo corso
            cur.execute("""
                        SELECT u.ID_UTENTE, u.Nome, u.Cognome
                        FROM Corso_Tutor ct
                                 JOIN Tutor t ON ct.COD_TUTOR = t.ID_TUTOR
                                 JOIN Utente u ON t.ID_TUTOR = u.ID_UTENTE
                        WHERE ct.COD_CORSO = ?
                        """, (self.id_corso,))
            tutor_associati = cur.fetchall()

            self.tabella_tutor.setRowCount(len(tutor_associati))
            if not tutor_associati:
                self.tabella_tutor.setRowCount(1)
                self.tabella_tutor.setItem(0, 0, QTableWidgetItem("-"))
                self.tabella_tutor.setItem(0, 1, QTableWidgetItem("Nessun tutor associato a questo corso"))
                self.tabella_tutor.setItem(0, 2, QTableWidgetItem("-"))
            else:
                for riga, t in enumerate(tutor_associati):
                    it0 = QTableWidgetItem(str(t[0]))
                    it1 = QTableWidgetItem(t[1])
                    it2 = QTableWidgetItem(t[2])
                    it0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabella_tutor.setItem(riga, 0, it0)
                    self.tabella_tutor.setItem(riga, 1, it1)
                    self.tabella_tutor.setItem(riga, 2, it2)

            # 2. Carica nel menu a tendina i tutor NON ancora associati a questo corso
            self.combo_tutor_disponibili.clear()
            cur.execute("""
                        SELECT u.ID_UTENTE, u.Nome, u.Cognome
                        FROM Tutor t
                                 JOIN Utente u ON t.ID_TUTOR = u.ID_UTENTE
                        WHERE t.ID_TUTOR NOT IN (SELECT COD_TUTOR
                                                 FROM Corso_Tutor
                                                 WHERE COD_CORSO = ?)
                        """, (self.id_corso,))
            disponibili = cur.fetchall()

            for d in disponibili:
                self.combo_tutor_disponibili.addItem(f"{d[1]} {d[2]} (ID: {d[0]})", d[0])

            if not disponibili:
                self.combo_tutor_disponibili.addItem("-- Nessun altro tutor disponibile --", None)

            conn.close()
        except Exception as e:
            print(f"Errore caricamento tutor: {e}")

    def associa_tutor(self):
        id_tutor = self.combo_tutor_disponibili.currentData()
        if not id_tutor:
            QMessageBox.warning(self, "Attenzione", "Seleziona un tutor valido da aggiungere.")
            return

        import sqlite3
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) VALUES (?, ?)", (id_tutor, self.id_corso))
            conn.commit()
            conn.close()

            QMessageBox.information(self, "Successo", "Tutor associato con successo al corso di laurea!")
            self.carica_dati_tutor()
        except Exception as e:
            QMessageBox.critical(self, "Errore DB", f"Impossibile associare il tutor:\n{e}")


# ==========================================
# POPUP (QDIALOG) PER VISUALIZZARE STATISTICHE APPELLO CHIUSO
# ==========================================
class DialogStatisticheAppello(QDialog):
    def __init__(self, id_materia, nome_materia, parent=None):
        super().__init__(parent)
        self.id_materia = id_materia
        self.setWindowTitle(f"Statistiche Appelli Chiusi - {nome_materia}")
        self.resize(500, 450)

        layout = QVBoxLayout(self)

        lbl_titolo = QLabel(
            f"Seleziona un appello chiuso per visualizzare le statistiche:<br><b>{nome_materia.upper()}</b>")
        lbl_titolo.setFont(QFont("Arial", 11))
        layout.addWidget(lbl_titolo)

        self.tabella_chiusi = QTableWidget()
        self.tabella_chiusi.setColumnCount(3)
        self.tabella_chiusi.setHorizontalHeaderLabels(["ID", "DESCRIZIONE", "DATA"])
        self.tabella_chiusi.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_chiusi.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabella_chiusi.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc;")
        layout.addWidget(self.tabella_chiusi)

        btn_stat = QLabel("<b>Dettaglio Statistiche (Percentuali di superamento):</b>")
        layout.addWidget(btn_stat)

        self.lbl_risultati_stat = QLabel("Seleziona un appello sopra per calcolare le statistiche.")
        self.lbl_risultati_stat.setStyleSheet(
            "background-color: white; padding: 15px; border-radius: 5px; color: black; border: 1px solid #ccc;")
        self.lbl_risultati_stat.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(self.lbl_risultati_stat)

        self.tabella_chiusi.itemSelectionChanged.connect(self.calcola_statistiche_appello)

        self.carica_appelli_chiusi()

    def carica_appelli_chiusi(self):
        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()
            cursore.execute("SELECT ID_APPELLO, Descrizione, Data FROM Appello WHERE COD_MATERIA = ? AND Chiuso = TRUE",
                            (self.id_materia,))
            risultati = cursore.fetchall()
            connessione.close()

            self.tabella_chiusi.setRowCount(len(risultati))
            if not risultati:
                self.tabella_chiusi.setRowCount(1)
                self.tabella_chiusi.setItem(0, 0, QTableWidgetItem("-"))
                self.tabella_chiusi.setItem(0, 1, QTableWidgetItem("Nessun appello chiuso disponibile"))
                self.tabella_chiusi.setItem(0, 2, QTableWidgetItem("-"))
                return

            for riga, app in enumerate(risultati):
                it0 = QTableWidgetItem(str(app[0]))
                it1 = QTableWidgetItem(str(app[1]))
                it2 = QTableWidgetItem(str(app[2]))
                it0.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.tabella_chiusi.setItem(riga, 0, it0)
                self.tabella_chiusi.setItem(riga, 1, it1)
                self.tabella_chiusi.setItem(riga, 2, it2)
        except Exception as e:
            print(f"Errore caricamento appelli chiusi: {e}")

    def calcola_statistiche_appello(self):
        selected_rows = self.tabella_chiusi.selectedItems()
        if not selected_rows:
            return

        row = selected_rows[0].row()
        id_appello_item = self.tabella_chiusi.item(row, 0)
        if not id_appello_item or id_appello_item.text() == "-":
            return

        id_appello = int(id_appello_item.text())

        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()

            cursore.execute("SELECT COUNT(*) FROM Esito_Appello_Studente WHERE COD_APPELLO = ? AND Stato = 'Superato'",
                            (id_appello,))
            superati = cursore.fetchone()[0]

            cursore.execute("SELECT COUNT(*) FROM Esito_Appello_Studente WHERE COD_APPELLO = ? AND Stato = 'Respinto'",
                            (id_appello,))
            bocciati = cursore.fetchone()[0]

            totale = superati + bocciati

            if totale == 0:
                testo = f"<b>Risultati Statistici per l'Appello ID:</b> {id_appello}<br><br>Nessun voto registrato in questo appello."
            else:
                perc_superati = (superati / totale) * 100
                perc_bocciati = (bocciati / totale) * 100
                testo = (
                    f"<b>📊 STATISTICHE APPELLO ID: {id_appello}</b><br><br>"
                    f"• <b>Totale Studenti Valutati:</b> {totale}<br>"
                    f"• <span style='color:green;'><b>Hanno passato l'esame (≥ 18):</b></span> {superati} ({perc_superati:.1f}%)<br>"
                    f"• <span style='color:red;'><b>Non superato (< 18):</b></span> {bocciati} ({perc_bocciati:.1f}%)<br><br>"
                    f"<i>[Rappresentazione Grafica a Barre]</i><br>"
                    f"{'█' * int(perc_superati // 5)} {perc_superati:.1f}% Superati<br>"
                    f"{'█' * int(perc_bocciati // 5)} {perc_bocciati:.1f}% Non Superati"
                )

            self.lbl_risultati_stat.setText(testo)
            connessione.close()
        except Exception as e:
            self.lbl_risultati_stat.setText(f"Errore calcolo statistiche: {e}")


# ==========================================
# DASHBOARD PRINCIPALE DEL PROFESSORE
# ==========================================
class ProfessorDashboard(QWidget):
    def __init__(self, id_utente, nome, cognome):
        super().__init__()
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.matricola = f"DOC{id_utente}00"
        self.corso_corrente_id = None
        self.corso_corrente_nome = ""

        self.setWindowTitle("Dashboard Professore - Gestionale UNIVPM")
        self.setMinimumSize(1100, 700)
        self.menu_buttons = {}
        self._inizializza_ui()

    def _inizializza_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. BARRA LATERALE
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: white; border-right: 1px solid #ccc;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_icona = QLabel("👤")
        lbl_icona.setFont(QFont("Arial", 40))
        lbl_icona.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icona.setStyleSheet("border: none; margin-top: 20px; color: black;")

        lbl_nome = QLabel(f"PROF. {self.nome.upper()} {self.cognome.upper()}")
        lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nome.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_nome.setStyleSheet("border: none; color: black;")

        lbl_matricola = QLabel(self.matricola)
        lbl_matricola.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_matricola.setStyleSheet("border: none; color: #666; margin-bottom: 20px;")

        sidebar_layout.addWidget(lbl_icona)
        sidebar_layout.addWidget(lbl_nome)
        sidebar_layout.addWidget(lbl_matricola)

        # 2. GESTORE PAGINE
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #E0E0E0;")

        self.pagina_home = self._crea_pagina_home()
        self.pagina_appelli = self._crea_pagina_appelli()
        self.pagina_impostazioni = self._crea_pagina_impostazioni()
        self.pagina_dettaglio = self._crea_pagina_dettaglio_corso()

        self.stacked_widget.addWidget(self.pagina_home)  # Indice 0
        self.stacked_widget.addWidget(self.pagina_appelli)  # Indice 1 (Gestione Appelli Aperti)
        self.stacked_widget.addWidget(self.pagina_impostazioni)  # Indice 2 (Impostazioni)
        self.stacked_widget.addWidget(self.pagina_dettaglio)  # Indice 3 (Gestione Materia)

        menu_items = [
            ("🏠 HOME / LE MIE MATERIE", 0),
            ("📅 GESTIONE APPELLI", 1),
            ("⚙️ IMPOSTAZIONI", 2)
        ]

        for test, index in menu_items:
            btn = QPushButton(test)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index, b=btn: self.cambia_pagina(idx, b))
            self.menu_buttons[btn] = test
            sidebar_layout.addWidget(btn)

        primo_bottone = list(self.menu_buttons.keys())[0]
        self.cambia_pagina(0, primo_bottone)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def cambia_pagina(self, index, active_button=None):
        self.stacked_widget.setCurrentIndex(index)

        if index == 0:
            self.ricarica_pagina_home()
        elif index == 1:
            self.ricarica_pagina_appelli()
        elif index == 2:
            self.ricarica_pagina_impostazioni()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet(
                "background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")

        if active_button:
            active_button.setStyleSheet(
                "background-color: #20B2AA; color: white; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 5px;")

    # ==========================================
    # PAGINA 0: HOME / LE MIE MATERIE
    # ==========================================
    def _crea_pagina_home(self):
        page = QWidget()
        self.layout_home = QVBoxLayout(page)
        self.layout_home.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()

        lbl_titolo = QLabel("LE MIE MATERIE ATTIVE")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: black;")

        btn_nuova_materia = QPushButton("➕ NUOVA MATERIA")
        btn_nuova_materia.setStyleSheet("""
            background-color: #0055A4; 
            color: white; 
            padding: 10px 20px; 
            font-weight: bold; 
            border-radius: 5px;
        """)
        btn_nuova_materia.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nuova_materia.clicked.connect(self.apri_creazione_materia)

        header_layout.addWidget(lbl_titolo)
        header_layout.addStretch()
        header_layout.addWidget(btn_nuova_materia)

        self.layout_home.addLayout(header_layout)
        self.layout_home.addSpacing(20)

        self.scroll_home = QScrollArea()
        self.scroll_home.setWidgetResizable(True)
        self.scroll_home.setStyleSheet("border: none; background-color: transparent;")

        self.contenitore_card_home = QWidget()
        self.griglia_home = QGridLayout(self.contenitore_card_home)
        self.griglia_home.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_home.setWidget(self.contenitore_card_home)

        self.layout_home.addWidget(self.scroll_home)
        return page

    def ricarica_pagina_home(self):
        for i in reversed(range(self.griglia_home.count())):
            w = self.griglia_home.itemAt(i).widget()
            self.griglia_home.removeWidget(w)
            w.setParent(None)

        corsi_reali = get_corsi_professore(self.id_utente)

        if not corsi_reali:
            lbl = QLabel("Non hai ancora creato nessuna materia.")
            lbl.setStyleSheet("color: black;")
            self.griglia_home.addWidget(lbl, 0, 0)
        else:
            r, c = 0, 0
            for corso in corsi_reali:
                info_materia = get_info_materia(corso['id_materia'])
                nome_corso_laurea = info_materia[1] if info_materia else "Corso Generale"

                card = ClickableFrame()
                card.setFixedSize(260, 210)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setStyleSheet(
                    "ClickableFrame { background-color: white; border-radius: 5px; padding: 10px; color: black; border: 1px solid #ccc; }")

                card.clicked.connect(
                    lambda id_m=corso['id_materia'], nome_m=corso['nome']: self.apri_dettaglio_corso(id_m, nome_m))

                lo = QVBoxLayout(card)

                testo_html = (
                    f"<span style='color:#0055A4; font-size:11px;'><b>{nome_corso_laurea.upper()}</b></span><br>"
                    f"<hr style='border: 0.5px solid #ccc;'>"
                    f"<b>{corso['nome'].upper()}</b><br>"
                    f"CFU: {corso['cfu']}<br>"
                    f"Anno: {corso['anno']}<br>"
                    f"Iscritti: {corso['iscritti']}<br>"
                    f"<span style='color:green; font-weight:bold;'>ATTIVO</span>"
                )

                lbl_testo = QLabel(testo_html)
                lbl_testo.setStyleSheet("border: none; background-color: transparent; color: black;")
                lbl_testo.setWordWrap(True)
                lbl_testo.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

                lo.addWidget(lbl_testo)
                self.griglia_home.addWidget(card, r, c)

                c += 1
                if c >= 3:
                    c = 0
                    r += 1

    # ==========================================
    # PAGINA 1: GESTIONE APPELLI (SOLO APERTI)
    # ==========================================
    def _crea_pagina_appelli(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl_titolo = QLabel("GESTIONE E RICERCA APPELLI APERTI")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: black;")
        layout.addWidget(lbl_titolo)
        layout.addSpacing(15)

        filtri_layout = QHBoxLayout()

        self.combo_filtro_corso = QComboBox()
        self.combo_filtro_corso.setStyleSheet("background-color: white; padding: 8px; color: black;")
        self.combo_filtro_corso.addItem("-- Seleziona Corso di Laurea --", None)
        self.combo_filtro_corso.currentIndexChanged.connect(self.aggiorna_materie_filtro)

        self.combo_filtro_materia = QComboBox()
        self.combo_filtro_materia.setStyleSheet("background-color: white; padding: 8px; color: black;")
        self.combo_filtro_materia.addItem("-- Seleziona prima il Corso --", None)
        self.combo_filtro_materia.setEnabled(False)

        btn_ricerca = QPushButton("🔍 AVVIA RICERCA")
        btn_ricerca.setStyleSheet(
            "background-color: #0055A4; color: white; font-weight: bold; padding: 8px 15px; border-radius: 4px;")
        btn_ricerca.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_ricerca.clicked.connect(self.esegui_ricerca_appelli)

        filtri_layout.addWidget(QLabel("<b>Corso:</b>"))
        filtri_layout.addWidget(self.combo_filtro_corso)
        filtri_layout.addWidget(QLabel("<b>Materia:</b>"))
        filtri_layout.addWidget(self.combo_filtro_materia)
        filtri_layout.addWidget(btn_ricerca)

        layout.addLayout(filtri_layout)
        layout.addSpacing(20)

        self.tabella_appelli = QTableWidget()
        self.tabella_appelli.setColumnCount(5)
        self.tabella_appelli.setHorizontalHeaderLabels(["MATERIA", "DATA", "ORA", "AULA", "AZIONI"])
        self.tabella_appelli.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabella_appelli.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc;")

        layout.addWidget(self.tabella_appelli)
        return page

    def ricarica_pagina_appelli(self):
        self.combo_filtro_corso.blockSignals(True)
        self.combo_filtro_corso.clear()
        self.combo_filtro_corso.addItem("-- Seleziona Corso di Laurea --", None)

        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()
            query = """
                    SELECT DISTINCT c.ID_CORSO, c.Nome
                    FROM Corso c
                             JOIN Corso_Materia cm ON c.ID_CORSO = cm.COD_CORSO
                             JOIN Materia m ON cm.COD_MATERIA = m.ID_MATERIA
                    WHERE m.COD_PROFESSORE = ? \
                    """
            cursore.execute(query, (self.id_utente,))
            for r in cursore.fetchall():
                self.combo_filtro_corso.addItem(r[1], r[0])
            connessione.close()
        except Exception as e:
            print(f"Errore caricamento corsi filtro: {e}")

        self.combo_filtro_corso.blockSignals(False)
        self.combo_filtro_materia.clear()
        self.combo_filtro_materia.addItem("-- Seleziona prima il Corso --", None)
        self.combo_filtro_materia.setEnabled(False)
        self.tabella_appelli.setRowCount(0)

    def aggiorna_materie_filtro(self, index):
        self.combo_filtro_materia.clear()
        id_corso = self.combo_filtro_corso.currentData()

        if id_corso is None:
            self.combo_filtro_materia.addItem("-- Seleziona prima il Corso --", None)
            self.combo_filtro_materia.setEnabled(False)
            return

        self.combo_filtro_materia.addItem("-- Tutte le Materie del Corso --", None)

        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()
            query = """
                    SELECT m.ID_MATERIA, m.Nome
                    FROM Materia m
                             JOIN Corso_Materia cm ON m.ID_MATERIA = cm.COD_MATERIA
                    WHERE cm.COD_CORSO = ? \
                      AND m.COD_PROFESSORE = ? \
                    """
            cursore.execute(query, (id_corso, self.id_utente))
            for r in cursore.fetchall():
                self.combo_filtro_materia.addItem(r[1], r[0])
            connessione.close()
            self.combo_filtro_materia.setEnabled(True)
        except Exception as e:
            print(f"Errore caricamento materie filtro: {e}")

    def esegui_ricerca_appelli(self):
        id_corso = self.combo_filtro_corso.currentData()
        id_materia = self.combo_filtro_materia.currentData()

        if id_corso is None:
            QMessageBox.warning(self, "Attenzione", "Seleziona almeno un Corso di Laurea per avviare la ricerca.")
            return

        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()

            if id_materia is not None:
                query = """
                        SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio, au.Nome
                        FROM Appello a
                                 JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                                 LEFT JOIN Aula_Appello au ON a.COD_AULA_APPELLO = au.ID_AULA
                        WHERE a.COD_MATERIA = ? \
                          AND (a.Chiuso = FALSE OR a.Chiuso IS NULL)
                        ORDER BY a.Data ASC \
                        """
                cursore.execute(query, (id_materia,))
            else:
                query = """
                        SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio, au.Nome
                        FROM Appello a
                                 JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                                 JOIN Corso_Materia cm ON m.ID_MATERIA = cm.COD_MATERIA
                                 LEFT JOIN Aula_Appello au ON a.COD_AULA_APPELLO = au.ID_AULA
                        WHERE cm.COD_CORSO = ? \
                          AND m.COD_PROFESSORE = ? \
                          AND (a.Chiuso = FALSE OR a.Chiuso IS NULL)
                        ORDER BY a.Data ASC \
                        """
                cursore.execute(query, (id_corso, self.id_utente))

            risultati = cursore.fetchall()
            connessione.close()

            self.tabella_appelli.setRowCount(len(risultati))
            if not risultati:
                QMessageBox.information(self, "Risultati", "Nessun appello aperto trovato per i filtri selezionati.")
                return

            for riga, app in enumerate(risultati):
                id_appello = app[0]
                nome_materia = app[1]
                self._inserisci_cella_tabella(self.tabella_appelli, riga, 0, nome_materia)
                self._inserisci_cella_tabella(self.tabella_appelli, riga, 1, app[2])
                self._inserisci_cella_tabella(self.tabella_appelli, riga, 2, app[3])
                aula_str = app[4] if app[4] else "Aula non specificata"
                self._inserisci_cella_tabella(self.tabella_appelli, riga, 3, aula_str)

                box_azioni = QWidget()
                ly_az = QHBoxLayout(box_azioni)
                ly_az.setContentsMargins(2, 2, 2, 2)

                btn_chiudi = QPushButton("📁 REGISTRA")
                btn_chiudi.setStyleSheet(
                    "background-color: #20B2AA; color: white; padding: 4px; font-weight: bold; border-radius: 3px;")
                btn_chiudi.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_chiudi.clicked.connect(
                    lambda ch, id_app=id_appello, m_nome=nome_materia: self.apri_chiusura_appello(id_app, m_nome))

                btn_elimina = QPushButton("❌ ELIMINA")
                btn_elimina.setStyleSheet(
                    "background-color: #D32F2F; color: white; padding: 4px; font-weight: bold; border-radius: 3px;")
                btn_elimina.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_elimina.clicked.connect(lambda ch, id_app=id_appello: self.elimina_appello_db(id_app))

                ly_az.addWidget(btn_chiudi)
                ly_az.addWidget(btn_elimina)

                self.tabella_appelli.setCellWidget(riga, 4, box_azioni)

        except Exception as e:
            QMessageBox.critical(self, "Errore DB", f"Impossibile effettuare la ricerca:\n{e}")

    def apri_chiusura_appello(self, id_appello, nome_materia):
        dialog = DialogChiusuraAppello(id_appello, nome_materia, self)
        if dialog.exec():
            self.esegui_ricerca_appelli()

    def elimina_appello_db(self, id_appello):
        import sqlite3
        try:
            connessione = sqlite3.connect(DB_PATH)
            cursore = connessione.cursor()
            cursore.execute("DELETE FROM Appello WHERE ID_APPELLO = ?", (id_appello,))
            connessione.commit()
            connessione.close()

            QMessageBox.information(self, "Successo", "Appello eliminato con successo!")
            self.esegui_ricerca_appelli()
        except Exception as e:
            QMessageBox.critical(self, "Errore", f"Impossibile eliminare l'appello:\n{e}")

    def _inserisci_cella_tabella(self, tabella, riga, colonna, testo):
        item = QTableWidgetItem(str(testo))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        tabella.setItem(riga, colonna, item)

    # ==========================================
    # PAGINA 2: IMPOSTAZIONI
    # ==========================================
    def _crea_pagina_impostazioni(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel("IMPOSTAZIONI GESTIONE PROFILO")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: black;")
        header_layout.addWidget(lbl_titolo)
        header_layout.addStretch()

        btn_logout = QPushButton("🚪 ESCI")
        btn_logout.setStyleSheet("background-color: transparent; font-size: 16px; font-weight: bold; color: #D32F2F;")
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.clicked.connect(self.esegui_logout)
        header_layout.addWidget(btn_logout)

        layout.addLayout(header_layout)
        layout.addSpacing(40)

        body_layout = QHBoxLayout()

        pwd_layout = QVBoxLayout()
        pwd_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_pwd = QLabel("CAMBIO PASSWORD")
        lbl_pwd.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_pwd.setStyleSheet("color: black; margin-bottom: 10px;")
        pwd_layout.addWidget(lbl_pwd)

        self.input_pwd_attuale = QLineEdit()
        self.input_pwd_attuale.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_attuale.setPlaceholderText("PASSWORD ATTUALE")
        self.input_pwd_attuale.setStyleSheet("background-color: white; color: black; padding: 10px;")

        self.input_pwd_nuova = QLineEdit()
        self.input_pwd_nuova.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_nuova.setPlaceholderText("NUOVA PASSWORD")
        self.input_pwd_nuova.setStyleSheet("background-color: white; color: black; padding: 10px;")

        self.input_pwd_conferma = QLineEdit()
        self.input_pwd_conferma.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_pwd_conferma.setPlaceholderText("CONFERMA NUOVA PASSWORD")
        self.input_pwd_conferma.setStyleSheet("background-color: white; color: black; padding: 10px;")

        btn_salva_pwd = QPushButton("AGGIORNA PASSWORD")
        btn_salva_pwd.setStyleSheet("background-color: #20B2AA; color: white; padding: 10px; font-weight: bold;")
        btn_salva_pwd.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_salva_pwd.clicked.connect(self.azione_cambia_password)

        pwd_layout.addWidget(self.input_pwd_attuale)
        pwd_layout.addWidget(self.input_pwd_nuova)
        pwd_layout.addWidget(self.input_pwd_conferma)
        pwd_layout.addWidget(btn_salva_pwd)

        body_layout.addLayout(pwd_layout)
        body_layout.addStretch()

        layout.addLayout(body_layout)
        layout.addStretch()

        return page

    def ricarica_pagina_impostazioni(self):
        self.input_pwd_attuale.clear()
        self.input_pwd_nuova.clear()
        self.input_pwd_conferma.clear()

    def azione_cambia_password(self):
        pwd_attuale = self.input_pwd_attuale.text()
        pwd_nuova = self.input_pwd_nuova.text()
        pwd_conferma = self.input_pwd_conferma.text()
        if not pwd_attuale or not pwd_nuova or not pwd_conferma:
            QMessageBox.warning(self, "Attenzione", "Compila tutti i campi della password.")
            return
        if pwd_nuova != pwd_conferma:
            QMessageBox.warning(self, "Attenzione", "Le nuove password non coincidono.")
            return

        successo, messaggio = cambia_password(self.id_utente, pwd_attuale, pwd_nuova)
        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.input_pwd_attuale.clear()
            self.input_pwd_nuova.clear()
            self.input_pwd_conferma.clear()
        else:
            QMessageBox.critical(self, "Errore", messaggio)

    def esegui_logout(self):
        from login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    # ==========================================
    # PAGINA 3: DETTAGLIO MATERIA E MATERIALE + STATISTICHE + GESTISCI TUTOR
    # ==========================================
    def _crea_pagina_dettaglio_corso(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        btn_indietro = QPushButton("⬅ TORNA ALLA HOME")
        btn_indietro.setStyleSheet(
            "background-color: transparent; color: #0055A4; font-weight: bold; text-align: left; padding: 0;")
        btn_indietro.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_indietro.clicked.connect(lambda: self.cambia_pagina(0, list(self.menu_buttons.keys())[0]))

        # BOTTONE GESTISCI TUTOR (NUOVO)
        btn_tutor = QPushButton("👥 GESTISCI TUTOR")
        btn_tutor.setStyleSheet(
            "background-color: #6A5ACD; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        btn_tutor.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_tutor.clicked.connect(self.apri_gestione_tutor)

        btn_statistiche = QPushButton("📊 STATISTICHE APPELLI")
        btn_statistiche.setStyleSheet(
            "background-color: #8A2BE2; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        btn_statistiche.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_statistiche.clicked.connect(self.apri_statistiche_appelli)

        btn_appello = QPushButton("📅 CREAZIONE APPELLO")
        btn_appello.setStyleSheet(
            "background-color: #FF8C00; color: white; padding: 10px; font-weight: bold; border-radius: 5px;")
        btn_appello.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_appello.clicked.connect(self.apri_creazione_appello)

        header_layout.addWidget(btn_indietro)
        header_layout.addStretch()
        header_layout.addWidget(btn_tutor)
        header_layout.addWidget(btn_statistiche)
        header_layout.addWidget(btn_appello)
        layout.addLayout(header_layout)

        self.lbl_titolo_dettaglio = QLabel("GESTIONE MATERIA")
        self.lbl_titolo_dettaglio.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.lbl_titolo_dettaglio.setStyleSheet("color: black; margin-top: 10px;")
        layout.addWidget(self.lbl_titolo_dettaglio)

        self.lbl_sottotitolo_corso = QLabel("CORSO DI LAUREA: --")
        self.lbl_sottotitolo_corso.setFont(QFont("Arial", 12))
        self.lbl_sottotitolo_corso.setStyleSheet("color: #555;")
        layout.addWidget(self.lbl_sottotitolo_corso)
        layout.addSpacing(20)

        lbl_mat = QLabel("MATERIALE DIDATTICO CARICATO")
        lbl_mat.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_mat.setStyleSheet("color: black;")
        layout.addWidget(lbl_mat)

        btn_aggiungi = QPushButton("➕ AGGIUNGI FILE")
        btn_aggiungi.setStyleSheet(
            "background-color: #20B2AA; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
        btn_aggiungi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiungi.setFixedWidth(150)
        btn_aggiungi.clicked.connect(self.aggiungi_file_materia)
        layout.addWidget(btn_aggiungi)
        layout.addSpacing(10)

        self.scroll_materiale = QScrollArea()
        self.scroll_materiale.setWidgetResizable(True)
        self.scroll_materiale.setStyleSheet("border: none; background-color: transparent;")
        self.contenitore_lista_file = QWidget()
        self.layout_lista_file = QVBoxLayout(self.contenitore_lista_file)
        self.layout_lista_file.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_materiale.setWidget(self.contenitore_lista_file)
        layout.addWidget(self.scroll_materiale)

        return page

    # --- AZIONI DEL DETTAGLIO CORSO ---

    def apri_creazione_materia(self):
        dialog = DialogNuovaMateria(self.id_utente, self)
        if dialog.exec():
            self.ricarica_pagina_home()

    def apri_creazione_appello(self):
        if not self.corso_corrente_id:
            return
        dialog = DialogCreaAppello(self.corso_corrente_id, self.corso_corrente_nome, self)
        dialog.exec()

    def apri_statistiche_appelli(self):
        if not self.corso_corrente_id:
            return
        dialog = DialogStatisticheAppello(self.corso_corrente_id, self.corso_corrente_nome, self)
        dialog.exec()

    def apri_gestione_tutor(self):
        if not self.corso_corrente_id:
            return
        dialog = DialogGestisciTutor(self.corso_corrente_id, self.corso_corrente_nome, self)
        dialog.exec()

    def apri_dettaglio_corso(self, id_materia, nome_materia):
        self.corso_corrente_id = id_materia
        self.corso_corrente_nome = nome_materia

        info = get_info_materia(id_materia)
        if info and info[0] != "Sconosciuto":
            nome_mat, nome_corso_laurea = info
        else:
            nome_mat = nome_materia
            nome_corso_laurea = "Sconosciuto"

        self.lbl_titolo_dettaglio.setText(f"GESTIONE MATERIA: {nome_mat.upper()}")
        self.lbl_sottotitolo_corso.setText(f"CORSO DI LAUREA: {nome_corso_laurea.upper()}")

        self.ricarica_lista_file()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet(
                "background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")
        self.stacked_widget.setCurrentIndex(3)

    def ricarica_lista_file(self):
        for i in reversed(range(self.layout_lista_file.count())):
            w = self.layout_lista_file.itemAt(i).widget()
            if w:
                self.layout_lista_file.removeWidget(w)
                w.setParent(None)

        materiali = get_materiale_corso(self.corso_corrente_id)
        if not materiali:
            lbl = QLabel("Nessun file caricato per questa materia. Clicca su '➕ AGGIUNGI FILE' per caricarne uno.")
            lbl.setStyleSheet("color: #666; font-size: 14px; font-style: italic;")
            self.layout_lista_file.addWidget(lbl)
        else:
            for mat in materiali:
                riga = QFrame()
                riga.setStyleSheet(
                    "background-color: white; border-radius: 5px; padding: 10px; border: 1px solid #ccc;")
                ly = QHBoxLayout(riga)

                nome_file = os.path.basename(mat['file'])
                lbl_nome = QLabel(f"📄 {nome_file}")
                lbl_nome.setStyleSheet("color: black; border: none; font-size: 14px;")

                btn_elimina = QPushButton("❌ ELIMINA")
                btn_elimina.setStyleSheet(
                    "background-color: #D32F2F; color: white; padding: 6px; border-radius: 4px; font-weight: bold;")
                btn_elimina.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_elimina.setFixedWidth(100)
                btn_elimina.clicked.connect(lambda ch, id_mat=mat['id']: self.elimina_file_materia(id_mat))

                ly.addWidget(lbl_nome)
                ly.addStretch()
                ly.addWidget(btn_elimina)

                self.layout_lista_file.addWidget(riga)

    def aggiungi_file_materia(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Seleziona File", "", "Tutti i file (*)")
        if file_path:
            info = get_info_materia(self.corso_corrente_id)
            if not info or info[0] == "Sconosciuto":
                QMessageBox.warning(self, "Errore", "Impossibile recuperare la cartella del corso.")
                return

            nome_materia, nome_corso = info

            def pulisci_stringa(testo):
                return re.sub(r'\W+', '_', testo.lower()).strip('_')

            cartella_corso = pulisci_stringa(nome_corso)
            cartella_materia = pulisci_stringa(nome_materia)
            nome_file = os.path.basename(file_path)

            base_dir = os.path.dirname(os.path.abspath(__file__))
            path_dir_destinazione = os.path.join(base_dir, "corso", cartella_corso, cartella_materia)

            os.makedirs(path_dir_destinazione, exist_ok=True)
            path_file_destinazione = os.path.join(path_dir_destinazione, nome_file)

            if os.path.exists(path_file_destinazione):
                QMessageBox.warning(self, "Attenzione", f"Il file '{nome_file}' è già presente in questo corso.")
                return

            try:
                shutil.copy2(file_path, path_file_destinazione)
                path_relativo = f"corso/{cartella_corso}/{cartella_materia}/{nome_file}"
                aggiungi_materiale_corso(self.corso_corrente_id, path_relativo)

                QMessageBox.information(self, "Successo", "File caricato correttamente!")
                self.ricarica_lista_file()
            except Exception as e:
                QMessageBox.critical(self, "Errore di Sistema", f"Impossibile caricare il file.\nErrore: {e}")

    def elimina_file_materia(self, id_materiale):
        path_relativo = get_path_materiale(id_materiale)
        if path_relativo:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            path_assoluto = os.path.join(base_dir, path_relativo.replace('/', os.sep))

            if os.path.exists(path_assoluto):
                try:
                    os.remove(path_assoluto)
                except Exception as e:
                    pass

        elimina_materiale_corso(id_materiale)
        self.ricarica_lista_file()