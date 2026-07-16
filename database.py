import sqlite3
import os

# Determina il percorso assoluto per evitare problemi se si lancia lo script da cartelle diverse
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'GestioneUniversita.db')


def autentica_utente(email, password):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        query = "SELECT ID_UTENTE, Nome, Cognome FROM Utente WHERE Email = ? AND Password = ?"
        cursore.execute(query, (email, password))
        utente = cursore.fetchone()

        if utente:
            id_utente = utente[0]
            nome = utente[1]
            cognome = utente[2]
            ruolo = _determina_ruolo(cursore, id_utente)

            return {
                "successo": True,
                "id": id_utente,
                "nome": nome,
                "cognome": cognome,
                "ruolo": ruolo
            }
        else:
            return {"successo": False, "errore": "Email o password errati."}

    except sqlite3.Error as errore_db:
        return {"successo": False, "errore": f"Errore del database: {errore_db}"}
    except Exception as errore_generico:
        return {"successo": False, "errore": f"Errore di sistema: {errore_generico}"}
    finally:
        if connessione:
            connessione.close()


def _determina_ruolo(cursore, id_utente):
    tabelle_ruoli = ["Studente", "Professore", "Admin", "Tutor"]

    for ruolo in tabelle_ruoli:
        colonna_id = "ID_" + (ruolo.upper() if ruolo != "Professore" else "PROF")
        query = f"SELECT {colonna_id} FROM {ruolo} WHERE {colonna_id} = ?"
        cursore.execute(query, (id_utente,))
        if cursore.fetchone():
            return ruolo

    return "Sconosciuto"


def get_dati_studente(id_utente):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT Matricola FROM Studente WHERE ID_STUDENTE = ?", (id_utente,))
        risultato = cursore.fetchone()
        return risultato[0] if risultato else "Matricola non trovata"
    except sqlite3.Error as e:
        print(f"Errore DB in get_dati_studente: {e}")
        return "Errore DB"
    finally:
        if connessione:
            connessione.close()


def get_corsi_studente(id_studente):
    connessione = None
    corsi = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        query = """
                SELECT m.Nome, u.Cognome, m.Anno, m.Numero_CFU, m.ID_MATERIA
                FROM Materia_Studenti ms
                         JOIN Materia m ON ms.COD_MATERIA = m.ID_MATERIA
                         LEFT JOIN Professore p ON m.COD_PROFESSORE = p.ID_PROF
                         LEFT JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
                WHERE ms.COD_STUDENTE = ?
                  AND m.ID_MATERIA NOT IN (SELECT a.COD_MATERIA \
                                           FROM Libretto l \
                                                    JOIN Appello a ON l.COD_APPELLO = a.ID_APPELLO \
                                           WHERE l.COD_STUDENTE = ?) \
                """
        cursore.execute(query, (id_studente, id_studente))
        for r in cursore.fetchall():
            corsi.append({"nome_materia": r[0], "professore": f"Prof. {r[1]}" if r[1] else "Nessun Prof", "anno": r[2],
                          "cfu": r[3], "id_materia": r[4]})
        return corsi
    except sqlite3.Error as e:
        print(f"Errore: {e}")
        return []
    finally:
        if connessione: connessione.close()


def get_materie_disponibili(id_studente):
    connessione = None
    materie = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        query = """
                SELECT m.ID_MATERIA,
                       m.Nome,
                       m.Anno,
                       m.Numero_CFU,
                       u.Cognome,
                       (SELECT MIN(Data)
                        FROM Appello a
                        WHERE a.COD_MATERIA = m.ID_MATERIA \
                          AND a.Data >= date ('now')) as Prossimo_Appello
                FROM Materia m
                    LEFT JOIN Professore p
                ON m.COD_PROFESSORE = p.ID_PROF
                    LEFT JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
                WHERE m.ID_MATERIA NOT IN (
                    SELECT COD_MATERIA FROM Materia_Studenti WHERE COD_STUDENTE = ?
                    ) \
                """
        cursore.execute(query, (id_studente,))
        risultati = cursore.fetchall()

        for r in risultati:
            materie.append({
                "id_materia": r[0],
                "nome_materia": r[1],
                "anno": r[2],
                "cfu": r[3],
                "professore": f"Prof. {r[4]}" if r[4] else "Nessun Prof",
                "prossimo_appello": r[5] if r[5] else "Da definire"
            })
        return materie
    except sqlite3.Error as e:
        print(f"Errore DB in get_materie_disponibili: {e}")
        return []
    finally:
        if connessione:
            connessione.close()


