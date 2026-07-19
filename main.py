import sys
from PyQt6.QtWidgets import QApplication
from ui.login_window import LoginWindow

def avvia_applicazione():
    try:
        app = QApplication(sys.argv)
        finestra_login = LoginWindow()
        finestra_login.show()
        sys.exit(app.exec())
    except Exception as e:
        print(f"Errore fatale all'avvio dell'applicazione: {e}")

if __name__ == "__main__":
    avvia_applicazione()