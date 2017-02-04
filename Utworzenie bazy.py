# -*- coding: utf-8 -*-

import sqlite3


db_path = 'piotrnurekkk.db'
conn = sqlite3.connect(db_path)

c = conn.cursor()
#
# Tabele
#
c.execute('''
          CREATE TABLE Ksiazka
          ( id INTEGER PRIMARY KEY,
            wpis_date DATE NOT NULL,
            grupa VARCHAR (100)
          )
          ''')
c.execute('''
          CREATE TABLE Wpisy
          ( name VARCHAR(100),
            nazwisko VARCHAR(100),
            numer NUMERIC NOT NULL,
            ulica VARCHAR(100),
            nrdomu VARCHAR(10),
            nrmieszkania VARCHAR(10),
            miasto VARCHAR(100),
            Ksiazka_id INTEGER,
           FOREIGN KEY(Ksiazka_id) REFERENCES Ksiazka(id),
           PRIMARY KEY (name, Ksiazka_id))
          ''')
