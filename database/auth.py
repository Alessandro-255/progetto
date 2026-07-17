import sqlite3
from .core import DB_PATH
from .studente import Studente
from .professore import Professore
from .admin import Admin
from .tutor import Tutor


def autentica(email, password):
    """Verifica le credenziali e istanzia l'oggetto corretto."""
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT ID_UTENTE, Nome, Cognome FROM Utente WHERE Email = ? AND Password = ?",
                        (email, password))
            res = cur.fetchone()

            if not res:
                return False, "Email o password errati.", None

            id_u, nome, cognome = res

            ruoli = ["Studente", "Professore", "Admin", "Tutor"]
            ruolo_trovato = None
            for r in ruoli:
                col_id = "ID_" + (r.upper() if r != "Professore" else "PROF")
                cur.execute(f"SELECT {col_id} FROM {r} WHERE {col_id} = ?", (id_u,))
                if cur.fetchone():
                    ruolo_trovato = r
                    break

            if ruolo_trovato == "Studente":
                cur.execute("SELECT Matricola, DSA FROM Studente WHERE ID_STUDENTE = ?", (id_u,))
                dati = cur.fetchone()
                return True, "Successo", Studente(id_u, nome, cognome, dati[0] if dati else "",
                                                  dati[1] if dati else None)
            elif ruolo_trovato == "Professore":
                return True, "Successo", Professore(id_u, nome, cognome)
            elif ruolo_trovato == "Admin":
                return True, "Successo", Admin(id_u, nome, cognome)
            elif ruolo_trovato == "Tutor":
                return True, "Successo", Tutor(id_u, nome, cognome)

            return False, "Ruolo non definito", None
    except Exception as e:
        return False, f"Errore DB: {e}", None