def iscrivi_studente_materia(id_studente, id_materia):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA) VALUES (?, ?)",
                        (id_studente, id_materia))
        connessione.commit()
        return True
    except sqlite3.Error as e:
        print(f"Errore DB in iscrivi_studente: {e}")
        return False
    finally:
        if connessione:
            connessione.close()


def get_appelli_per_studente(id_studente):
    connessione = None
    disponibili = []
    prenotati = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        # Query aggiornata: esclude le materie già verbalizzate (in Libretto)
        # e quelle con un voto in attesa di accettazione (in Voto_Da_Verbalizzare)
        query_disp = """
                     SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio, a.Gruppo
                     FROM Appello a
                              JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                              JOIN Materia_Studenti ms ON m.ID_MATERIA = ms.COD_MATERIA
                     WHERE ms.COD_STUDENTE = ?
                       AND a.Data >= date ('now')
                       AND (a.Chiuso = FALSE OR a.Chiuso IS NULL)
                       AND a.ID_APPELLO NOT IN (SELECT COD_APPELLO FROM Prenotazione WHERE COD_STUDENTE = ?)
                       AND m.ID_MATERIA NOT IN (SELECT app.COD_MATERIA FROM Libretto l JOIN Appello app ON l.COD_APPELLO = app.ID_APPELLO WHERE l.COD_STUDENTE = ?)
                       AND m.ID_MATERIA NOT IN (SELECT app.COD_MATERIA FROM Voto_Da_Verbalizzare v JOIN Appello app ON v.COD_APPELLO = app.ID_APPELLO WHERE v.COD_STUDENTE = ?) \
                     """
        # Passiamo id_studente 4 volte per i rispettivi segnaposto "?"
        cursore.execute(query_disp, (id_studente, id_studente, id_studente, id_studente))
        for r in cursore.fetchall():
            disponibili.append(
                {"id_appello": r[0], "materia": r[1], "data": r[2], "ora": r[3], "gruppo": "SI" if r[4] else "NO"})

        query_pren = """
                     SELECT a.ID_APPELLO, m.Nome, a.Data, a.Ora_Inizio
                     FROM Prenotazione p
                              JOIN Appello a ON p.COD_APPELLO = a.ID_APPELLO
                              JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                     WHERE p.COD_STUDENTE = ? 
                       AND (a.Chiuso = FALSE OR a.Chiuso IS NULL) \
                     """
        cursore.execute(query_pren, (id_studente,))
        for r in cursore.fetchall():
            prenotati.append({"id_appello": r[0], "materia": r[1], "data": r[2], "ora": r[3]})

        return disponibili, prenotati
    except sqlite3.Error as e:
        print(f"Errore DB Appelli: {e}")
        return [], []
    finally:
        if connessione: connessione.close()


def prenota_appello_studente(id_studente, id_appello):
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("INSERT INTO Prenotazione (COD_STUDENTE, COD_APPELLO) VALUES (?, ?)", (id_studente, id_appello))
        connessione.commit()
        return True
    except sqlite3.Error:
        return False


