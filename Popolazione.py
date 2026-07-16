import sqlite3


def reset_e_crea_database():
    print("Inizio il reset e la creazione del database...")

    connessione = sqlite3.connect('GestioneUniversita.db')
    cursore = connessione.cursor()

    cursore.execute("PRAGMA foreign_keys = ON;")

    script_sql = """
                 -- 1. DROP DELLE TABELLE VECCHIE (Ordine inverso rispetto alla creazione)
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

                 -- 2. CREAZIONE DELLE TABELLE AGGIORNATE
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

                 -- TABELLA APPELLO AGGIORNATA (Campo Gruppo aggiunto qui)
                 CREATE TABLE Appello (
                                          ID_APPELLO INTEGER PRIMARY KEY AUTOINCREMENT,
                                          Data DATE NOT NULL,
                                          Ora_Inizio TIME,
                                          Ora_Fine TIME,
                                          Descrizione TEXT,
                                          Gruppo BOOLEAN DEFAULT FALSE,
                                          COD_MATERIA INTEGER,
                                          COD_AULA_APPELLO INTEGER,
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

                 -- TABELLA LIBRETTO AGGIORNATA (Campo Gruppo rimosso)
                 CREATE TABLE Libretto (
                                           ID_Libretto INTEGER PRIMARY KEY AUTOINCREMENT,
                                           Voto INTEGER,
                                           COD_STUDENTE INTEGER,
                                           COD_APPELLO INTEGER,
                                           FOREIGN KEY (COD_STUDENTE) REFERENCES Studente(ID_STUDENTE) ON DELETE CASCADE,
                                           FOREIGN KEY (COD_APPELLO) REFERENCES Appello(ID_APPELLO) ON DELETE CASCADE
                 );

                 -- 3. INSERIMENTO DATI DI PROVA
                 INSERT INTO Utente (Nome, Cognome, Data_Nascita, COD_FISCALE, Email, Password) VALUES
                                                                                                    ('Mario', 'Rossi', '2001-05-15', 'RSSMRA01E15H501A', 'mario.rossi@studenti.uni.it', 'password123'),
                                                                                                    ('Giulia', 'Bianchi', '2002-03-22', 'BNCGLI02C22F205Z', 'giulia.bianchi@studenti.uni.it', 'password123'),
                                                                                                    ('Alan', 'Turing', '1912-06-23', 'TRNALN12H23Z404X', 'alan.turing@uni.it', 'enigma456'),
                                                                                                    ('Ada', 'Lovelace', '1815-12-10', 'LVLADA15T10Z404Y', 'ada.lovelace@tutor.uni.it', 'engine789'),
                                                                                                    ('Admin', 'Superiore', '1980-01-01', 'ADMSPR80A01H501W', 'admin@uni.it', 'adminpwd');

                 INSERT INTO Studente (ID_STUDENTE, Matricola) VALUES (1, 'MAT10001'), (2, 'MAT10002');
                 INSERT INTO Professore (ID_PROF) VALUES (3);
                 INSERT INTO Tutor (ID_TUTOR) VALUES (4);
                 INSERT INTO Admin (ID_ADMIN) VALUES (5);

                 INSERT INTO Corso (Nome, Data_Creazione, Anno_Inizio, Anno_Fine) VALUES
                                                                                      ('Ingegneria Informatica', '2023-09-01', 2023, 2026),
                                                                                      ('Informatica Umanistica', '2023-09-01', 2023, 2026);

                 INSERT INTO Gruppo (Descrizione) VALUES ('Gruppo Progetto Basi di Dati'), ('Gruppo Studio Analisi');

                 INSERT INTO Aula_Appello (Nome, Capienza) VALUES ('Aula Magna', 250), ('Aula 101', 50);

                 INSERT INTO Materia (Nome, Numero_CFU, COD_PROFESSORE, Anno) VALUES
                                                                                  ('Basi di Dati', 9, 3, 2),
                                                                                  ('Programmazione Web', 6, 3, 2);

                 -- Inserimento Appelli aggiornato (Il campo "Gruppo" è TRUE per il primo, FALSE per il secondo)
                 INSERT INTO Appello (Data, Ora_Inizio, Ora_Fine, Descrizione, Gruppo, COD_MATERIA, COD_AULA_APPELLO) VALUES
                                                                                                                          ('2024-06-20', '09:00:00', '11:00:00', 'Appello Estivo Basi di Dati', TRUE, 1, 1),
                                                                                                                          ('2024-07-15', '14:00:00', '16:00:00', 'Appello Estivo Prog Web', FALSE, 2, 2);

                 INSERT INTO Corso_Studente (COD_STUDENTE, COD_CORSO) VALUES (1, 1), (2, 1);
                 INSERT INTO Corso_Professore (COD_PROFESSORE, COD_CORSO) VALUES (3, 1);
                 INSERT INTO Corso_Tutor (COD_TUTOR, COD_CORSO) VALUES (4, 1);
                 INSERT INTO Corso_Materia (COD_CORSO, COD_MATERIA) VALUES (1, 1), (1, 2);
                 INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA, COD_GRUPPO) VALUES (1, 1, 1), (2, 1, 1);

                 -- Inserimento Libretto aggiornato (Niente più TRUE/FALSE qui)
                 INSERT INTO Libretto (Voto, COD_STUDENTE, COD_APPELLO) VALUES (28, 1, 1), (30, 2, 1); \
                 """

    try:
        cursore.executescript(script_sql)
        connessione.commit()
        print("Tutto fatto! Database droppato, pulito e ricreato con la struttura corretta.")
    except sqlite3.Error as errore:
        print(f"Ops, c'è stato un problema: {errore}")
    finally:
        cursore.close()
        connessione.close()


if __name__ == "__main__":
    reset_e_crea_database()

