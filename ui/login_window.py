from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from .tutor_dashboard import TutorDashboard

from database.auth import autentica

from .student_dashboard import StudentDashboard
from .dashboard_professore import ProfessorDashboard
from .admin_dashboard import AdminDashboard

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Autenticazione - Gestionale UNIVPM")
        self.setFixedSize(350, 250)
        self._inizializza_ui()
        self.dashboard = None

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

        successo, msg, utente_loggato = autentica(email, password)

        if successo:
            u_id = utente_loggato.id_utente
            u_nome = utente_loggato.nome
            u_cognome = utente_loggato.cognome

            if utente_loggato.ruolo == "Studente":
                self.dashboard = StudentDashboard(u_id, u_nome, u_cognome)
                self.dashboard.show()
                self.close()
            elif utente_loggato.ruolo == "Professore":
                self.dashboard = ProfessorDashboard(u_id, u_nome, u_cognome)
                self.dashboard.show()
                self.close()
            elif utente_loggato.ruolo == "Admin":
                self.dashboard = AdminDashboard(u_id, u_nome, u_cognome)
                self.dashboard.show()
                self.close()
            elif utente_loggato.ruolo == "Tutor":
                self.dashboard = TutorDashboard(u_id, u_nome, u_cognome)
                self.dashboard.show()
                self.close()
            else:
                QMessageBox.information(self, "Accesso", f"Interfaccia per {utente_loggato.ruolo} in costruzione.")
        else:
            QMessageBox.critical(self, "Accesso Negato", msg)