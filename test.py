# -*- coding: utf-8 -*-

import repository
import sqlite3
import unittest

db_path = 'piotrnurek.db'

class RepositoryTest(unittest.TestCase):

    def setUp(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Wpisy')
        c.execute('DELETE FROM Ksiazka')
        c.execute('''INSERT INTO Ksiazka (id, wpis_date, grupa) VALUES(1, 2016-01-01, 'Dyrektorzy')''')
        c.execute('''INSERT INTO Wpisy (name, nazwisko, numer, ulica, nrdomu, nrmieszkania, miasto, ksiazka_id) VALUES('Jan','Janowski','000000000','nowa','1','2','katowice',1)''')
        c.execute('''INSERT INTO Wpisy (name, nazwisko, numer, ulica, nrdomu, nrmieszkania, miasto, ksiazka_id) VALUES('Jan','Janowski','000000000','nowa','1','2','katowice',1)''')
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute('DELETE FROM Wpisy')
        c.execute('DELETE FROM Ksiazka')
        conn.commit()
        conn.close()

    def testGetByIdInstance(self):
        ksiazka = repository.KsiazkaRepository().getById(1)
        self.assertIsInstance(ksiazka, repository.Ksiazka, "Objekt nie jest klasy Ksiazka")

    def testGetByIdNotFound(self):
        self.assertEqual(repository.KsiazkaRepository().getById(22),
                None, "Powinno wyjść None")

    def testGetByIdWpisyLen(self):
        self.assertEqual(len(repository.KsiazkaRepository().getById(1).wpisy),
                2, "Powinno wyjść 2")

    def testDeleteNotFound(self):
        self.assertRaises(repository.RepositoryException,
                repository.KsiazkaRepository().delete, 22)



if __name__ == "__main__":
    unittest.main()
