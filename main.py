import sys
from PyQt6.QtWidgets import QApplication, QMessageBox

from login_window import LoginWindow


def avvia_applicazione():
    try:
        app = QApplication(sys.argv)

        # Inizializza e mostra la finestra di login
        finestra_login = LoginWindow()
        finestra_login.show()

        # Avvia il loop degli eventi dell'applicazione
        sys.exit(app.exec())

    except Exception as e:
        # Se c'è un errore fatale (es. mancano librerie PyQt), lo stampiamo e gestiamo
        print(f"Errore fatale all'avvio dell'applicazione: {e}")


if __name__ == "__main__":
    avvia_applicazione()