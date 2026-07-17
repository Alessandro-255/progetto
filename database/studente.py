import sqlite3
from .core import DB_PATH, Utente

class Studente(Utente):
    def __init__(self, id_utente, nome, cognome, matricola, dsa):
        super().__init__(id_utente, nome, cognome)
        self.ruolo = "Studente"
        self.matricola = matricola
        self.dsa = dsa

    def get_corsi_attivi(self):
        corsi = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query = """
                SELECT m.Nome, u.Cognome, m.Anno, m.Numero_CFU, m.ID_MATERIA
                FROM Materia_Studenti ms
                         JOIN Materia m ON ms.COD_MATERIA = m.ID_MATERIA
                         LEFT JOIN Professore p ON m.COD_PROFESSORE = p.ID_PROF
                         LEFT JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
                WHERE ms.COD_STUDENTE = ?
                  AND m.ID_MATERIA NOT IN (SELECT a.COD_MATERIA FROM Libretto l JOIN Appello a ON l.COD_APPELLO = a.ID_APPELLO WHERE l.COD_STUDENTE = ?)
            """
            cur.execute(query, (self.id_utente, self.id_utente))
            for r in cur.fetchall():
                corsi.append({"nome_materia": r[0], "professore": f"Prof. {r[1]}" if r[1] else "Nessun Prof", "anno": r[2], "cfu": r[3], "id_materia": r[4]})
        return corsi

    def get_materie_disponibili(self):
        materie = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query = """
                SELECT m.ID_MATERIA, m.Nome, m.Anno, m.Numero_CFU, u.Cognome,
                       (SELECT MIN(Data) FROM Appello a WHERE a.COD_MATERIA = m.ID_MATERIA AND a.Data >= date ('now')) as Prossimo_Appello
                FROM Materia m
                    LEFT JOIN Professore p ON m.COD_PROFESSORE = p.ID_PROF
                    LEFT JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
                WHERE m.ID_MATERIA NOT IN (SELECT COD_MATERIA FROM Materia_Studenti WHERE COD_STUDENTE = ?)
            """
            cur.execute(query, (self.id_utente,))
            for r in cur.fetchall():
                materie.append({"id_materia": r[0], "nome_materia": r[1], "anno": r[2], "cfu": r[3], "professore": f"Prof. {r[4]}" if r[4] else "Nessun Prof", "prossimo_appello": r[5] if r[5] else "Da definire"})
        return materie

    def iscrivi_materia(self, id_materia):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA) VALUES (?, ?)", (self.id_utente, id_materia))
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_appelli(self):
        disponibili, prenotati = [], []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            query_disp = """
                 SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio, a.Gruppo
                 FROM Appello a
                          JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                          JOIN Materia_Studenti ms ON m.ID_MATERIA = ms.COD_MATERIA
                 WHERE ms.COD_STUDENTE = ? AND a.Data >= date ('now') AND (a.Chiuso = FALSE OR a.Chiuso IS NULL)
                   AND a.ID_APPELLO NOT IN (SELECT COD_APPELLO FROM Prenotazione WHERE COD_STUDENTE = ?)
                   AND m.ID_MATERIA NOT IN (SELECT app.COD_MATERIA FROM Libretto l JOIN Appello app ON l.COD_APPELLO = app.ID_APPELLO WHERE l.COD_STUDENTE = ?)
                   AND m.ID_MATERIA NOT IN (SELECT app.COD_MATERIA FROM Voto_Da_Verbalizzare v JOIN Appello app ON v.COD_APPELLO = app.ID_APPELLO WHERE v.COD_STUDENTE = ?)
            """
            cur.execute(query_disp, (self.id_utente, self.id_utente, self.id_utente, self.id_utente))
            for r in cur.fetchall():
                disponibili.append({"id_appello": r[0], "materia": r[1], "data": r[2], "ora": r[3], "gruppo": "SI" if r[4] else "NO"})

            query_pren = """
                 SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio
                 FROM Prenotazione p
                          JOIN Appello a ON p.COD_APPELLO = a.ID_APPELLO
                          JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                 WHERE p.COD_STUDENTE = ? AND (a.Chiuso = FALSE OR a.Chiuso IS NULL)
            """
            cur.execute(query_pren, (self.id_utente,))
            for r in cur.fetchall():
                prenotati.append({"id_appello": r[0], "materia": r[1], "data": r[2], "ora": r[3]})
        return disponibili, prenotati

    def prenota_appello(self, id_appello):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("INSERT INTO Prenotazione (COD_STUDENTE, COD_APPELLO) VALUES (?, ?)", (self.id_utente, id_appello))
                conn.commit()
            return True
        except sqlite3.Error:
            return False

    def get_dati_libretto(self):
        da_verbalizzare, superati = [], []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT v.ID_VOTO_SOSPESO, m.Nome, v.Voto_Proposto
                FROM Voto_Da_Verbalizzare v
                         JOIN Appello a ON v.COD_APPELLO = a.ID_APPELLO
                         JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                WHERE v.COD_STUDENTE = ?
            """, (self.id_utente,))
            for r in cur.fetchall():
                da_verbalizzare.append({"id_sospeso": r[0], "materia": r[1], "voto": r[2]})

            cur.execute("""
                SELECT m.Nome, l.Voto, m.Numero_CFU, a.Gruppo, l.ID_Libretto
                FROM Libretto l
                         JOIN Appello a ON l.COD_APPELLO = a.ID_APPELLO
                         JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                WHERE l.COD_STUDENTE = ?
            """, (self.id_utente,))
            for r in cur.fetchall():
                superati.append({"materia": r[0], "voto": r[1], "cfu": r[2], "gruppo": "SI" if r[3] else "NO", "id_libretto": r[4]})
        return da_verbalizzare, superati

    def gestisci_verbalizzazione(self, id_sospeso, accetta=True):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                if accetta:
                    cur.execute("SELECT COD_STUDENTE, COD_APPELLO, Voto_Proposto FROM Voto_Da_Verbalizzare WHERE ID_VOTO_SOSPESO = ?", (id_sospeso,))
                    dati = cur.fetchone()
                    if dati:
                        cur.execute("INSERT INTO Libretto (Voto, COD_STUDENTE, COD_APPELLO) VALUES (?, ?, ?)", (dati[2], dati[0], dati[1]))
                cur.execute("DELETE FROM Voto_Da_Verbalizzare WHERE ID_VOTO_SOSPESO = ?", (id_sospeso,))
                conn.commit()
            return True
        except sqlite3.Error:
            return False