def get_dati_libretto(id_studente):
    connessione = None
    da_verbalizzare = []
    superati = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        cursore.execute("""
                        SELECT v.ID_VOTO_SOSPESO, m.Nome, v.Voto_Proposto
                        FROM Voto_Da_Verbalizzare v
                                 JOIN Appello a ON v.COD_APPELLO = a.ID_APPELLO
                                 JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                        WHERE v.COD_STUDENTE = ?
                        """, (id_studente,))
        for r in cursore.fetchall():
            da_verbalizzare.append({"id_sospeso": r[0], "materia": r[1], "voto": r[2]})

        # MODIFICA QUI: Aggiunto l.ID_Libretto alla SELECT
        cursore.execute("""
                        SELECT m.Nome, l.Voto, m.Numero_CFU, a.Gruppo, l.ID_Libretto
                        FROM Libretto l
                                 JOIN Appello a ON l.COD_APPELLO = a.ID_APPELLO
                                 JOIN Materia m ON a.COD_MATERIA = m.ID_MATERIA
                        WHERE l.COD_STUDENTE = ?
                        """, (id_studente,))
        for r in cursore.fetchall():
            superati.append({"materia": r[0], "voto": r[1], "cfu": r[2], "gruppo": "SI" if r[3] else "NO", "id_libretto": r[4]})

        return da_verbalizzare, superati
    except sqlite3.Error:
        return [], []
    finally:
        if connessione: connessione.close()

# NUOVA FUNZIONE: per eliminare un voto già presente nel libretto
def rifiuta_voto_libretto(id_libretto):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("DELETE FROM Libretto WHERE ID_Libretto = ?", (id_libretto,))
        connessione.commit()
        return True
    except sqlite3.Error as e:
        print(f"Errore rimozione libretto: {e}")
        return False
    finally:
        if connessione: connessione.close()


def gestisci_verbalizzazione(id_sospeso, accetta=True):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        if accetta:
            cursore.execute(
                "SELECT COD_STUDENTE, COD_APPELLO, Voto_Proposto FROM Voto_Da_Verbalizzare WHERE ID_VOTO_SOSPESO = ?",
                (id_sospeso,))
            dati = cursore.fetchone()
            if dati:
                cursore.execute("INSERT INTO Libretto (Voto, COD_STUDENTE, COD_APPELLO) VALUES (?, ?, ?)",
                                (dati[2], dati[0], dati[1]))

        cursore.execute("DELETE FROM Voto_Da_Verbalizzare WHERE ID_VOTO_SOSPESO = ?", (id_sospeso,))
        connessione.commit()
        return True
    except sqlite3.Error as e:
        print(f"Errore Verbalizzazione: {e}")
        return False
    finally:
        if connessione: connessione.close()


def cambia_password(id_utente, vecchia_pass, nuova_pass):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT Password FROM Utente WHERE ID_UTENTE = ?", (id_utente,))
        risultato = cursore.fetchone()

        if risultato and risultato[0] == vecchia_pass:
            cursore.execute("UPDATE Utente SET Password = ? WHERE ID_UTENTE = ?", (nuova_pass, id_utente))
            connessione.commit()
            return True, "Password aggiornata con successo."
        return False, "La password attuale non è corretta."
    except sqlite3.Error as e:
        return False, f"Errore DB: {e}"
    finally:
        if connessione: connessione.close()


def get_stato_dsa(id_studente):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT DSA FROM Studente WHERE ID_STUDENTE = ?", (id_studente,))
        risultato = cursore.fetchone()
        return risultato[0] if risultato else None
    except sqlite3.Error:
        return None
    finally:
        if connessione: connessione.close()


def set_stato_dsa(id_studente, stato):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("UPDATE Studente SET DSA = ? WHERE ID_STUDENTE = ?", (stato, id_studente))
        connessione.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        if connessione: connessione.close()


def get_materiale_corso(id_materia):
    connessione = None
    materiali = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT ID_MATERIALE, Path_File FROM Materiale WHERE COD_MATERIA = ?", (id_materia,))
        for r in cursore.fetchall():
            materiali.append({"id": r[0], "file": r[1]})
        return materiali
    except sqlite3.Error as e:
        print(f"Errore DB Materiale: {e}")
        return []
    finally:
        if connessione: connessione.close()


