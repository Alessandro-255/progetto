import sqlite3
from .core import DB_PATH, Utente


class Professore(Utente):
    def __init__(self, id_utente, nome, cognome):
        super().__init__(id_utente, nome, cognome)
        self.ruolo = "Professore"

    def get_corsi_professore(self):
        corsi = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query = """
                    SELECT m.ID_MATERIA,
                           m.Nome,
                           m.Numero_CFU,
                           m.Anno,
                           (SELECT COUNT(*)
                            FROM Materia_Studenti ms
                            WHERE ms.COD_MATERIA = m.ID_MATERIA) as Num_Iscritti
                    FROM Materia m
                    WHERE m.COD_PROFESSORE = ?
                    """
            cur.execute(query, (self.id_utente,))
            for r in cur.fetchall():
                corsi.append({"id_materia": r[0], "nome": r[1], "cfu": r[2], "anno": r[3], "iscritti": r[4]})
        return corsi

    def get_corsi_assegnati(self):
        """Recupera i Corsi di Laurea a cui l'Admin ha assegnato questo professore."""
        corsi = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                        SELECT c.ID_CORSO, c.Nome
                        FROM Corso_Professore cp
                                 JOIN Corso c ON cp.COD_CORSO = c.ID_CORSO
                        WHERE cp.COD_PROFESSORE = ?
                        """, (self.id_utente,))
            for r in cur.fetchall():
                corsi.append({"id": r[0], "nome": r[1]})
        return corsi

    def crea_nuova_materia(self, nome, cfu, anno, id_corso):
        """Crea la materia e la associa al corso di laurea corretto."""
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO Materia (Nome, Numero_CFU, COD_PROFESSORE, Anno) VALUES (?, ?, ?, ?)",
                            (nome, cfu, self.id_utente, anno))
                id_mat = cur.lastrowid

                cur.execute("INSERT INTO Corso_Materia (COD_CORSO, COD_MATERIA) VALUES (?, ?)",
                            (id_corso, id_mat))
                conn.commit()
            return True, "Materia creata con successo."
        except sqlite3.Error as e:
            return False, f"Errore Database: {e}"