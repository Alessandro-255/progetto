import sqlite3
from .core import DB_PATH, Utente
from .studente import Studente
from .professore import Professore
from .admin import Admin
from .tutor import Tutor
from .auth import autentica

# Alias nel caso qualche dashboard usi il vecchio nome
autentica_utente = autentica

# ==========================================
# BRIDGE (FACCIATA) PER LE DASHBOARD
# ==========================================

def cambia_password(id_utente, vecchia, nuova):
    # Creiamo un utente fittizio solo per sfruttare il suo metodo
    return Utente(id_utente, "", "").cambia_password(vecchia, nuova)

# --- FUNZIONI STUDENTE ---
def get_dati_studente(id_utente):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT Matricola FROM Studente WHERE ID_STUDENTE = ?", (id_utente,))
        res = cur.fetchone()
        return res[0] if res else ""

def get_corsi_studente(id_utente):
    return Studente(id_utente, "", "", "", None).get_corsi_attivi()

def get_materie_disponibili(id_utente):
    return Studente(id_utente, "", "", "", None).get_materie_disponibili()

def iscrivi_studente_materia(id_utente, id_materia):
    return Studente(id_utente, "", "", "", None).iscrivi_materia(id_materia)

def get_appelli_per_studente(id_utente):
    return Studente(id_utente, "", "", "", None).get_appelli()

def prenota_appello_studente(id_utente, id_appello):
    return Studente(id_utente, "", "", "", None).prenota_appello(id_appello)

def get_dati_libretto(id_utente):
    return Studente(id_utente, "", "", "", None).get_dati_libretto()

def gestisci_verbalizzazione(id_sospeso, accetta=True):
    return Studente(0, "", "", "", None).gestisci_verbalizzazione(id_sospeso, accetta)

def rifiuta_voto_libretto(id_libretto):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM Libretto WHERE ID_Libretto = ?", (id_libretto,))
            conn.commit()
        return True
    except sqlite3.Error:
        return False
def get_corso_laurea_studente(id_utente):
    return Studente(id_utente, "", "", "", None).get_corso_laurea()

def get_stato_dsa(id_utente):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT DSA FROM Studente WHERE ID_STUDENTE = ?", (id_utente,))
        res = cur.fetchone()
        return res[0] if res else None

def set_stato_dsa(id_utente, stato):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Studente SET DSA = ? WHERE ID_STUDENTE = ?", (stato, id_utente))
            conn.commit()
        return True
    except sqlite3.Error:
        return False

# --- FUNZIONI PROFESSORE E CORSI ---
def get_corsi_professore(id_utente):
    return Professore(id_utente, "", "").get_corsi_professore()

def get_tutti_corsi_laurea():
    return Admin(0, "", "").get_corsi_laurea()

def crea_nuova_materia(id_prof, nome, cfu, id_corso):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Materia (Nome, Numero_CFU, COD_PROFESSORE) VALUES (?, ?, ?)", (nome, cfu, id_prof))
            id_mat = cur.lastrowid
            cur.execute("INSERT INTO Corso_Materia (COD_CORSO, COD_MATERIA) VALUES (?, ?)", (id_corso, id_mat))
            conn.commit()
        return True, "Materia creata"
    except Exception as e:
        return False, str(e)

def get_info_materia(id_materia):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT m.Nome, c.Nome 
            FROM Materia m 
            LEFT JOIN Corso_Materia cm ON m.ID_MATERIA = cm.COD_MATERIA 
            LEFT JOIN Corso c ON cm.COD_CORSO = c.ID_CORSO 
            WHERE m.ID_MATERIA = ?
        """, (id_materia,))
        res = cur.fetchone()
        return res if res else ("Sconosciuto", "Sconosciuto")

def get_materiale_corso(id_materia):
    mat = []
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT ID_MATERIALE, Path_File FROM Materiale WHERE COD_MATERIA = ?", (id_materia,))
        for r in cur.fetchall():
            mat.append({"id": r[0], "file": r[1]})
    return mat

def aggiungi_materiale_corso(id_materia, path):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO Materiale (COD_MATERIA, Path_File) VALUES (?, ?)", (id_materia, path))
        conn.commit()

def get_path_materiale(id_materiale):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT Path_File FROM Materiale WHERE ID_MATERIALE = ?", (id_materiale,))
        res = cur.fetchone()
        return res[0] if res else None

def elimina_materiale_corso(id_materiale):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM Materiale WHERE ID_MATERIALE = ?", (id_materiale,))
        conn.commit()

        # --- FUNZIONI TUTOR ---
def get_materie_tutor(id_utente):
    return Tutor(id_utente, "", "").get_materie_tutor()

def get_professore_by_materia(id_materia):
    """Recupera il Nome e Cognome del professore titolare della materia."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.Nome, u.Cognome 
            FROM Materia m
            LEFT JOIN Professore p ON m.COD_PROFESSORE = p.ID_PROF
            LEFT JOIN Utente u ON p.ID_PROF = u.ID_UTENTE
            WHERE m.ID_MATERIA = ?
        """, (id_materia,))
        res = cur.fetchone()
        if res and res[0]:
            return f"Prof. {res[0]} {res[1]}"
        return "Nessun Docente Assegnato"

    