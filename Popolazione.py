import sqlite3
import random


def reset_e_crea_database():
    print("Inizio il reset e la creazione del database 'GestioneUniversita.db'...")

    connessione = sqlite3.connect('GestioneUniversita.db')
    cursore = connessione.cursor()

    cursore.execute("PRAGMA foreign_keys = ON;")

    # ==========================================
    # 1. CREAZIONE SCHEMA (Tabelle aggiornate)
    # ==========================================
    script_schema = """
                    DROP TABLE IF EXISTS Esito_Appello_Studente;
                    DROP TABLE IF EXISTS Voto_Da_Verbalizzare;
                    DROP TABLE IF EXISTS Prenotazione;
                    DROP TABLE IF EXISTS Libretto;
                    DROP TABLE IF EXISTS Materia_Studenti;
                    DROP TABLE IF EXISTS Corso_Materia;
                    DROP TABLE IF EXISTS Corso_Tutor;
                    DROP TABLE IF EXISTS Corso_Professore;
                    DROP TABLE IF EXISTS Corso_Studente;
                    DROP TABLE IF EXISTS Appello;
                    DROP TABLE IF EXISTS Materiale_del_Gruppo;
                    DROP TABLE IF EXISTS Materiale;
                    DROP TABLE IF EXISTS Materia;
                    DROP TABLE IF EXISTS Aula_Appello;
                    DROP TABLE IF EXISTS Gruppo;
                    DROP TABLE IF EXISTS Corso;
                    DROP TABLE IF EXISTS Admin;
                    DROP TABLE IF EXISTS Tutor;
                    DROP TABLE IF EXISTS Professore;
                    DROP TABLE IF EXISTS Studente;
                    DROP TABLE IF EXISTS Utente;

                    CREATE TABLE Utente (
                                            ID_UTENTE INTEGER PRIMARY KEY AUTOINCREMENT,
                                            Nome VARCHAR(100) NOT NULL,
                                            Cognome VARCHAR(100) NOT NULL,
                                            Data_Nascita DATE,
                                            COD_FISCALE VARCHAR(16) UNIQUE NOT NULL,
                                            Email VARCHAR(255) UNIQUE NOT NULL,
                                            Password VARCHAR(255) NOT NULL
                    );

                    CREATE TABLE Studente (
                                              ID_STUDENTE INTEGER PRIMARY KEY,
                                              Matricola VARCHAR(20) UNIQUE NOT NULL,
                                              DSA INTEGER DEFAULT NULL,
                                              FOREIGN KEY (ID_STUDENTE) REFERENCES Utente(ID_UTENTE) ON DELETE CASCADE
                    );

                    CREATE TABLE Professore (
                                                ID_PROF INTEGER PRIMARY KEY,
                                                FOREIGN KEY (ID_PROF) REFERENCES Utente(ID_UTENTE) ON DELETE CASCADE
                    );

                    CREATE TABLE Tutor (
                                           ID_TUTOR INTEGER PRIMARY KEY,
                                           FOREIGN KEY (ID_TUTOR) REFERENCES Utente(ID_UTENTE) ON DELETE CASCADE
                    );

                    CREATE TABLE Admin (
                                           ID_ADMIN INTEGER PRIMARY KEY,
                                           FOREIGN KEY (ID_ADMIN) REFERENCES Utente(ID_UTENTE) ON DELETE CASCADE
                    );

                    CREATE TABLE Corso (
                                           ID_CORSO INTEGER PRIMARY KEY AUTOINCREMENT,
                                           Nome VARCHAR(255) NOT NULL,
                                           Data_Creazione DATE,
                                           Anno_Inizio INTEGER,
                                           Anno_Fine INTEGER
                    );

                    CREATE TABLE Gruppo (
                                            ID_GRUPPO INTEGER PRIMARY KEY AUTOINCREMENT,
                                            Descrizione VARCHAR(255)
                    );

                    CREATE TABLE Aula_Appello (
                                                  ID_AULA INTEGER PRIMARY KEY AUTOINCREMENT,
                                                  Nome VARCHAR(100) NOT NULL,
                                                  Capienza INTEGER NOT NULL
                    );

                    CREATE TABLE Materia (
                                             ID_MATERIA INTEGER PRIMARY KEY AUTOINCREMENT,
                                             Nome VARCHAR(255) NOT NULL,
                                             Numero_CFU INTEGER NOT NULL,
                                             COD_PROFESSORE INTEGER,
                                             Anno INTEGER,
                                             FOREIGN KEY (COD_PROFESSORE) REFERENCES Professore(ID_PROF) ON DELETE SET NULL
                    );

                    CREATE TABLE Materiale (
                                               ID_MATERIALE INTEGER PRIMARY KEY AUTOINCREMENT,
                                               Path_File VARCHAR(255) NOT NULL,
                                               COD_MATERIA INTEGER,
                                               FOREIGN KEY (COD_MATERIA) REFERENCES Materia(ID_MATERIA) ON DELETE CASCADE
                    );

                    CREATE TABLE Materiale_del_Gruppo (
                                                          ID_MATERIALE_DEL_GRUPPO INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          COD_GRUPPO INTEGER,
                                                          Path_File VARCHAR(255) NOT NULL,
                                                          FOREIGN KEY (COD_GRUPPO) REFERENCES Gruppo(ID_GRUPPO) ON DELETE CASCADE
                    );

                    CREATE TABLE Appello (
                                             ID_APPELLO INTEGER PRIMARY KEY AUTOINCREMENT,
                                             Data DATE NOT NULL,
                                             Ora_Inizio TIME,
                                             Ora_Fine TIME,
                                             Descrizione TEXT,
                                             Gruppo BOOLEAN DEFAULT FALSE,
                                             Chiuso BOOLEAN DEFAULT FALSE,
                                             COD_MATERIA INTEGER,
                                             COD_AULA_APPELLO INTEGER,
                                             Limite_Iscritti INTEGER NOT NULL,
                                             FOREIGN KEY (COD_MATERIA) REFERENCES Materia(ID_MATERIA) ON DELETE CASCADE,
                                             FOREIGN KEY (COD_AULA_APPELLO) REFERENCES Aula_Appello(ID_AULA) ON DELETE SET NULL
                    );

                    CREATE TABLE Corso_Studente (
                                                    ID_CORSO_STUDENTE INTEGER PRIMARY KEY AUTOINCREMENT,
                                                    COD_STUDENTE INTEGER,
                                                    COD_CORSO INTEGER,
                                                    FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                                    FOREIGN KEY (COD_CORSO) REFERENCES Corso(ID_CORSO) ON DELETE CASCADE
                    );

                    CREATE TABLE Corso_Professore (
                                                      ID_CORSO_PROFESSORE INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      COD_PROFESSORE INTEGER,
                                                      COD_CORSO INTEGER,
                                                      FOREIGN KEY (COD_PROFESSORE) REFERENCES Professore(ID_PROF) ON DELETE CASCADE,
                                                      FOREIGN KEY (COD_CORSO) REFERENCES Corso(ID_CORSO) ON DELETE CASCADE
                    );

                    CREATE TABLE Corso_Tutor (
                                                 ID_CORSO_TUTOR INTEGER PRIMARY KEY AUTOINCREMENT,
                                                 COD_TUTOR INTEGER,
                                                 COD_CORSO INTEGER,
                                                 FOREIGN KEY (COD_TUTOR) REFERENCES Tutor(ID_TUTOR) ON DELETE CASCADE,
                                                 FOREIGN KEY (COD_CORSO) REFERENCES Corso(ID_CORSO) ON DELETE CASCADE
                    );

                    CREATE TABLE Corso_Materia (
                                                   ID_CORSO_MATERIA INTEGER PRIMARY KEY AUTOINCREMENT,
                                                   COD_CORSO INTEGER,
                                                   COD_MATERIA INTEGER,
                                                   FOREIGN KEY (COD_CORSO) REFERENCES Corso(ID_CORSO) ON DELETE CASCADE,
                                                   FOREIGN KEY (COD_MATERIA) REFERENCES Materia(ID_MATERIA) ON DELETE CASCADE
                    );

                    CREATE TABLE Materia_Studenti (
                                                      ID_MATERIA_STUDENTI INTEGER PRIMARY KEY AUTOINCREMENT,
                                                      COD_STUDENTE INTEGER,
                                                      COD_MATERIA INTEGER,
                                                      COD_GRUPPO INTEGER,
                                                      FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                                      FOREIGN KEY (COD_MATERIA) REFERENCES Materia(ID_MATERIA) ON DELETE CASCADE,
                                                      FOREIGN KEY (COD_GRUPPO) REFERENCES Gruppo(ID_GRUPPO) ON DELETE SET NULL
                    );

                    CREATE TABLE Libretto (
                                              ID_Libretto INTEGER PRIMARY KEY AUTOINCREMENT,
                                              Voto INTEGER,
                                              COD_STUDENTE INTEGER,
                                              COD_APPELLO INTEGER,
                                              FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                              FOREIGN KEY (COD_APPELLO) REFERENCES Appello(ID_APPELLO) ON DELETE CASCADE
                    );

                    CREATE TABLE Prenotazione (
                                                  ID_PRENOTAZIONE INTEGER PRIMARY KEY AUTOINCREMENT,
                                                  COD_STUDENTE INTEGER,
                                                  COD_APPELLO INTEGER,
                                                  FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                                  FOREIGN KEY (COD_APPELLO) REFERENCES Appello(ID_APPELLO) ON DELETE CASCADE
                    );

                    CREATE TABLE Voto_Da_Verbalizzare (
                                                          ID_VOTO_SOSPESO INTEGER PRIMARY KEY AUTOINCREMENT,
                                                          COD_STUDENTE INTEGER,
                                                          COD_APPELLO INTEGER,
                                                          Voto_Proposto INTEGER,
                                                          FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                                          FOREIGN KEY (COD_APPELLO) REFERENCES Appello(ID_APPELLO) ON DELETE CASCADE
                    );

                    CREATE TABLE Esito_Appello_Studente (
                                                            ID_ESITO INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            COD_APPELLO INTEGER,
                                                            COD_STUDENTE INTEGER,
                                                            Voto_Ottenuto INTEGER,
                                                            Stato VARCHAR(20),
                                                            FOREIGN KEY (COD_APPELLO) REFERENCES Appello(ID_APPELLO) ON DELETE CASCADE,
                                                            FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE
                    ); \
                    """

    # ==========================================
    # 2. INSERIMENTO DATI BASE (Utenti Test, Corsi, Aule)
    # ==========================================
    script_dati_base = """
                       -- CREDENZIALI DI TEST RAPIDO (I primi 8 ID)
                       INSERT INTO Utente (ID_UTENTE, Nome, Cognome, Data_Nascita, COD_FISCALE, Email, Password) \
                       VALUES (1, 'Mario', 'Rossi', '2001-05-15', 'RSSMRA01E15H501A', 'mario.rossi@studenti.uni.it', \
                               'password123'), \
                              (2, 'Giulia', 'Bianchi', '2002-03-22', 'BNCGLI02C22F205Z', \
                               'giulia.bianchi@studenti.uni.it', 'password123'), \
                              (3, 'Alan', 'Turing', '1912-06-23', 'TRNALN12H23Z404X', 'alan.turing@uni.it', \
                               'enigma456'), \
                              (4, 'Ada', 'Lovelace', '1815-12-10', 'LVLADA15T10Z404Y', 'ada.lovelace@tutor.uni.it', \
                               'engine789'), \
                              (5, 'Admin', 'Supremo', '1980-01-01', 'ADMSPR80A01H501W', 'admin', 'admin'), \
                              (6, 'Studente', 'Test', '2000-01-01', 'STUTST00A01H501Z', 'studente', 'studente'), \
                              (7, 'Tutor', 'Attivo', '1995-05-05', 'TUTTTV95E05H501Y', 'tutor', 'tutor'), \
                              (8, 'Professore', 'Docente', '1975-10-10', 'PRFDCT75R10H501X', 'prof', 'prof');

                       INSERT INTO Studente (ID_STUDENTE, Matricola, DSA) \
                       VALUES (1, 'MAT10001', 0), \
                              (2, 'MAT10002', 0), \
                              (6, 'MAT10003', 1);
                       INSERT INTO Professore (ID_PROF) \
                       VALUES (3), \
                              (8);
                       INSERT INTO Tutor (ID_TUTOR) \
                       VALUES (4), \
                              (7);
                       INSERT INTO Admin (ID_ADMIN) \
                       VALUES (5);

                       -- CORSI DI LAUREA
                       INSERT INTO Corso (ID_CORSO, Nome, Data_Creazione, Anno_Inizio, Anno_Fine) \
                       VALUES (1, 'Ingegneria Informatica', '2023-09-01', 2023, 2026), \
                              (2, 'Informatica Umanistica', '2023-09-01', 2023, 2026), \
                              (3, 'Ingegneria Biomedica', '2024-09-01', 2024, 2027);

                       -- AULE
                       INSERT INTO Aula_Appello (ID_AULA, Nome, Capienza) \
                       VALUES (1, 'Aula Magna', 250), \
                              (2, 'Aula 101', 50), \
                              (3, 'Laboratorio Turing', 35), \
                              (4, 'Aula 102 (Piccola)', 20), \
                              (5, 'Aula 103 (Media)', 80), \
                              (6, 'Laboratorio Von Neumann', 60);

                       -- MATERIE
                       INSERT INTO Materia (ID_MATERIA, Nome, Numero_CFU, COD_PROFESSORE, Anno) \
                       VALUES (1, 'Basi di Dati', 9, 3, 2), \
                              (2, 'Programmazione Web', 6, 3, 2), \
                              (3, 'Analisi Matematica 1', 12, 8, 1), \
                              (4, 'Biologia Cellulare', 6, 8, 1), \
                              (5, 'Architettura degli Elaboratori', 9, 8, 2);

                       -- COLLEGAMENTI CORSO <-> MATERIA
                       INSERT INTO Corso_Materia (COD_CORSO, COD_MATERIA) \
                       VALUES (1, 1), \
                              (1, 2), \
                              (1, 3), \
                              (1, 5), \
                              (2, 2), \
                              (3, 3), \
                              (3, 4);

                       -- ASSEGNAZIONI MANUALI (Test users)
                       INSERT INTO Corso_Studente (COD_STUDENTE, COD_CORSO) \
                       VALUES (1, 1), \
                              (2, 2), \
                              (6, 1);
                       INSERT INTO Corso_Professore (COD_PROFESSORE, COD_CORSO) \
                       VALUES (3, 1), \
                              (3, 2), \
                              (8, 1), \
                              (8, 3);
                       INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) \
                       VALUES (4, 1), \
                              (7, 1), \
                              (7, 3);
                       INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA, COD_GRUPPO) \
                       VALUES (1, 1, NULL), \
                              (1, 2, NULL), \
                              (2, 2, NULL), \
                              (6, 1, NULL), \
                              (6, 3, NULL), \
                              (6, 5, NULL);

                       -- APPELLI INIZIALI
                       INSERT INTO Appello (ID_APPELLO, Data, Ora_Inizio, Ora_Fine, Descrizione, Gruppo, Chiuso, \
                                            COD_MATERIA, COD_AULA_APPELLO, Limite_Iscritti) \
                       VALUES (1, '2026-06-20', '09:00:00', '11:00:00', 'Appello Estivo Basi di Dati', 0, 0, 1, 1, 250), \
                              (2, '2026-07-15', '14:00:00', '16:00:00', 'Appello Estivo Prog Web', 0, 0, 2, 2, 50), \
                              (3, '2026-07-20', '09:00:00', '12:00:00', 'Scritto Analisi Matematica 1', 0, 0, 3, 1, \
                               250), \
                              (4, '2026-01-15', '10:00:00', '12:00:00', 'Appello Invernale Architettura (CHIUSO)', 0, 1, \
                               5, 3, 35);

                       -- PRENOTAZIONI, VOTI E LIBRETTI PER GLI UTENTI TEST
                       INSERT INTO Prenotazione (COD_STUDENTE, COD_APPELLO) \
                       VALUES (6, 3), \
                              (1, 2);
                       INSERT INTO Libretto (Voto, COD_STUDENTE, COD_APPELLO) \
                       VALUES (28, 1, 1), \
                              (30, 2, 1), \
                              (24, 6, 4);
                       INSERT INTO Voto_Da_Verbalizzare (COD_STUDENTE, COD_APPELLO, Voto_Proposto) \
                       VALUES (6, 1, 27);
                       INSERT INTO Esito_Appello_Studente (COD_APPELLO, COD_STUDENTE, Voto_Ottenuto, Stato) \
                       VALUES (1, 6, 27, 'Superato'), \
                              (4, 6, 24, 'Superato'), \
                              (4, 1, NULL, 'Respinto'); \
                       """

    try:
        cursore.executescript(script_schema)
        cursore.executescript(script_dati_base)

        print("Schema base e utenti di test creati. Procedo alla generazione dei 300 utenti massivi...")

        # ==========================================
        # 3. GENERAZIONE MASSIVA IN PYTHON (~300 UTENTI)
        # ==========================================
        random.seed(42)  # Per generare sempre lo stesso database prevedibile

        nomi = ['Marco', 'Giulia', 'Alessandro', 'Martina', 'Lorenzo', 'Chiara', 'Matteo', 'Sara', 'Leonardo', 'Sofia',
                'Andrea', 'Anna', 'Gabriele', 'Francesca', 'Riccardo', 'Elena', 'Tommaso', 'Alice', 'Davide', 'Giorgia',
                'Simone', 'Beatrice', 'Luca', 'Vittoria', 'Christian', 'Aurora', 'Emanuele', 'Emma', 'Giacomo',
                'Camilla']
        cognomi = ['Rossi', 'Bianchi', 'Esposito', 'Russo', 'Romano', 'Colombo', 'Ricci', 'Marino', 'Greco', 'Bruno',
                   'Gallo', 'Conti', 'De Luca', 'Mancini', 'Costa', 'Giordano', 'Rizzo', 'Lombardi', 'Moretti',
                   'Barbieri', 'Fontana', 'Santoro', 'Caruso', 'Mariani', 'Martini', 'Ferraro', 'Galli', 'Rinaldi',
                   'Leone', 'Conte']

        corsi_materie = {
            1: [1, 2, 3, 5],
            2: [2],
            3: [3, 4]
        }

        utenti = []
        studenti = []
        professori = []
        tutor = []
        corso_studente = []
        materia_studenti = []
        prenotazioni = []

        ID_CORRENTE = 9  # I primi 8 ID sono occupati dai test users

        # GENERIAMO 280 STUDENTI
        for i in range(1, 281):
            nome = random.choice(nomi)
            cognome = random.choice(cognomi)
            cf = f"{nome[:3].upper()}{cognome[:3].upper()}{random.randint(10, 99)}A00H501{chr(65 + random.randint(0, 25))}"
            email = f"{nome.lower()}.{cognome.lower()}{i}@studenti.uni.it"

            # 1. Tabella Utente
            utenti.append((ID_CORRENTE, nome, cognome, '2002-05-10', cf, email, 'password123'))

            # 2. Tabella Studente
            matricola = f"MAT{20000 + i}"
            dsa = 1 if random.random() > 0.9 else 0  # Il 10% ha il DSA
            studenti.append((ID_CORRENTE, matricola, dsa))

            # 3. Iscrizione al Corso di Laurea
            corso_scelto = random.choice([1, 2, 3])
            corso_studente.append((ID_CORRENTE, corso_scelto))

            # 4. Assegnazione automatica a tutte le materie di quel corso
            for id_mat in corsi_materie[corso_scelto]:
                materia_studenti.append((ID_CORRENTE, id_mat, None))

                # 5. Simuliamo prenotazioni casuali agli appelli aperti (Appelli 1, 2, 3)
                if id_mat == 1 and random.random() > 0.6:  # 40% si prenota a Basi di dati
                    prenotazioni.append((ID_CORRENTE, 1))
                if id_mat == 2 and random.random() > 0.8:  # 20% si prenota a Prog Web
                    prenotazioni.append((ID_CORRENTE, 2))
                if id_mat == 3 and random.random() > 0.5:  # 50% si prenota ad Analisi
                    prenotazioni.append((ID_CORRENTE, 3))

            ID_CORRENTE += 1

        # GENERIAMO 15 PROFESSORI
        for i in range(1, 16):
            nome = random.choice(nomi)
            cognome = random.choice(cognomi)
            cf = f"PRF{nome[:2].upper()}{cognome[:2].upper()}{random.randint(10, 99)}X"
            email = f"{nome.lower()}.{cognome.lower()}@docenti.uni.it"

            utenti.append((ID_CORRENTE, nome, cognome, '1970-01-01', cf, email, 'prof123'))
            professori.append((ID_CORRENTE,))
            ID_CORRENTE += 1

        # GENERIAMO 5 TUTOR
        for i in range(1, 6):
            nome = random.choice(nomi)
            cognome = random.choice(cognomi)
            cf = f"TUT{nome[:2].upper()}{cognome[:2].upper()}{random.randint(10, 99)}Y"
            email = f"{nome.lower()}.{cognome.lower()}@tutor.uni.it"

            utenti.append((ID_CORRENTE, nome, cognome, '1998-01-01', cf, email, 'tutor123'))
            tutor.append((ID_CORRENTE,))
            ID_CORRENTE += 1

        # ESECUZIONE DELLE QUERY MASSIVE (Executemany garantisce prestazioni istantanee)
        cursore.executemany(
            "INSERT INTO Utente (ID_UTENTE, Nome, Cognome, Data_Nascita, COD_FISCALE, Email, Password) VALUES (?, ?, ?, ?, ?, ?, ?)",
            utenti)
        cursore.executemany("INSERT INTO Studente (ID_STUDENTE, Matricola, DSA) VALUES (?, ?, ?)", studenti)
        cursore.executemany("INSERT INTO Professore (ID_PROF) VALUES (?)", professori)
        cursore.executemany("INSERT INTO Tutor (ID_TUTOR) VALUES (?)", tutor)
        cursore.executemany("INSERT INTO Corso_Studente (COD_STUDENTE, COD_CORSO) VALUES (?, ?)", corso_studente)
        cursore.executemany("INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA, COD_GRUPPO) VALUES (?, ?, ?)",
                            materia_studenti)
        cursore.executemany("INSERT INTO Prenotazione (COD_STUDENTE, COD_APPELLO) VALUES (?, ?)", prenotazioni)

        connessione.commit()

        print("✅ Generazione completata! Database popolato con ~300 utenti collegati perfettamente.")
        print("\n--- CREDENZIALI DI ACCESSO RAPIDO ---")
        print("🧑‍🎓 Studente   ->  Email: studente  | Password: studente")
        print("👨‍🏫 Professore ->  Email: prof      | Password: prof")
        print("🎓 Tutor      ->  Email: tutor     | Password: tutor")
        print("🛡️ Admin      ->  Email: admin     | Password: admin")
        print(
            "\nLe altre decine di studenti generati hanno email nel formato: nome.cognome1@studenti.uni.it con password 'password123'")

    except sqlite3.Error as errore:
        print(f"❌ Ops, c'è stato un problema: {errore}")
    finally:
        cursore.close()
        connessione.close()


if __name__ == "__main__":
    reset_e_crea_database()