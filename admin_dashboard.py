import os
import sqlite3
from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QScrollArea, QGridLayout, QFrame,
                             QStackedWidget, QMessageBox, QDialog, QFormLayout,
                             QComboBox, QLineEdit, QTabWidget)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from database import DB_PATH, cambia_password


class AdminDashboard(QWidget):
    def __init__(self, id_utente, nome, cognome):
        super().__init__()
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.setWindowTitle("Dashboard Admin - Gestionale UNIVPM")
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

        lbl_icona = QLabel("🛡️")
        lbl_icona.setFont(QFont("Arial", 40))
        lbl_icona.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icona.setStyleSheet("border: none; margin-top: 20px; color: black;")

        lbl_nome = QLabel(f"ADMIN {self.nome.upper()}")
        lbl_nome.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_nome.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        lbl_nome.setStyleSheet("border: none; color: black;")

        lbl_ruolo = QLabel("Segreteria / ESSE3")
        lbl_ruolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_ruolo.setStyleSheet("border: none; color: #666; margin-bottom: 20px;")

        sidebar_layout.addWidget(lbl_icona)
        sidebar_layout.addWidget(lbl_nome)
        sidebar_layout.addWidget(lbl_ruolo)

        # 2. GESTORE PAGINE
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setStyleSheet("background-color: #E0E0E0;")

        self.pagina_gestione_utenti = self._crea_pagina_gestione_utenti()  # Indice 0
        self.pagina_impostazioni = self._crea_pagina_impostazioni()  # Indice 1

        self.stacked_widget.addWidget(self.pagina_gestione_utenti)
        self.stacked_widget.addWidget(self.pagina_impostazioni)

        menu_items = [
            ("👥 GESTIONE UTENTI", 0),
            ("⚙️ IMPOSTAZIONI", 1)
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
            self.ricarica_dati_admin()

        for btn in self.menu_buttons.keys():
            btn.setStyleSheet(
                "background-color: transparent; color: black; text-align: left; padding: 15px; border: none; font-weight: normal;")
        if active_button:
            active_button.setStyleSheet(
                "background-color: #20B2AA; color: white; text-align: left; padding: 15px; border: none; font-weight: bold; border-radius: 5px;")

    # ==========================================
    # PAGINA 0: GESTIONE UTENTI (CREAZIONE E MODIFICA)
    # ==========================================
    def _crea_pagina_gestione_utenti(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        lbl_titolo = QLabel("PANNELLO ADMIN - POPOLAMENTO E GESTIONE ANAGRAFICA")
        lbl_titolo.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        lbl_titolo.setStyleSheet("color: black;")
        layout.addWidget(lbl_titolo)
        layout.addSpacing(10)

        tabs = QTabWidget()
        tabs.setStyleSheet("background-color: white; color: black;")

        tabs.addTab(self._tab_crea_utente(), "➕ Crea Nuovo Utente")
        tabs.addTab(self._tab_modifica_professore(), "✏️ Modifica Professore")

        layout.addWidget(tabs)
        return page

    def _tab_crea_utente(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()

        self.input_ruolo = QComboBox()
        self.input_ruolo.addItems(["Studente", "Professore", "Tutor"])
        self.input_ruolo.currentIndexChanged.connect(self._aggiorna_campi_creazione)

        self.input_nome = QLineEdit()
        self.input_cognome = QLineEdit()
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("nome.cognome@uni.it")
        self.input_cf = QLineEdit()
        self.input_cf.setPlaceholderText("Codice Fiscale 16 caratteri")
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_matricola = QLineEdit()
        self.input_matricola.setPlaceholderText("Es: MAT10003, DOC103 o TUT01")

        # Campo specifico per Professore e Tutor (Corso di Laurea)
        self.lbl_corso_associato = QLabel("Corso di Laurea:")
        self.combo_corso_associato = QComboBox()

        form.addRow("Ruolo Utente:", self.input_ruolo)
        form.addRow("Nome:", self.input_nome)
        form.addRow("Cognome:", self.input_cognome)
        form.addRow("Email:", self.input_email)
        form.addRow("Codice Fiscale:", self.input_cf)
        form.addRow("Password Temporanea:", self.input_password)
        form.addRow("Matricola / ID:", self.input_matricola)
        form.addRow(self.lbl_corso_associato, self.combo_corso_associato)

        layout.addLayout(form)
        layout.addSpacing(20)

        btn_crea = QPushButton("REGISTRA UTENTE NEL SISTEMA")
        btn_crea.setStyleSheet(
            "background-color: #0055A4; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
        btn_crea.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_crea.clicked.connect(self.salva_nuovo_utente)
        layout.addWidget(btn_crea)

        layout.addStretch()
        self._aggiorna_campi_creazione()
        return widget

    def _aggiorna_campi_creazione(self):
        ruolo = self.input_ruolo.currentText()
        if ruolo in ["Professore", "Tutor"]:
            self.lbl_corso_associato.show()
            self.combo_corso_associato.show()
        else:
            self.lbl_corso_associato.hide()
            self.combo_corso_associato.hide()

    def ricarica_dati_admin(self):
        """Carica in modo sicuro i dati dal DB quando la pagina viene aperta"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()

            # Carica corsi per la combo professori/tutor
            self.combo_corso_associato.blockSignals(True)
            self.combo_corso_associato.clear()
            cur.execute("SELECT ID_CORSO, Nome FROM Corso")
            for r in cur.fetchall():
                self.combo_corso_associato.addItem(r[1], r[0])
            self.combo_corso_associato.blockSignals(False)

            # Carica professori per la combo modifica
            self.combo_professori.blockSignals(True)
            self.combo_professori.clear()
            cur.execute(
                "SELECT p.ID_PROF, u.Nome, u.Cognome FROM Professore p JOIN Utente u ON p.ID_PROF = u.ID_UTENTE")
            for r in cur.fetchall():
                self.combo_professori.addItem(f"Prof. {r[1]} {r[2]} (ID: {r[0]})", r[0])
            self.combo_professori.blockSignals(False)

            conn.close()
            self._carica_dati_professore()
        except Exception as e:
            print(f"Errore caricamento dati admin: {e}")

    def salva_nuovo_utente(self):
        ruolo = self.input_ruolo.currentText()
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        cf = self.input_cf.text().strip().upper()
        password = self.input_password.text().strip()
        matricola = self.input_matricola.text().strip()

        if not nome or not cognome or not email or not cf or not password or not matricola:
            QMessageBox.warning(self, "Attenzione", "Tutti i campi anagrafici sono obbligatori.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO Utente (Nome, Cognome, Data_Nascita, COD_FISCALE, Email, Password) VALUES (?, ?, '2000-01-01', ?, ?, ?)",
                (nome, cognome, cf, email, password)
            )
            id_utente = cur.lastrowid

            if ruolo == "Studente":
                cur.execute("INSERT INTO Studente (ID_STUDENTE, Matricola) VALUES (?, ?)", (id_utente, matricola))
            elif ruolo == "Professore":
                cur.execute("INSERT INTO Professore (ID_PROF) VALUES (?)", (id_utente,))
                id_corso = self.combo_corso_associato.currentData()
                if id_corso:
                    cur.execute("INSERT INTO Corso_Professore (COD_PROFESSORE, COD_CORSO) VALUES (?, ?)",
                                (id_utente, id_corso))
            elif ruolo == "Tutor":
                cur.execute("INSERT INTO Tutor (ID_TUTOR) VALUES (?)", (id_utente,))
                id_corso = self.combo_corso_associato.currentData()
                if id_corso:
                    cur.execute("INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) VALUES (?, ?)", (id_utente, id_corso))

            conn.commit()
            QMessageBox.information(self, "Successo", f"{ruolo} {nome} {cognome} creato e associato con successo!")
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_cf.clear()
            self.input_password.clear()
            self.input_matricola.clear()
            self.ricarica_dati_admin()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Errore Database", f"Impossibile registrare l'utente:\n{e}")
        finally:
            conn.close()

    # ==========================================
    # TAB 2: MODIFICA INFORMAZIONI PROFESSORE
    # ==========================================
    def _tab_modifica_professore(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()

        self.combo_professori = QComboBox()
        self.combo_professori.currentIndexChanged.connect(self._carica_dati_professore)

        self.edit_prof_nome = QLineEdit()
        self.edit_prof_cognome = QLineEdit()
        self.edit_prof_email = QLineEdit()

        form.addRow("Seleziona Professore:", self.combo_professori)
        form.addRow("Nome:", self.edit_prof_nome)
        form.addRow("Cognome:", self.edit_prof_cognome)
        form.addRow("Email:", self.edit_prof_email)

        layout.addLayout(form)
        layout.addSpacing(20)

        lbl_info = QLabel(
            "<i>Nota: Un professore gestisce più corsi e materie direttamente dalla sua dashboard personale. Da qui puoi aggiornare le sue credenziali anagrafiche.</i>")
        lbl_info.setStyleSheet("color: #666;")
        layout.addWidget(lbl_info)
        layout.addSpacing(15)

        btn_aggiorna = QPushButton("SALVA MODIFICHE PROFESSORE")
        btn_aggiorna.setStyleSheet(
            "background-color: #20B2AA; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
        btn_aggiorna.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiorna.clicked.connect(self.salva_modifiche_professore)
        layout.addWidget(btn_aggiorna)

        layout.addStretch()
        return widget

    def _carica_dati_professore(self):
        id_prof = self.combo_professori.currentData()
        if not id_prof:
            self.edit_prof_nome.clear()
            self.edit_prof_cognome.clear()
            self.edit_prof_email.clear()
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT Nome, Cognome, Email FROM Utente WHERE ID_UTENTE = ?", (id_prof,))
        res = cur.fetchone()
        conn.close()

        if res:
            self.edit_prof_nome.setText(res[0])
            self.edit_prof_cognome.setText(res[1])
            self.edit_prof_email.setText(res[2])

    def salva_modifiche_professore(self):
        id_prof = self.combo_professori.currentData()
        if not id_prof:
            QMessageBox.warning(self, "Attenzione", "Seleziona un professore valido.")
            return

        nome = self.edit_prof_nome.text().strip()
        cognome = self.edit_prof_cognome.text().strip()
        email = self.edit_prof_email.text().strip()

        if not nome or not cognome or not email:
            QMessageBox.warning(self, "Attenzione", "Compila tutti i campi.")
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        try:
            cur.execute("UPDATE Utente SET Nome = ?, Cognome = ?, Email = ? WHERE ID_UTENTE = ?",
                        (nome, cognome, email, id_prof))
            conn.commit()
            QMessageBox.information(self, "Successo", "Informazioni del professore aggiornate correttamente!")
            self.ricarica_dati_admin()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Errore DB", f"Impossibile aggiornare:\n{e}")
        finally:
            conn.close()

    # ==========================================
    # PAGINA 1: IMPOSTAZIONI (CAMBIO PASSWORD / LOGOUT)
    # ==========================================
    def _crea_pagina_impostazioni(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(30, 30, 30, 30)

        header_layout = QHBoxLayout()
        lbl_titolo = QLabel("IMPOSTAZIONI ADMIN")
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

        lbl_pwd = QLabel("CAMBIO PASSWORD AMMINISTRATORE")
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