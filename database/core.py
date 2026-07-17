import sqlite3
import os

# Punta alla cartella principale del progetto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'GestioneUniversita.db')

class Utente:
    """Superclasse base per tutti gli utenti del sistema."""
    def __init__(self, id_utente, nome, cognome):
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.ruolo = "Sconosciuto"

    def cambia_password(self, vecchia_pass, nuova_pass):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("SELECT Password FROM Utente WHERE ID_UTENTE = ?", (self.id_utente,))
                res = cur.fetchone()
                if res and res[0] == vecchia_pass:
                    cur.execute("UPDATE Utente SET Password = ? WHERE ID_UTENTE = ?", (nuova_pass, self.id_utente))
                    conn.commit()
                    return True, "Password aggiornata con successo."
                return False, "La password attuale non è corretta."
        except sqlite3.Error as e:
            return False, f"Errore DB: {e}"