# ==========================================
# GESTIONE PROFESSORE E MATERIE
# ==========================================
def get_corsi_professore(id_professore):
    connessione = None
    corsi = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        query = """
                SELECT m.ID_MATERIA,
                       m.Nome,
                       m.Numero_CFU,
                       m.Anno,
                       (SELECT COUNT(*) FROM Materia_Studenti ms WHERE ms.COD_MATERIA = m.ID_MATERIA) as Num_Iscritti
                FROM Materia m
                WHERE m.COD_PROFESSORE = ? \
                """
        cursore.execute(query, (id_professore,))
        for r in cursore.fetchall():
            corsi.append({
                "id_materia": r[0],
                "nome": r[1],
                "cfu": r[2],
                "anno": r[3],
                "iscritti": r[4]
            })
        return corsi
    except sqlite3.Error as e:
        print(f"Errore DB in get_corsi_professore: {e}")
        return []
    finally:
        if connessione:
            connessione.close()


def get_tutti_corsi_laurea():
    connessione = None
    corsi = []
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT ID_CORSO, Nome FROM Corso")
        for r in cursore.fetchall():
            corsi.append({"id_corso": r[0], "nome": r[1]})
        return corsi
    except sqlite3.Error as e:
        print(f"Errore DB in get_tutti_corsi_laurea: {e}")
        return []
    finally:
        if connessione: connessione.close()


def crea_nuova_materia(id_professore, nome_materia, cfu, id_corso_laurea, anno=1):
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()

        cursore.execute(
            "INSERT INTO Materia (Nome, Numero_CFU, COD_PROFESSORE, Anno) VALUES (?, ?, ?, ?)",
            (nome_materia, cfu, id_professore, anno)
        )
        id_materia = cursore.lastrowid

        cursore.execute(
            "INSERT INTO Corso_Materia (COD_CORSO, COD_MATERIA) VALUES (?, ?)",
            (id_corso_laurea, id_materia)
        )

        connessione.commit()
        return True, id_materia
    except sqlite3.Error as e:
        print(f"Errore DB in crea_nuova_materia: {e}")
        return False, str(e)
    finally:
        if connessione: connessione.close()


# --- FUNZIONI AGGIUNTE PER GESTIONE FILE E MATERIALI PROFESSORE ---

def get_info_materia(id_materia):
    """Recupera nome della materia e nome del corso di laurea ad essa associato."""
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        query = """
                SELECT m.Nome, c.Nome
                FROM Materia m
                         JOIN Corso_Materia cm ON m.ID_MATERIA = cm.COD_MATERIA
                         JOIN Corso c ON cm.COD_CORSO = c.ID_CORSO
                WHERE m.ID_MATERIA = ? \
                """
        cursore.execute(query, (id_materia,))
        res = cursore.fetchone()
        return res if res else ("Sconosciuto", "Sconosciuto")
    except sqlite3.Error:
        return ("Sconosciuto", "Sconosciuto")
    finally:
        if connessione: connessione.close()


def aggiungi_materiale_corso(id_materia, path_relativo):
    """Aggiunge il percorso di un nuovo file nel DB."""
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("INSERT INTO Materiale (COD_MATERIA, Path_File) VALUES (?, ?)", (id_materia, path_relativo))
        connessione.commit()
    except sqlite3.Error as e:
        print(f"Errore DB in aggiungi_materiale_corso: {e}")
    finally:
        if connessione: connessione.close()


def get_path_materiale(id_materiale):
    """Recupera il percorso del file dal DB prima di eliminarlo."""
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("SELECT Path_File FROM Materiale WHERE ID_MATERIALE = ?", (id_materiale,))
        res = cursore.fetchone()
        return res[0] if res else None
    except sqlite3.Error:
        return None
    finally:
        if connessione: connessione.close()


def elimina_materiale_corso(id_materiale):
    """Elimina il record del file dal DB."""
    connessione = None
    try:
        connessione = sqlite3.connect(DB_PATH)
        cursore = connessione.cursor()
        cursore.execute("DELETE FROM Materiale WHERE ID_MATERIALE = ?", (id_materiale,))
        connessione.commit()
    except sqlite3.Error as e:
        print(f"Errore DB in elimina_materiale_corso: {e}")
    finally:
        if connessione: connessione.close()