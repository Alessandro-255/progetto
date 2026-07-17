import os
import shutil
import sqlite3
from database import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

# --- CLASSE PERSONALIZZATA PER RENDERE CLICCABILI I QUADRATI ---
class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


# ---------------------------------------------------------------

class StudentDashboard(QWidget):
    def __init__(self, id_utente, nome, cognome):
        super().__init__()
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.matricola = get_dati_studente(id_utente)

        # ORA RICHIAMA DIRETTAMENTE LA TUA FUNZIONE
        self.corso_laurea = self.get_corso_laurea()

        self.setWindowTitle("Dashboard Studente - Gestionale UNIVPM")
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

        lbl_nome = QLabel(f"STUD {self.nome.upper()} {self.cognome.upper()}")
        lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nome.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_nome.setStyleSheet("border: none; color: black;")

        lbl_matricola = QLabel(self.matricola)
        lbl_matricola.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_matricola.setStyleSheet("border: none; color: #666;")  # <--- Nota: ho rimosso il margin-bottom qui

        # --- INIZIO NUOVO BLOCCO CORSO ---
        lbl_corso = QLabel(self.corso_laurea.upper())
        lbl_corso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_corso.setFont(QFont("Arial", 8, QFont.Weight.Bold))
        lbl_corso.setStyleSheet("border: none; color: #0055A4; margin-bottom: 20px;")
        lbl_corso.setWordWrap(True)  # Se il nome del corso è lungo, andrà a capo
        # --- FINE NUOVO BLOCCO CORSO ---

        sidebar_layout.addWidget(lbl_icona)
        sidebar_layout.addWidget(lbl_nome)
        sidebar_layout.addWidget(lbl_matricola)
        sidebar_layout.addWidget(lbl_corso)  # <--- NUOVA RIGA: aggiunta dell'etichetta al layout laterale

        # 2. GESTORE PAGINE
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #E0E0E0;")

        self.pagina_home = self._crea_pagina_home()
        self.pagina_corsi = self._crea_pagina_corsi()
        self.pagina_appelli = self._crea_pagina_appelli()
        self.pagina_libretto = self._crea_pagina_libretto()
        self.pagina_impostazioni = self._crea_pagina_impostazioni()
        self.pagina_materiale = self._crea_pagina_materiale()

        self.stacked_widget.addWidget(self.pagina_home)  # 0
        self.stacked_widget.addWidget(self.pagina_corsi)  # 1
        self.stacked_widget.addWidget(self.pagina_appelli)  # 2
        self.stacked_widget.addWidget(self.pagina_libretto)  # 3
        self.stacked_widget.addWidget(self.pagina_impostazioni)  # 4
        self.stacked_widget.addWidget(self.pagina_materiale)  # 5

        menu_items = [
            ("🏠 HOME", 0),
            ("📚 CORSI", 1),
            ("📅 APPELLI D'ESAME", 2),
            ("🎓 LIBRETTO", 3),
            ("⚙️ IMPOSTAZIONI", 4)
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

    def cambia_pagina(self, index, active_button):
        self.stacked_widget.setCurrentIndex(index)

        if index == 0:
            self.ricarica_pagina_home()
        elif index == 1:
            self.ricarica_pagina_corsi()
        elif index == 2:
            self.ricarica_pagina_appelli()
        elif index == 3:
            self.ricarica_pagina_libretto()
        elif index == 4:
            self.ricarica_pagina_impostazioni()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet(
                "background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")

        if active_button:
            active_button.setStyleSheet(
                "background-color: #20B2AA; color: white; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 5px;")

    # ==========================
    # METODI DI SUPPORTO TABELLE
    # ==========================
    def _crea_tabella_base(self, colonne):
        tabella = QTableWidget()
        tabella.setColumnCount(len(colonne))
        tabella.setHorizontalHeaderLabels(colonne)
        tabella.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tabella.setStyleSheet("background-color: white; color: black; gridline-color: #ccc; border: 1px solid #ccc;")
        return tabella

    def _inserisci_testo_cella(self, tabella, riga, colonna, testo):
        item = QTableWidgetItem(str(testo))
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        item.setFlags(Qt.ItemFlag.ItemIsEnabled)
        tabella.setItem(riga, colonna, item)

    # ==========================
    # PAGINA 0: HOME
    # ==========================
    def _crea_pagina_home(self):
        page = QWidget()
        self.layout_home = QVBoxLayout(page)
        self.layout_home.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("I MIEI CORSI ATTIVI (Clicca per il materiale)")
        lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black;")
        self.layout_home.addWidget(lbl)
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
        corsi = get_corsi_studente(self.id_utente)
        if not corsi:
            lbl = QLabel("Non hai corsi in sospeso. Ottimo lavoro!")
            lbl.setStyleSheet("color: black;")
            self.griglia_home.addWidget(lbl, 0, 0)
        else:
            r, c = 0, 0
            for corso in corsi:
                card = ClickableFrame()
                card.setFixedSize(250, 200)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px; color: black;")

                card.clicked.connect(
                    lambda id_m=corso['id_materia'], nome_m=corso['nome_materia']: self.apri_pagina_materiale(id_m,
                                                                                                              nome_m))

                lo = QVBoxLayout(card)
                lo.addWidget(QLabel(
                    f"<b>{corso['nome_materia'].upper()}</b><br><br>CFU: {corso['cfu']}<br><span style='color:green;'>IN CORSO</span>"))
                self.griglia_home.addWidget(card, r, c)
                c += 1
                if c >= 3:
                    c = 0;
                    r += 1

    # ==========================
    # PAGINA 5: MATERIALE
    # ==========================
    def _crea_pagina_materiale(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        btn_indietro = QPushButton("⬅ TORNA ALLA HOME")
        btn_indietro.setStyleSheet(
            "background-color: transparent; color: #0055A4; font-weight: bold; font-size: 14px; text-align: left; padding: 0px;")
        btn_indietro.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_indietro.setFixedWidth(200)
        btn_indietro.clicked.connect(self.torna_alla_home)

        header_layout.addWidget(btn_indietro)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.lbl_titolo_materiale = QLabel("MATERIALE DEL CORSO")
        self.lbl_titolo_materiale.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.lbl_titolo_materiale.setStyleSheet("color: black; margin-top: 15px;")
        layout.addWidget(self.lbl_titolo_materiale)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none; background-color: transparent;")
        self.contenitore_materiale = QWidget()
        self.layout_lista_materiale = QVBoxLayout(self.contenitore_materiale)
        self.layout_lista_materiale.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(self.contenitore_materiale)

        layout.addWidget(scroll)
        return page

    def apri_pagina_materiale(self, id_materia, nome_materia):
        self.lbl_titolo_materiale.setText(f"MATERIALE DEL CORSO: {nome_materia.upper()}")

        for i in reversed(range(self.layout_lista_materiale.count())):
            w = self.layout_lista_materiale.itemAt(i).widget()
            if w:
                self.layout_lista_materiale.removeWidget(w)
                w.setParent(None)

        materiali = get_materiale_corso(id_materia)

        if not materiali:
            lbl = QLabel("Non c'è ancora nessun materiale caricato dal professore per questo corso.")
            lbl.setStyleSheet("color: #666; font-size: 14px;")
            self.layout_lista_materiale.addWidget(lbl)
        else:
            for mat in materiali:
                riga_file = QFrame()
                riga_file.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
                ly = QHBoxLayout(riga_file)

                nome_file_pulito = os.path.basename(mat['file'])
                lbl_nome = QLabel(f"📄 {nome_file_pulito}")
                lbl_nome.setStyleSheet("color: black; font-size: 14px;")

                btn_scarica = QPushButton("SCARICA")
                btn_scarica.setStyleSheet(
                    "background-color: #20B2AA; color: white; padding: 8px; font-weight: bold; border-radius: 4px;")
                btn_scarica.setCursor(Qt.CursorShape.PointingHandCursor)
                btn_scarica.setFixedWidth(100)

                btn_scarica.clicked.connect(lambda ch, f_path=mat['file']: self.esegui_download_reale(f_path))

                ly.addWidget(lbl_nome)
                ly.addStretch()
                ly.addWidget(btn_scarica)

                self.layout_lista_materiale.addWidget(riga_file)

        self.stacked_widget.setCurrentIndex(5)

    def esegui_download_reale(self, path_relativo_db):
        base_dir = os.path.dirname(os.path.abspath(__file__))

        # FIX: Aggiunto ".." per uscire dalla cartella 'ui' e andare nella root del progetto
        percorso_sorgente = os.path.join(base_dir, "..", path_relativo_db)

        # Opzionale ma consigliato: normalizza il path per uniformare gli slash (\ e /) su Windows
        percorso_sorgente = os.path.normpath(percorso_sorgente)

        if not os.path.exists(percorso_sorgente):
            QMessageBox.critical(self, "Errore di Sistema",
                                 f"Il file non è stato trovato sul server dell'università:\n{percorso_sorgente}")
            return

        nome_file = os.path.basename(path_relativo_db)

        percorso_salvataggio, _ = QFileDialog.getSaveFileName(
            self,
            "Scarica Materiale",
            nome_file,
            "PDF Files (*.pdf);;Tutti i file (*)"
        )

        if percorso_salvataggio:
            try:
                shutil.copy2(percorso_sorgente, percorso_salvataggio)
                QMessageBox.information(self, "Download Completato",
                                        f"Il file {nome_file} è stato salvato con successo!")
            except Exception as errore:
                QMessageBox.critical(self, "Errore", f"Impossibile salvare il file:\n{str(errore)}")

    def torna_alla_home(self):
        for btn, testo in self.menu_buttons.items():
            if "HOME" in testo:
                self.cambia_pagina(0, btn)
                break

    # ==========================
    # PAGINA 1: CORSI
    # ==========================
    def _crea_pagina_corsi(self):
        page = QWidget()
        self.layout_corsi = QVBoxLayout(page)
        self.layout_corsi.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("ISCRIVITI A NUOVI CORSI")
        lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black;")
        self.layout_corsi.addWidget(lbl)
        self.scroll_corsi = QScrollArea()
        self.scroll_corsi.setWidgetResizable(True)
        self.scroll_corsi.setStyleSheet("border: none; background-color: transparent;")
        self.contenitore_card_corsi = QWidget()
        self.griglia_corsi = QGridLayout(self.contenitore_card_corsi)
        self.griglia_corsi.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_corsi.setWidget(self.contenitore_card_corsi)
        self.layout_corsi.addWidget(self.scroll_corsi)
        return page

    def ricarica_pagina_corsi(self):
        for i in reversed(range(self.griglia_corsi.count())):
            w = self.griglia_corsi.itemAt(i).widget()
            self.griglia_corsi.removeWidget(w)
            w.setParent(None)
        materie = get_materie_disponibili(self.id_utente)
        if not materie:
            lbl = QLabel("Sei già iscritto a tutti i corsi!")
            lbl.setStyleSheet("color: black;")
            self.griglia_corsi.addWidget(lbl, 0, 0)
        else:
            r, c = 0, 0
            for materia in materie:
                card = QFrame()
                card.setFixedSize(250, 200)
                card.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px; color: black;")
                lo = QVBoxLayout(card)
                lo.addWidget(QLabel(f"<b>{materia['nome_materia'].upper()}</b><br>CFU: {materia['cfu']}"))
                btn = QPushButton("ISCRIVITI")
                btn.setStyleSheet("background-color: #20B2AA; color: white; padding: 5px;")
                btn.clicked.connect(lambda ch, id_m=materia['id_materia']: self.iscriviti_azione(id_m))
                lo.addWidget(btn)
                self.griglia_corsi.addWidget(card, r, c)
                c += 1
                if c >= 3:
                    c = 0;
                    r += 1

    def iscriviti_azione(self, id_materia):
        if iscrivi_studente_materia(self.id_utente, id_materia):
            QMessageBox.information(self, "Successo", "Iscrizione avvenuta!")
            self.ricarica_pagina_corsi()

    # ==========================
    # PAGINA 2: APPELLI
    # ==========================
    def _crea_pagina_appelli(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("APPELLI D'ESAME DISPONIBILI E PRENOTATI")
        lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black;")
        layout.addWidget(lbl)
        layout.addWidget(QLabel("<br><b>APPELLI DA PRENOTARE:</b>"))
        self.tabella_disp = self._crea_tabella_base(["MATERIA", "GRUPPO", "DATA", "ORA", "AZIONI"])
        layout.addWidget(self.tabella_disp)
        layout.addWidget(QLabel("<br><b>LE MIE PRENOTAZIONI:</b>"))
        self.tabella_pren = self._crea_tabella_base(["MATERIA", "DATA", "ORA"])
        layout.addWidget(self.tabella_pren)
        return page

    def ricarica_pagina_appelli(self):
        disp, pren = get_appelli_per_studente(self.id_utente)
        self.tabella_disp.setRowCount(len(disp))
        for riga, app in enumerate(disp):
            self._inserisci_testo_cella(self.tabella_disp, riga, 0, app['materia'])
            self._inserisci_testo_cella(self.tabella_disp, riga, 1, app['gruppo'])
            self._inserisci_testo_cella(self.tabella_disp, riga, 2, app['data'])
            self._inserisci_testo_cella(self.tabella_disp, riga, 3, app['ora'])
            btn_prenota = QPushButton("PRENOTA")
            btn_prenota.setStyleSheet("background-color: #20B2AA; color: white;")
            btn_prenota.clicked.connect(lambda ch, a_id=app['id_appello']: self._azione_prenota(a_id))
            self.tabella_disp.setCellWidget(riga, 4, btn_prenota)
        self.tabella_pren.setRowCount(len(pren))
        for riga, app in enumerate(pren):
            self._inserisci_testo_cella(self.tabella_pren, riga, 0, app['materia'])
            self._inserisci_testo_cella(self.tabella_pren, riga, 1, app['data'])
            self._inserisci_testo_cella(self.tabella_pren, riga, 2, app['ora'])

    def _azione_prenota(self, id_appello):
        if prenota_appello_studente(self.id_utente, id_appello):
            QMessageBox.information(self, "Successo", "Ti sei prenotato all'appello!")
            self.ricarica_pagina_appelli()

    # ==========================
    # PAGINA 3: LIBRETTO
    # ==========================
    def _crea_pagina_libretto(self):
        page = QWidget()
        self.layout_libretto = QVBoxLayout(page)
        self.layout_libretto.setContentsMargins(30, 30, 30, 30)
        lbl = QLabel("LIBRETTO DIGITALE E STATISTICHE")
        lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: black;")
        self.layout_libretto.addWidget(lbl)
        stats_layout = QHBoxLayout()
        self.lbl_media_arit = QLabel("MEDIA ARITMETICA:\n--")
        self.lbl_media_arit.setStyleSheet(
            "background-color: white; color: black; padding: 15px; border-radius: 5px; font-weight: bold;")
        self.lbl_media_arit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_media_pond = QLabel("MEDIA PONDERATA:\n--")
        self.lbl_media_pond.setStyleSheet(
            "background-color: white; color: black; padding: 15px; border-radius: 5px; font-weight: bold;")
        self.lbl_media_pond.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_cfu = QFrame()
        box_cfu.setStyleSheet("background-color: white; color: black; padding: 10px; border-radius: 5px;")
        box_cfu_layout = QVBoxLayout(box_cfu)
        self.lbl_cfu_text = QLabel("CFU Totali Acquisiti: 0 / 180")
        self.lbl_cfu_text.setStyleSheet("border: none; font-weight: bold;")
        self.progress_cfu = QProgressBar()
        self.progress_cfu.setMaximum(180)
        self.progress_cfu.setValue(0)
        self.progress_cfu.setStyleSheet(
            "QProgressBar { border: 1px solid #ccc; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #20B2AA; }")
        box_cfu_layout.addWidget(self.lbl_cfu_text)
        box_cfu_layout.addWidget(self.progress_cfu)
        stats_layout.addWidget(self.lbl_media_arit)
        stats_layout.addWidget(self.lbl_media_pond)
        stats_layout.addWidget(box_cfu)
        self.layout_libretto.addLayout(stats_layout)
        self.layout_libretto.addWidget(QLabel("<br><b>VOTI IN SOSPESO (Da Verbalizzare):</b>"))
        self.tabella_sospesi = self._crea_tabella_base(["MATERIA", "VOTO PROPOSTO", "AZIONI"])
        self.layout_libretto.addWidget(self.tabella_sospesi)
        self.layout_libretto.addWidget(QLabel("<br><b>REGISTRO ESAMI SUPERATI:</b>"))
        self.tabella_superati = self._crea_tabella_base(["MATERIA", "VOTO", "CFU", "GRUPPO", "VERBALIZZATO"])
        self.layout_libretto.addWidget(self.tabella_superati)
        return page

    def ricarica_pagina_libretto(self):
        # 1. Svuotiamo forzatamente le tabelle per garantire un refresh grafico pulito
        self.tabella_sospesi.clearContents()
        self.tabella_sospesi.setRowCount(0)
        self.tabella_superati.clearContents()
        self.tabella_superati.setRowCount(0)

        sospesi, superati = get_dati_libretto(self.id_utente)

        tot_voti = 0
        somma_voti_cfu = 0
        tot_cfu = 0

        # 2. Calcolo Statistiche Aggiornato
        for esame in superati:
            voto = esame['voto']
            cfu = esame['cfu']

            # Se il voto è 31 (30L), ai fini del calcolo della media matematica vale 30
            voto_calcolo = 30 if voto > 30 else voto

            tot_voti += voto_calcolo
            somma_voti_cfu += (voto_calcolo * cfu)
            tot_cfu += cfu

        media_arit = (tot_voti / len(superati)) if superati else 0
        media_pond = (somma_voti_cfu / tot_cfu) if tot_cfu > 0 else 0

        self.lbl_media_arit.setText(f"MEDIA ARITMETICA:\n{media_arit:.2f}")
        self.lbl_media_pond.setText(f"MEDIA PONDERATA:\n{media_pond:.2f}")
        self.lbl_cfu_text.setText(f"CFU Totali Acquisiti: {tot_cfu} / 180")
        self.progress_cfu.setValue(tot_cfu)

        # 3. Popolamento Tabella Voti In Sospeso
        self.tabella_sospesi.setRowCount(len(sospesi))
        for riga, v in enumerate(sospesi):
            self._inserisci_testo_cella(self.tabella_sospesi, riga, 0, v['materia'])

            # Mostra 30L se il professore ha inserito la lode
            voto_display = "30L" if v['voto'] > 30 else str(v['voto'])
            self._inserisci_testo_cella(self.tabella_sospesi, riga, 1, voto_display)

            box_azioni = QWidget()
            box_azioni_layout = QHBoxLayout(box_azioni)
            box_azioni_layout.setContentsMargins(0, 0, 0, 0)

            btn_accetta = QPushButton("✔️ ACCETTA")
            btn_accetta.setStyleSheet("background-color: green; color: white; font-weight: bold;")
            btn_accetta.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_accetta.clicked.connect(lambda ch, id_v=v['id_sospeso']: self._azione_verbalizza(id_v, True))

            btn_rifiuta = QPushButton("❌ RIFIUTA")
            btn_rifiuta.setStyleSheet("background-color: red; color: white; font-weight: bold;")
            btn_rifiuta.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_rifiuta.clicked.connect(lambda ch, id_v=v['id_sospeso']: self._azione_verbalizza(id_v, False))

            box_azioni_layout.addWidget(btn_accetta)
            box_azioni_layout.addWidget(btn_rifiuta)
            self.tabella_sospesi.setCellWidget(riga, 2, box_azioni)

        # 4. Popolamento Tabella Esami Superati (Testo definitivo)
        self.tabella_superati.setRowCount(len(superati))
        for riga, esame in enumerate(superati):
            self._inserisci_testo_cella(self.tabella_superati, riga, 0, esame['materia'])

            voto_str = "30L" if esame['voto'] > 30 else str(esame['voto'])
            self._inserisci_testo_cella(self.tabella_superati, riga, 1, voto_str)
            self._inserisci_testo_cella(self.tabella_superati, riga, 2, str(esame['cfu']))
            self._inserisci_testo_cella(self.tabella_superati, riga, 3, esame['gruppo'])
            self._inserisci_testo_cella(self.tabella_superati, riga, 4, "SI")

    def get_corso_laurea(self):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query = """
                    SELECT c.Nome
                    FROM Corso_Studente cs
                             JOIN Corso c ON cs.COD_CORSO = c.ID_CORSO
                    WHERE cs.COD_STUDENTE = ? \
                    """
            cur.execute(query, (self.id_utente,))
            res = cur.fetchall()
            if res:
                # Se è iscritto a più corsi li unisce con " / ", altrimenti stampa l'unico trovato
                return " / ".join([r[0] for r in res])
            return "Nessun Corso Assegnato"

    def _azione_accetta_libretto(self):
        QMessageBox.information(self, "Info",
                                "Questo esame è già stato confermato ed è presente nel tuo libretto definitivo.")

    def _azione_rifiuta_libretto(self, id_libretto):
        risposta = QMessageBox.question(self, "Conferma Rifiuto",
                                        "Sei sicuro di voler rifiutare ed eliminare questo voto dal libretto?\nL'azione è irreversibile.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if risposta == QMessageBox.StandardButton.Yes:
            if rifiuta_voto_libretto(id_libretto):
                QMessageBox.information(self, "Successo", "Il voto è stato rifiutato ed eliminato dal libretto.")
                self.ricarica_pagina_libretto()
                self.ricarica_pagina_home()
            else:
                QMessageBox.critical(self, "Errore", "Si è verificato un problema nella rimozione del voto.")

    def _azione_verbalizza(self, id_sospeso, accetta):
        azione = "accettare" if accetta else "rifiutare"
        risposta = QMessageBox.question(self, "Conferma Scelta",
                                        f"Sei sicuro di voler {azione} questo voto?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if risposta == QMessageBox.StandardButton.Yes:
            if gestisci_verbalizzazione(id_sospeso, accetta):
                azione_passata = "accettato e registrato" if accetta else "rifiutato"
                QMessageBox.information(self, "Esito", f"Hai {azione_passata} il voto con successo!")

                # Ricarica immediatamente la pagina per forzare l'aggiornamento visivo di entrambe le tabelle
                self.ricarica_pagina_libretto()
                self.ricarica_pagina_home()
    # ==========================
    # PAGINA 4: IMPOSTAZIONI
    # ==========================
    def _crea_pagina_impostazioni(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel("IMPOSTAZIONI GESTIONE PROFILO E APPLICAZIONE")
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
        btn_salva_pwd.clicked.connect(self.azione_cambia_password)

        pwd_layout.addWidget(self.input_pwd_attuale)
        pwd_layout.addWidget(self.input_pwd_nuova)
        pwd_layout.addWidget(self.input_pwd_conferma)
        pwd_layout.addWidget(btn_salva_pwd)

        dsa_layout = QVBoxLayout()
        dsa_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        lbl_dsa = QLabel("DSA")
        lbl_dsa.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        lbl_dsa.setStyleSheet("color: black; margin-bottom: 10px;")
        dsa_layout.addWidget(lbl_dsa)

        self.combo_dsa = QComboBox()
        self.combo_dsa.addItems(["-- Seleziona --", "SI", "NO"])
        self.combo_dsa.setStyleSheet("background-color: white; color: black; padding: 10px;")

        self.btn_salva_dsa = QPushButton("CONFERMA DSA")
        self.btn_salva_dsa.setStyleSheet("background-color: #20B2AA; color: white; padding: 10px; font-weight: bold;")
        self.btn_salva_dsa.clicked.connect(self.azione_salva_dsa)

        dsa_layout.addWidget(self.combo_dsa)
        dsa_layout.addWidget(self.btn_salva_dsa)

        body_layout.addLayout(pwd_layout)
        body_layout.addSpacing(50)
        body_layout.addLayout(dsa_layout)
        body_layout.addStretch()

        layout.addLayout(body_layout)
        layout.addStretch()

        return page

    def ricarica_pagina_impostazioni(self):
        self.input_pwd_attuale.clear()
        self.input_pwd_nuova.clear()
        self.input_pwd_conferma.clear()
        stato_dsa = get_stato_dsa(self.id_utente)

        if stato_dsa is not None:
            indice = 1 if stato_dsa == 1 else 2
            self.combo_dsa.setCurrentIndex(indice)
            self.combo_dsa.setEnabled(False)
            self.btn_salva_dsa.setEnabled(False)
            self.btn_salva_dsa.setText("GIÀ DICHIARATO")
            self.btn_salva_dsa.setStyleSheet(
                "background-color: #A9A9A9; color: white; padding: 10px; font-weight: bold;")
        else:
            self.combo_dsa.setCurrentIndex(0)
            self.combo_dsa.setEnabled(True)
            self.btn_salva_dsa.setEnabled(True)
            self.btn_salva_dsa.setText("CONFERMA DSA")
            self.btn_salva_dsa.setStyleSheet(
                "background-color: #20B2AA; color: white; padding: 10px; font-weight: bold;")

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

    def azione_salva_dsa(self):
        scelta = self.combo_dsa.currentText()
        if scelta == "-- Seleziona --":
            QMessageBox.warning(self, "Attenzione", "Seleziona un'opzione valida per il DSA.")
            return
        risposta = QMessageBox.question(self, "Conferma Irreversibile",
                                        "Sei sicuro? Questa scelta non potrà più essere modificata.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if risposta == QMessageBox.StandardButton.Yes:
            stato = 1 if scelta == "SI" else 0
            if set_stato_dsa(self.id_utente, stato):
                QMessageBox.information(self, "Successo", "Stato DSA aggiornato correttamente.")
                self.ricarica_pagina_impostazioni()
            else:
                QMessageBox.critical(self, "Errore", "Si è verificato un errore nel salvataggio.")

    def esegui_logout(self):
        from ui.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()