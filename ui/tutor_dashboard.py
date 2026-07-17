import os
import re
import shutil
from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database import (cambia_password, get_materie_tutor, get_info_materia,
                      get_materiale_corso, aggiungi_materiale_corso,
                      get_path_materiale, elimina_materiale_corso,
                      get_professore_by_materia)


# --- CLASSE PERSONALIZZATA PER I QUADRATI DEI CORSI ---
class ClickableFrame(QFrame):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        super().mousePressEvent(event)


class TutorDashboard(QWidget):
    def __init__(self, id_utente, nome, cognome):
        super().__init__()
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.matricola = f"TUT{id_utente}00"
        self.corso_corrente_id = None
        self.corso_corrente_nome = ""

        self.setWindowTitle("Dashboard Tutor - Gestionale UNIVPM")
        self.setMinimumSize(1100, 700)
        self.menu_buttons = {}
        self._inizializza_ui()


    def _inizializza_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # BARRA LATERALE
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background-color: white; border-right: 1px solid #ccc;")
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        lbl_icona = QLabel("🎓")
        lbl_icona.setFont(QFont("Arial", 40))
        lbl_icona.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icona.setStyleSheet("border: none; margin-top: 20px; color: black;")

        lbl_nome = QLabel(f"TUTOR {self.nome.upper()} {self.cognome.upper()}")
        lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nome.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_nome.setStyleSheet("border: none; color: black;")

        lbl_matricola = QLabel(self.matricola)
        lbl_matricola.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_matricola.setStyleSheet("border: none; color: #666; margin-bottom: 20px;")

        sidebar_layout.addWidget(lbl_icona)
        sidebar_layout.addWidget(lbl_nome)
        sidebar_layout.addWidget(lbl_matricola)

        # GESTORE PAGINE
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #E0E0E0;")

        self.pagina_home = self._crea_pagina_home()
        self.pagina_impostazioni = self._crea_pagina_impostazioni()
        self.pagina_dettaglio = self._crea_pagina_dettaglio_corso()

        self.stacked_widget.addWidget(self.pagina_home)  # 0
        self.stacked_widget.addWidget(self.pagina_impostazioni)  # 1
        self.stacked_widget.addWidget(self.pagina_dettaglio)  # 2

        menu_items = [
            ("🏠 CORSI ASSEGNATI", 0),
            ("⚙️ IMPOSTAZIONI", 1)
        ]

        for test, index in menu_items:
            btn = QPushButton(test)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda checked, idx=index, b=btn: self.cambia_pagina(idx, b))
            self.menu_buttons[btn] = test
            sidebar_layout.addWidget(btn)

        self.cambia_pagina(0, list(self.menu_buttons.keys())[0])

        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

    def cambia_pagina(self, index, active_button=None):
        self.stacked_widget.setCurrentIndex(index)
        if index == 0:
            self.ricarica_pagina_home()
        elif index == 1:
            self.ricarica_pagina_impostazioni()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet(
                "background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")

        if active_button:
            active_button.setStyleSheet(
                "background-color: #20B2AA; color: white; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 5px;")

    # ==========================================
    # PAGINA 0: HOME / MATERIE ASSEGNATE
    # ==========================================
    def _crea_pagina_home(self):
        page = QWidget()
        self.layout_home = QVBoxLayout(page)
        self.layout_home.setContentsMargins(30, 30, 30, 30)

        lbl_titolo = QLabel("LE MATERIE DEL MIO CORSO")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: black;")
        self.layout_home.addWidget(lbl_titolo)
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

        materie = get_materie_tutor(self.id_utente)

        if not materie:
            lbl = QLabel("Non sei stato ancora assegnato a nessun Corso di Laurea dai professori.")
            lbl.setStyleSheet("color: black;")
            self.griglia_home.addWidget(lbl, 0, 0)
        else:
            r, c = 0, 0
            for mat in materie:
                card = ClickableFrame()
                card.setFixedSize(260, 160)
                card.setCursor(Qt.CursorShape.PointingHandCursor)
                card.setStyleSheet(
                    "ClickableFrame { background-color: white; border-radius: 5px; padding: 10px; color: black; border: 1px solid #ccc; }")
                card.clicked.connect(
                    lambda id_m=mat['id_materia'], nome_m=mat['nome_materia']: self.apri_dettaglio_corso(id_m, nome_m))

                lo = QVBoxLayout(card)
                testo_html = (
                    f"<span style='color:#0055A4; font-size:11px;'><b>{mat['nome_corso'].upper()}</b></span><br>"
                    f"<hr style='border: 0.5px solid #ccc;'>"
                    f"<b>{mat['nome_materia'].upper()}</b><br><br>"
                    f"<span style='color:green;'>ACCESSO DIDATTICO CONSENTITO</span>"
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
    # PAGINA 2: GESTIONE MATERIALE (DETTAGLIO CORSO)
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

        header_layout.addWidget(btn_indietro)
        header_layout.addStretch()
        layout.addLayout(header_layout)

        self.lbl_titolo_dettaglio = QLabel("GESTIONE MATERIALE")
        self.lbl_titolo_dettaglio.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.lbl_titolo_dettaglio.setStyleSheet("color: black; margin-top: 10px;")
        layout.addWidget(self.lbl_titolo_dettaglio)

        # (Codice esistente...)
        self.lbl_sottotitolo_corso = QLabel("CORSO DI LAUREA: --")
        self.lbl_sottotitolo_corso.setFont(QFont("Arial", 12))
        self.lbl_sottotitolo_corso.setStyleSheet("color: #555;")
        layout.addWidget(self.lbl_sottotitolo_corso)

        # --- INIZIO NUOVO CODICE ---
        self.lbl_professore = QLabel("DOCENTE TITOLARE: --")
        self.lbl_professore.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.lbl_professore.setStyleSheet("color: #0055A4;")  # Un bel blu per farlo risaltare
        layout.addWidget(self.lbl_professore)

        layout.addSpacing(20)  # Lo spazio lo mettiamo qui
        # --- FINE NUOVO CODICE ---


        # (Il resto del codice continua uguale...)


        btn_aggiungi = QPushButton("➕ CARICA NUOVO FILE DIDATTICO")
        btn_aggiungi.setStyleSheet(
            "background-color: #20B2AA; color: white; padding: 12px; font-weight: bold; border-radius: 4px;")
        btn_aggiungi.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiungi.setFixedWidth(250)
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

    def apri_dettaglio_corso(self, id_materia, nome_materia):
        self.corso_corrente_id = id_materia
        self.corso_corrente_nome = nome_materia

        # Info del corso
        info = get_info_materia(id_materia)
        nome_corso_laurea = info[1] if info and info[0] != "Sconosciuto" else "Sconosciuto"

        # Recupera il nome del professore
        nome_professore = get_professore_by_materia(id_materia)

        # Aggiorna tutte le scritte
        self.lbl_titolo_dettaglio.setText(f"GESTIONE MATERIALE: {nome_materia.upper()}")
        self.lbl_sottotitolo_corso.setText(f"CORSO DI LAUREA: {nome_corso_laurea.upper()}")
        self.lbl_professore.setText(f"DOCENTE TITOLARE: {nome_professore.upper()}")

        self.ricarica_lista_file()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet("background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")
        self.stacked_widget.setCurrentIndex(2)

    def ricarica_lista_file(self):
        for i in reversed(range(self.layout_lista_file.count())):
            w = self.layout_lista_file.itemAt(i).widget()
            if w:
                self.layout_lista_file.removeWidget(w)
                w.setParent(None)

        materiali = get_materiale_corso(self.corso_corrente_id)
        if not materiali:
            lbl = QLabel("Nessun file caricato per questa materia. Usa il pulsante in alto per caricarne uno.")
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
            path_dir_destinazione = os.path.join(base_dir, "../corso", cartella_corso, cartella_materia)

            os.makedirs(path_dir_destinazione, exist_ok=True)
            path_file_destinazione = os.path.join(path_dir_destinazione, nome_file)

            if os.path.exists(path_file_destinazione):
                QMessageBox.warning(self, "Attenzione", f"Il file '{nome_file}' è già presente.")
                return

            try:
                shutil.copy2(file_path, path_file_destinazione)
                path_relativo = f"corso/{cartella_corso}/{cartella_materia}/{nome_file}"
                aggiungi_materiale_corso(self.corso_corrente_id, path_relativo)

                QMessageBox.information(self, "Successo", "File didattico caricato correttamente!")
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
                except Exception:
                    pass

        elimina_materiale_corso(id_materiale)
        self.ricarica_lista_file()

    # ==========================================
    # PAGINA 1: IMPOSTAZIONI
    # ==========================================
    def _crea_pagina_impostazioni(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel("IMPOSTAZIONI PROFILO TUTOR")
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

        layout.addLayout(pwd_layout)
        layout.addStretch()

        return page

    def ricarica_pagina_impostazioni(self):
        self.input_pwd_attuale.clear()
        self.input_pwd_nuova.clear()
        self.input_pwd_conferma.clear()

    def azione_cambia_password(self):
        successo, messaggio = cambia_password(self.id_utente, self.input_pwd_attuale.text(),
                                              self.input_pwd_nuova.text())
        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.ricarica_pagina_impostazioni()
        else:
            QMessageBox.critical(self, "Errore", messaggio)

    def esegui_logout(self):
        from ui.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()