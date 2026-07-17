import sqlite3
from .core import DB_PATH, Utente

class Admin(Utente):
    def __init__(self, id_utente, nome, cognome):
        super().__init__(id_utente, nome, cognome)
        self.ruolo = "Admin"

    def get_corsi_laurea(self):
        corsi = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT ID_CORSO, Nome FROM Corso")
            for r in cur.fetchall():
                corsi.append({"id": r[0], "nome": r[1]})
        return corsi

    def get_utenti_modifica(self):
        utenti = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            # Escludiamo l'admin stesso per evitare auto-eliminazioni accidentali
            cur.execute("SELECT ID_UTENTE, Nome, Cognome FROM Utente WHERE Email != 'admin@uni.it'")
            for r in cur.fetchall():
                utenti.append({"id": r[0], "nome": r[1], "cognome": r[2]})
        return utenti

    def get_utenti_assegnazioni(self):
        utenti = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.ID_UTENTE, u.Nome, u.Cognome, 'Professore' as Ruolo FROM Professore p JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
                UNION
                SELECT u.ID_UTENTE, u.Nome, u.Cognome, 'Tutor' as Ruolo FROM Tutor t JOIN Utente u ON t.ID_TUTOR = u.ID_UTENTE
            """)
            for r in cur.fetchall():
                utenti.append({"id": r[0], "nome": r[1], "cognome": r[2], "ruolo": r[3]})
        return utenti

    def get_info_utente(self, id_u):
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("SELECT Nome, Cognome, Email FROM Utente WHERE ID_UTENTE = ?", (id_u,))
            res = cur.fetchone()
            if res:
                return {"nome": res[0], "cognome": res[1], "email": res[2]}
        return None

    def salva_nuovo_utente(self, ruolo, nome, cognome, email, cf, password, matricola, id_corso):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;")
                cur.execute(
                    "INSERT INTO Utente (Nome, Cognome, Data_Nascita, COD_FISCALE, Email, Password) VALUES (?, ?, '2000-01-01', ?, ?, ?)",
                    (nome, cognome, cf, email, password)
                )
                id_utente = cur.lastrowid

                if ruolo == "Studente":
                    cur.execute("INSERT INTO Studente (ID_STUDENTE, Matricola) VALUES (?, ?)", (id_utente, matricola))
                elif ruolo == "Professore":
                    cur.execute("INSERT INTO Professore (ID_PROF) VALUES (?)", (id_utente,))
                    if id_corso:
                        cur.execute("INSERT INTO Corso_Professore (COD_PROFESSORE, COD_CORSO) VALUES (?, ?)", (id_utente, id_corso))
                elif ruolo == "Tutor":
                    cur.execute("INSERT INTO Tutor (ID_TUTOR) VALUES (?)", (id_utente,))
                    if id_corso:
                        cur.execute("INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) VALUES (?, ?)", (id_utente, id_corso))
                conn.commit()
            return True, f"{ruolo} {nome} {cognome} creato con successo!"
        except sqlite3.Error as e:
            return False, f"Impossibile registrare l'utente: {e}"

    def salva_modifiche_utente(self, id_u, nome, cognome, email):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("UPDATE Utente SET Nome = ?, Cognome = ?, Email = ? WHERE ID_UTENTE = ?", (nome, cognome, email, id_u))
                conn.commit()
            return True, "Informazioni aggiornate correttamente."
        except sqlite3.Error as e:
            return False, f"Errore DB: {e}"

    def elimina_utente(self, id_u):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("PRAGMA foreign_keys = ON;") # Attiva eliminazione a cascata
                cur.execute("DELETE FROM Utente WHERE ID_UTENTE = ?", (id_u,))
                conn.commit()
            return True, "L'utente è stato eliminato dal database con tutti i dati associati."
        except sqlite3.Error as e:
            return False, f"Errore DB: {e}"

    def get_assegnazioni_utente(self, id_u, ruolo):
        assegnazioni = []
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            if ruolo == 'Professore':
                cur.execute("SELECT c.ID_CORSO, c.Nome FROM Corso_Professore cp JOIN Corso c ON cp.COD_CORSO = c.ID_CORSO WHERE cp.COD_PROFESSORE = ?", (id_u,))
            elif ruolo == 'Tutor':
                cur.execute("SELECT c.ID_CORSO, c.Nome FROM Corso_Tutor ct JOIN Corso c ON ct.COD_CORSO = c.ID_CORSO WHERE ct.COD_TUTOR = ?", (id_u,))
            for r in cur.fetchall():
                assegnazioni.append({"id_corso": r[0], "nome_corso": r[1]})
        return assegnazioni

    def aggiungi_assegnazione(self, id_u, ruolo, id_corso):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                if ruolo == 'Professore':
                    cur.execute("SELECT 1 FROM Corso_Professore WHERE COD_PROFESSORE=? AND COD_CORSO=?", (id_u, id_corso))
                    if cur.fetchone():
                        return False, "Il professore è già stato assegnato a questo corso."
                    cur.execute("INSERT INTO Corso_Professore (COD_PROFESSORE, COD_CORSO) VALUES (?, ?)", (id_u, id_corso))
                elif ruolo == 'Tutor':
                    cur.execute("SELECT 1 FROM Corso_Tutor WHERE COD_TUTOR=? AND COD_CORSO=?", (id_u, id_corso))
                    if cur.fetchone():
                        return False, "Il tutor è già stato assegnato a questo corso."
                    cur.execute("INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) VALUES (?, ?)", (id_u, id_corso))
                conn.commit()
            return True, f"{ruolo} assegnato al nuovo corso con successo!"
        except sqlite3.Error as e:
            return False, f"Errore DB: {e}"

    def rimuovi_assegnazione(self, id_u, ruolo, id_corso):
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                if ruolo == 'Professore':
                    cur.execute("DELETE FROM Corso_Professore WHERE COD_PROFESSORE=? AND COD_CORSO=?", (id_u, id_corso))
                elif ruolo == 'Tutor':
                    cur.execute("DELETE FROM Corso_Tutor WHERE COD_TUTOR=? AND COD_CORSO=?", (id_u, id_corso))
                conn.commit()
            return True, "Accesso al corso revocato con successo."
        except sqlite3.Error as e:
            return False, f"Errore DB: {e}"