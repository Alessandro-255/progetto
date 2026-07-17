import sqlite3
from .core import DB_PATH, Utente

class Tutor(Utente):
    def __init__(self, id_utente, nome, cognome):
        super().__init__(id_utente, nome, cognome)
        self.ruolo = "Tutor"

    def get_materie_tutor(self):
        """
        Recupera tutte le materie collegate ai Corsi di Laurea 
        a cui il tutor è stato associato.
        """
        materie = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query = """
                SELECT m.ID_MATERIA, m.Nome, c.Nome AS NomeCorso
                FROM Corso_Tutor ct
                JOIN Corso_Materia cm ON ct.COD_CORSO = cm.COD_CORSO
                JOIN Materia m ON cm.COD_MATERIA = m.ID_MATERIA
                JOIN Corso c ON ct.COD_CORSO = c.ID_CORSO
                WHERE ct.COD_TUTOR = ?
            """
            cur.execute(query, (self.id_utente,))
            for r in cur.fetchall():
                materie.append({
                    "id_materia": r[0], 
                    "nome_materia": r[1], 
                    "nome_corso": r[2]
                })
        return materie