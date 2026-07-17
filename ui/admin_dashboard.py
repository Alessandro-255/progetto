from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel,
                             QPushButton, QFrame,
                             QStackedWidget, QMessageBox, QFormLayout,
                             QComboBox, QLineEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# Importiamo direttamente la nostra classe orientata agli oggetti!
from database.admin import Admin


class AdminDashboard(QWidget):
    def __init__(self, id_utente, nome, cognome):
        super().__init__()
        # Inizializziamo l'oggetto Admin che si occuperà di tutto il DB
        self.admin = Admin(id_utente, nome, cognome)

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

        lbl_nome = QLabel(f"ADMIN {self.admin.nome.upper()}")
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

        self.pagina_gestione_utenti = self._crea_pagina_gestione_utenti()
        self.pagina_impostazioni = self._crea_pagina_impostazioni()

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
    # PAGINA 0: GESTIONE UTENTI E ASSEGNAZIONI (CRUD)
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
        tabs.addTab(self._tab_modifica_elimina(), "✏️ Modifica/Elimina Utente")
        tabs.addTab(self._tab_assegnazioni(), "🔗 Assegnazioni Corsi")

        layout.addWidget(tabs)
        return page

    # --- TAB 1: CREATE ---
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

        self.lbl_corso_associato = QLabel("Assegnazione Iniziale Corso:")
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
        btn_crea.setStyleSheet("background-color: #0055A4; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
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

    def salva_nuovo_utente(self):
        ruolo = self.input_ruolo.currentText()
        nome = self.input_nome.text().strip()
        cognome = self.input_cognome.text().strip()
        email = self.input_email.text().strip()
        cf = self.input_cf.text().strip().upper()
        password = self.input_password.text().strip()
        matricola = self.input_matricola.text().strip()
        id_corso = self.combo_corso_associato.currentData()

        if not nome or not cognome or not email or not cf or not password or not matricola:
            QMessageBox.warning(self, "Attenzione", "Tutti i campi anagrafici sono obbligatori.")
            return

        # Deleghiamo la creazione all'oggetto Admin!
        successo, msg = self.admin.salva_nuovo_utente(ruolo, nome, cognome, email, cf, password, matricola, id_corso)

        if successo:
            QMessageBox.information(self, "Successo", msg)
            self.input_nome.clear()
            self.input_cognome.clear()
            self.input_email.clear()
            self.input_cf.clear()
            self.input_password.clear()
            self.input_matricola.clear()
            self.ricarica_dati_admin()
        else:
            QMessageBox.critical(self, "Errore", msg)

    # --- TAB 2: UPDATE & DELETE ---
    def _tab_modifica_elimina(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        form = QFormLayout()
        self.combo_utenti_modifica = QComboBox()
        self.combo_utenti_modifica.currentIndexChanged.connect(self._carica_dati_modifica)

        self.edit_utente_nome = QLineEdit()
        self.edit_utente_cognome = QLineEdit()
        self.edit_utente_email = QLineEdit()

        form.addRow("Seleziona Utente:", self.combo_utenti_modifica)
        form.addRow("Nome:", self.edit_utente_nome)
        form.addRow("Cognome:", self.edit_utente_cognome)
        form.addRow("Email:", self.edit_utente_email)

        layout.addLayout(form)
        layout.addSpacing(20)

        btn_layout = QHBoxLayout()

        btn_elimina = QPushButton("🗑️ ELIMINA UTENTE")
        btn_elimina.setStyleSheet("background-color: #D32F2F; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
        btn_elimina.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_elimina.clicked.connect(self.elimina_utente)

        btn_aggiorna = QPushButton("💾 SALVA MODIFICHE")
        btn_aggiorna.setStyleSheet("background-color: #20B2AA; color: white; font-weight: bold; padding: 12px; border-radius: 4px;")
        btn_aggiorna.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiorna.clicked.connect(self.salva_modifiche_utente)

        btn_layout.addWidget(btn_elimina)
        btn_layout.addWidget(btn_aggiorna)
        layout.addLayout(btn_layout)

        layout.addStretch()
        return widget

    def _carica_dati_modifica(self):
        id_u = self.combo_utenti_modifica.currentData()
        if not id_u:
            self.edit_utente_nome.clear()
            self.edit_utente_cognome.clear()
            self.edit_utente_email.clear()
            return

        info = self.admin.get_info_utente(id_u)
        if info:
            self.edit_utente_nome.setText(info["nome"])
            self.edit_utente_cognome.setText(info["cognome"])
            self.edit_utente_email.setText(info["email"])

    def salva_modifiche_utente(self):
        id_u = self.combo_utenti_modifica.currentData()
        if not id_u: return

        nome = self.edit_utente_nome.text().strip()
        cognome = self.edit_utente_cognome.text().strip()
        email = self.edit_utente_email.text().strip()

        if not nome or not cognome or not email:
            QMessageBox.warning(self, "Attenzione", "Compila tutti i campi.")
            return

        successo, msg = self.admin.salva_modifiche_utente(id_u, nome, cognome, email)
        if successo:
            QMessageBox.information(self, "Successo", msg)
            self.ricarica_dati_admin()
        else:
            QMessageBox.critical(self, "Errore", msg)

    def elimina_utente(self):
        id_u = self.combo_utenti_modifica.currentData()
        if not id_u: return

        risposta = QMessageBox.question(self, "Conferma Eliminazione",
                                        "Vuoi davvero eliminare questo utente? Tutti i suoi dati (libretti, esami, assegnazioni) verranno rimossi a cascata dal sistema.",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if risposta == QMessageBox.StandardButton.Yes:
            successo, msg = self.admin.elimina_utente(id_u)
            if successo:
                QMessageBox.information(self, "Successo", msg)
                self.ricarica_dati_admin()
            else:
                QMessageBox.critical(self, "Errore", msg)

    # --- TAB 3: ASSEGNAZIONI DOCENTI E TUTOR ---
    def _tab_assegnazioni(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)

        # Combo per scegliere il docente/tutor
        selez_layout = QHBoxLayout()
        selez_layout.addWidget(QLabel("<b>Seleziona Docente o Tutor:</b>"))
        self.combo_utenti_assegnazioni = QComboBox()
        self.combo_utenti_assegnazioni.currentIndexChanged.connect(self._carica_tabella_assegnazioni)
        selez_layout.addWidget(self.combo_utenti_assegnazioni)
        layout.addLayout(selez_layout)
        layout.addSpacing(10)

        # Tabella di visualizzazione
        self.tabella_assegnazioni = QTableWidget()
        self.tabella_assegnazioni.setColumnCount(2)
        self.tabella_assegnazioni.setHorizontalHeaderLabels(["CORSO DI LAUREA ASSEGNATO", "AZIONI"])
        self.tabella_assegnazioni.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabella_assegnazioni.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabella_assegnazioni.setStyleSheet("background-color: white; color: black; border: 1px solid #ccc;")
        layout.addWidget(self.tabella_assegnazioni)
        layout.addSpacing(10)

        # Controlli per aggiungere nuovo corso
        add_layout = QHBoxLayout()
        add_layout.addWidget(QLabel("<b>Nuovo Corso da Assegnare:</b>"))
        self.combo_nuovo_corso = QComboBox()
        btn_aggiungi_corso = QPushButton("➕ AGGIUNGI CORSO")
        btn_aggiungi_corso.setStyleSheet("background-color: #FF8C00; color: white; font-weight: bold; padding: 6px; border-radius: 4px;")
        btn_aggiungi_corso.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_aggiungi_corso.clicked.connect(self.aggiungi_assegnazione)

        add_layout.addWidget(self.combo_nuovo_corso)
        add_layout.addWidget(btn_aggiungi_corso)
        layout.addLayout(add_layout)

        return widget

    def _carica_tabella_assegnazioni(self):
        data = self.combo_utenti_assegnazioni.currentData()
        if not data:
            self.tabella_assegnazioni.setRowCount(0)
            return

        id_u = data["id"]
        ruolo = data["ruolo"]

        assegnazioni = self.admin.get_assegnazioni_utente(id_u, ruolo)

        self.tabella_assegnazioni.setRowCount(len(assegnazioni))
        for riga, ass in enumerate(assegnazioni):
            id_corso = ass["id_corso"]
            nome_corso = ass["nome_corso"]

            item = QTableWidgetItem(nome_corso)
            item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.tabella_assegnazioni.setItem(riga, 0, item)

            btn_rimuovi = QPushButton("❌ REVOCA ACCESSO")
            btn_rimuovi.setStyleSheet("background-color: #D32F2F; color: white; padding: 4px;")
            btn_rimuovi.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_rimuovi.clicked.connect(lambda checked, c_id=id_corso, r=ruolo, u=id_u: self.rimuovi_assegnazione(u, r, c_id))

            self.tabella_assegnazioni.setCellWidget(riga, 1, btn_rimuovi)

    def aggiungi_assegnazione(self):
        data = self.combo_utenti_assegnazioni.currentData()
        id_corso = self.combo_nuovo_corso.currentData()

        if not data or not id_corso: return
        id_u = data["id"]
        ruolo = data["ruolo"]

        successo, msg = self.admin.aggiungi_assegnazione(id_u, ruolo, id_corso)
        if successo:
            self._carica_tabella_assegnazioni()
            QMessageBox.information(self, "Successo", msg)
        else:
            QMessageBox.warning(self, "Attenzione", msg)

    def rimuovi_assegnazione(self, id_u, ruolo, id_corso):
        risposta = QMessageBox.question(self, "Conferma Revoca",
                                        "Sei sicuro di voler revocare l'accesso a questo corso?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if risposta == QMessageBox.StandardButton.Yes:
            successo, msg = self.admin.rimuovi_assegnazione(id_u, ruolo, id_corso)
            if successo:
                self._carica_tabella_assegnazioni()
            else:
                QMessageBox.critical(self, "Errore", msg)

    # --- RICARICA GLOBALE DEI DATI DELLE COMBOBOX ---
    def ricarica_dati_admin(self):
        # 1. Carica corsi per Creazione e Assegnazione
        self.combo_corso_associato.blockSignals(True)
        self.combo_nuovo_corso.blockSignals(True)
        self.combo_corso_associato.clear()
        self.combo_nuovo_corso.clear()

        corsi = self.admin.get_corsi_laurea()
        for c in corsi:
            self.combo_corso_associato.addItem(c["nome"], c["id"])
            self.combo_nuovo_corso.addItem(c["nome"], c["id"])

        self.combo_corso_associato.blockSignals(False)
        self.combo_nuovo_corso.blockSignals(False)

        # 2. Carica TUTTI gli utenti per Modifica/Elimina
        self.combo_utenti_modifica.blockSignals(True)
        self.combo_utenti_modifica.clear()

        utenti = self.admin.get_utenti_modifica()
        for u in utenti:
            self.combo_utenti_modifica.addItem(f"{u['nome']} {u['cognome']} (ID: {u['id']})", u['id'])

        self.combo_utenti_modifica.blockSignals(False)

        # 3. Carica SOLO Professori e Tutor per le Assegnazioni
        self.combo_utenti_assegnazioni.blockSignals(True)
        self.combo_utenti_assegnazioni.clear()

        utenti_ass = self.admin.get_utenti_assegnazioni()
        for u in utenti_ass:
            self.combo_utenti_assegnazioni.addItem(f"[{u['ruolo']}] {u['nome']} {u['cognome']}", {"id": u['id'], "ruolo": u['ruolo']})

        self.combo_utenti_assegnazioni.blockSignals(False)

        # Aggiorniamo i campi a schermo in base alle nuove combo
        self._carica_dati_modifica()
        self._carica_tabella_assegnazioni()

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

        # Sfruttiamo il metodo ereditato direttamente dall'oggetto Utente/Admin!
        successo, messaggio = self.admin.cambia_password(pwd_attuale, pwd_nuova)

        if successo:
            QMessageBox.information(self, "Successo", messaggio)
            self.input_pwd_attuale.clear()
            self.input_pwd_nuova.clear()
            self.input_pwd_conferma.clear()
        else:
            QMessageBox.critical(self, "Errore", messaggio)

    def esegui_logout(self):
        from ui.login_window import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()