import pytest
from unittest.mock import patch, MagicMock

# Importiamo le classi dal package database
from database.professore import Professore
from database.studente import Studente
from database.tutor import Tutor


# ==========================================
# TEST CLASSE PROFESSORE
# ==========================================
class TestProfessore:
    @patch('database.professore.sqlite3.connect')
    def test_get_corsi_assegnati(self, mock_connect):
        # 1. Setup Mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # 2. Dati fittizi dal DB
        mock_cursor.fetchall.return_value = [
            (1, "Ingegneria Informatica"),
            (3, "Ingegneria Elettronica")
        ]

        # 3. Esecuzione
        prof = Professore(id_utente=3, nome="Mario", cognome="Rossi")
        risultato = prof.get_corsi_assegnati()

        # 4. Asserts (usando assert nativo di pytest)
        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args
        query = args[0]

        assert "SELECT c.ID_CORSO, c.Nome" in query
        assert len(risultato) == 2
        assert risultato[0]["nome"] == "Ingegneria Informatica"


# ==========================================
# TEST CLASSE STUDENTE
# ==========================================
class TestStudente:
    @patch('database.studente.sqlite3.connect')
    def test_iscrivi_materia_successo(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        studente = Studente(id_utente=10, nome="Luca", cognome="Bianchi", matricola="S123", dsa=False)
        esito = studente.iscrivi_materia(id_materia=5)

        assert esito is True
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO Materia_Studenti (COD_STUDENTE, COD_MATERIA) VALUES (?, ?)",
            (10, 5)
        )
        mock_conn.commit.assert_called_once()

    @patch('database.studente.sqlite3.connect')
    def test_get_materie_disponibili(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (101, "Sistemi Operativi", 2, 9, "Verdi", "2026-07-20")
        ]

        studente = Studente(id_utente=10, nome="Luca", cognome="Bianchi", matricola="S123", dsa=False)
        risultato = studente.get_materie_disponibili()

        mock_cursor.execute.assert_called_once()
        assert len(risultato) == 1
        assert risultato[0]["id_materia"] == 101
        assert risultato[0]["professore"] == "Prof. Verdi"


# ==========================================
# TEST CLASSE TUTOR
# ==========================================
class TestTutor:
    @patch('database.tutor.sqlite3.connect')
    def test_get_materie_tutor(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value.__enter__.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        mock_cursor.fetchall.return_value = [
            (20, "Reti di Calcolatori", "Ingegneria Informatica")
        ]

        tutor = Tutor(id_utente=7, nome="Anna", cognome="Neri")
        risultato = tutor.get_materie_tutor()

        mock_cursor.execute.assert_called_once()
        args, _ = mock_cursor.execute.call_args

        assert "SELECT m.ID_MATERIA, m.Nome, c.Nome AS NomeCorso" in args[0]
        assert len(risultato) == 1
        assert risultato[0]["nome_materia"] == "Reti di Calcolatori"