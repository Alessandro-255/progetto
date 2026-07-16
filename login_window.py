from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from database import autentica_utente
from student_dashboard import StudentDashboard
from dashboard_professore import ProfessorDashboard
from admin_dashboard import AdminDashboard

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autenticazione - Gestionale UNIVPM")
        self.setFixedSize(350, 250)
        self._inizializza_ui()
        # Manteniamo i riferimenti per non far distruggere le finestre
        self.dashboard = None
        self.dashboard_prof = None
        self.dashboard_admin = None  # <-- Riferimento per la dashboard admin

    def _inizializza_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        self.label_titolo = QLabel("Benvenuto nel Gestionale")
        font = self.label_titolo.font()
        font.setPointSize(14)
        font.setBold(True)
        self.label_titolo.setFont(font)
        self.label_titolo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label_titolo)

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Indirizzo Email")
        layout.addWidget(self.input_email)

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Password")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.input_password)

        self.btn_login = QPushButton("Accedi")
        self.btn_login.clicked.connect(self.gestisci_login)
        self.btn_login.setStyleSheet("background-color: #0055A4; color: white; padding: 5px;")
        layout.addWidget(self.btn_login)

        self.setLayout(layout)

    def gestisci_login(self):
        email = self.input_email.text().strip()
        password = self.input_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Attenzione", "Devi inserire sia l'email che la password.")
            return

        try:
            risultato = autentica_utente(email, password)

            if risultato.get("successo"):
                ruolo = risultato['ruolo']

                # --- SMISTAMENTO RUOLI ---
                if ruolo == "Studente":
                    self.dashboard = StudentDashboard(
                        id_utente=risultato['id'],
                        nome=risultato['nome'],
                        cognome=risultato['cognome']
                    )
                    self.dashboard.show()
                    self.close()

                elif ruolo == "Professore":
                    self.dashboard_prof = ProfessorDashboard(
                        id_utente=risultato['id'],
                        nome=risultato['nome'],
                        cognome=risultato['cognome']
                    )
                    self.dashboard_prof.show()
                    self.close()

                elif ruolo == "Admin":
                    self.dashboard_admin = AdminDashboard(
                        id_utente=risultato['id'],
                        nome=risultato['nome'],
                        cognome=risultato['cognome']
                    )
                    self.dashboard_admin.show()
                    self.close()

                else:
                    # Tutor e altri ruoli
                    QMessageBox.information(self, "Accesso",
                                            f"Accesso riuscito come {ruolo}.\nInterfaccia in costruzione.")
            else:
                errore_msg = risultato.get("errore", "Errore sconosciuto.")
                QMessageBox.critical(self, "Accesso Negato", errore_msg)

        except Exception as e:
            QMessageBox.critical(self, "Errore Critico", f"Si è verificato un errore inaspettato:\n{str(e)}")