# -*- coding: utf-8 -*-

import sqlite3
from datetime import datetime

#
# Ścieżka połączenia z bazą danych
#
db_path = 'piotrnurek.db'

#
# Wyjątek używany w repozytorium
#
class RepositoryException(Exception):
    def __init__(self, message, *errors):
        Exception.__init__(self, message)
        self.errors = errors


#
# Model danych
#
class Ksiazka():
    """Model pojedynczej faktury
    """
    def __init__(self, id, date=datetime.now(), grupa=(), wpisy=[]):
        self.id = id
        self.date = date
        self.grupa = grupa
        self.wpisy = wpisy

    def __repr__(self):
        return "<Ksiazka(id='%s', date='%s', items='%s')>" % (
                    self.id, self.date, self.wpisy
                )


class WpisItem():
    """Model pozycji na fakturze. Występuje tylko wewnątrz obiektu Ksiazka.
    """
    def __init__(self, name, nazwisko, numer, ulica, nrdomu, nrmieszkania, miasto):
        self.name = name
        self.nazwisko = nazwisko
        self.numer = numer
        self.ulica = ulica
        self.nrdomu = nrdomu
        self.nrmieszkania = nrmieszkania
        self.miasto = miasto

    def __repr__(self):
        return "<WpisItem(name='%s', nazwisko='%s', numer='%s', ulica='%s', nrdomu='%s', nrmieszkania='%s', miasto='%s')>" % (
                    self.name, str(self.nazwisko), str(self.numer), self.ulica, self.nrdomu, self.nrmieszkania, self.miasto
                )


#
# Klasa bazowa repozytorium
#
class Repository():
    def __init__(self):
        try:
            self.conn = self.get_connection()
        except Exception as e:
            raise RepositoryException('GET CONNECTION:', *e.args)
        self._complete = False

    # wejście do with ... as ...
    def __enter__(self):
        return self

    # wyjście z with ... as ...
    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def get_connection(self):
        return sqlite3.connect(db_path)

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

#
# repozytorium obiektow typu Ksiazka
#
class KsiazkaRepository(Repository):

    def add(self, ksiazka):
        """Metoda dodaje pojedynczą fakturę do bazy danych,
        wraz ze wszystkimi jej pozycjami.
        """
        try:
            c = self.conn.cursor()
            # zapisz nagłowek faktury
            # nazwisko = sum([item.nazwisko*item.numer for item in ksiazka.wpisy])
            c.execute('INSERT INTO Ksiazka (id, wpis_date, grupa) VALUES(?, ?, ?)',
                        (ksiazka.id, str(ksiazka.date), ksiazka.grupa)
                    )
            # zapisz pozycje faktury
            if ksiazka.wpisy:
                for wpisitem in ksiazka.wpisy:
                    try:
                        c.execute('INSERT INTO Wpisy (name, nazwisko, numer, ulica, nrdomu, nrmieszkania, miasto, ksiazka_id) VALUES(?,?,?,?,?,?,?,?)',
                                        (wpisitem.name, wpisitem.nazwisko, wpisitem.numer, wpisitem.ulica, wpisitem.nrdomu, wpisitem.nrmieszkania, wpisitem.miasto, ksiazka.id)
                                )
                    except Exception as e:
                        #print "item add error:", e
                        raise RepositoryException('error adding ksiazka item: %s, to ksiazka: %s' %
                                                    (str(wpisitem), str(ksiazka.id))
                                                )
        except Exception as e:
            #print "ksiazka add error:", e
            raise RepositoryException('error adding ksiazka %s' % str(ksiazka))

    def delete(self, ksiazka):
        """Metoda usuwa pojedynczą fakturę z bazy danych,
        wraz ze wszystkimi jej pozycjami.
        """
        try:
            c = self.conn.cursor()
            # usuń pozycje
            c.execute('DELETE FROM Wpisy WHERE ksiazka_id=?', (ksiazka.id,))
            # usuń nagłowek
            c.execute('DELETE FROM Ksiazka WHERE id=?', (ksiazka.id,))

        except Exception as e:
            #print "ksiazka delete error:", e
            raise RepositoryException('error deleting ksiazka %s' % str(ksiazka))

    def getById(self, id):
        """Get ksiazka by id
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM Ksiazka WHERE id=?", (id,))
            wpis_row = c.fetchone()
            ksiazka = Ksiazka(id=id)
            if wpis_row == None:
                ksiazka=None
            else:
                ksiazka.date = wpis_row[1]
                c.execute("SELECT * FROM Wpisy WHERE ksiazka_id=? order by name", (id,))
                wpis_items_rows = c.fetchall()
                items_list = []
                for item_row in wpis_items_rows:
                    item = WpisItem(name=item_row[0], nazwisko=item_row[1], numer=item_row[2], ulica=item_row[3], nrdomu=item_row[4], nrmieszkania=item_row[5], miasto=item_row[6])
                    items_list.append(item)
                ksiazka.wpisy=items_list
        except Exception as e:
            #print "ksiazka getById error:", e
            raise RepositoryException('error getting by id ksiazka_id: %s' % str(id))
        return ksiazka

    def update(self, ksiazka):
        """Metoda uaktualnia pojedynczą fakturę w bazie danych,
        wraz ze wszystkimi jej pozycjami.
        """
        try:
            # pobierz z bazy fakturę
            wpis_oryg = self.getById(ksiazka.id)
            if wpis_oryg != None:
                # faktura jest w bazie: usuń ją
                self.delete(ksiazka)
            self.add(ksiazka)

        except Exception as e:
            #print "ksiazka update error:", e
            raise RepositoryException('error updating ksiazka %s' % str(ksiazka))



if __name__ == '__main__':
    try:
        with KsiazkaRepository() as ksiazka_repository:
            ksiazka_repository.add(
                Ksiazka(id = 1, date = datetime.now(), grupa='Dyrektorzy',
                        wpisy = [
                            WpisItem(name = "Jan",   nazwisko = 'Janowski', numer = 111222333, ulica = 'zielona', nrdomu='10B', nrmieszkania='1', miasto='Ustka'),
                            WpisItem(name = "Adam",   nazwisko = 'Adamowski', numer = 222333444, ulica = 'biala', nrdomu='1B', nrmieszkania='2', miasto='Slupsk'),
                            WpisItem(name = "Alina",   nazwisko = 'Alinowicz', numer = 333444555, ulica = 'zolta', nrdomu='60', nrmieszkania='10', miasto='Grudziadz'),
                            WpisItem(name = "Piotr",   nazwisko = 'Piotrowski', numer = 444555666, ulica = 'wojewodzka', nrdomu='1', nrmieszkania='150', miasto='Warszawa'),
                            WpisItem(name = "Krystyna",   nazwisko = 'Krystynowicz', numer = 555666777, ulica = 'nowa', nrdomu='12', nrmieszkania='1', miasto='Lublin')
                        ]
                    )
                )
            ksiazka_repository.complete()
    except RepositoryException as e:
        print(e)

    print KsiazkaRepository().getById(1)

if __name__ == '__main__':
    try:
        with KsiazkaRepository() as ksiazka_repository:
            ksiazka_repository.add(
                Ksiazka(id = 2, date = datetime.now(), grupa='Kierownicy',
                        wpisy = [
                            WpisItem(name = "Michal",   nazwisko = 'Janowski', numer = 111222333, ulica = 'zielona', nrdomu='10B', nrmieszkania='1', miasto='Ustka'),
                            WpisItem(name = "Adam",   nazwisko = 'Babinicz', numer = 222333444, ulica = 'biala', nrdomu='1B', nrmieszkania='2', miasto='Slupsk'),
                            WpisItem(name = "Michalina",   nazwisko = 'Iksinski', numer = 333444555, ulica = 'zolta', nrdomu='60', nrmieszkania='10', miasto='Grudziadz'),
                            WpisItem(name = "Abelard",   nazwisko = 'Nowakowski', numer = 444555666, ulica = 'wojewodzka', nrdomu='1', nrmieszkania='150', miasto='Warszawa'),
                            WpisItem(name = "Ziemowit",   nazwisko = 'Klimczak', numer = 555666777, ulica = 'nowa', nrdomu='12', nrmieszkania='1', miasto='Lublin')
                        ]
                    )
                )
            ksiazka_repository.complete()
    except RepositoryException as e:
        print(e)

        print KsiazkaRepository().getById(2)

if __name__ == '__main__':
    try:
        with KsiazkaRepository() as ksiazka_repository:
            ksiazka_repository.add(
                Ksiazka(id = 3, date = datetime.now(), grupa='zarzad',
                        wpisy = [
                            WpisItem(name = "Michal",   nazwisko = 'Janowski', numer = 111222333, ulica = 'zielona', nrdomu='10B', nrmieszkania='1', miasto='Ustka'),
                            WpisItem(name = "Adam",   nazwisko = 'Babinicz', numer = 222333444, ulica = 'biala', nrdomu='1B', nrmieszkania='2', miasto='Slupsk'),
                            WpisItem(name = "Michalina",   nazwisko = 'Iksinski', numer = 333444555, ulica = 'zolta', nrdomu='60', nrmieszkania='10', miasto='Grudziadz'),
                            WpisItem(name = "Abelard",   nazwisko = 'Nowakowski', numer = 444555666, ulica = 'wojewodzka', nrdomu='1', nrmieszkania='150', miasto='Warszawa'),
                            WpisItem(name = "Ziemowit",   nazwisko = 'Klimczak', numer = 555666777, ulica = 'nowa', nrdomu='12', nrmieszkania='1', miasto='Lublin')
                        ]
                    )
                )
            ksiazka_repository.complete()
    except RepositoryException as e:
        print(e)

    print KsiazkaRepository().getById(3)


    try:
        with KsiazkaRepository() as ksiazka_repository:
            ksiazka_repository.update(
                Ksiazka(id = 1, date = datetime.now(), grupa='Dyrektorzy',
                        wpisy = [
                            WpisItem(name = "Jana",   nazwisko = 'Janowski', numer = 111222333, ulica = 'zielona', nrdomu='10B', nrmieszkania='1', miasto='Ustka'),
                            WpisItem(name = "Adama",   nazwisko = 'Adamowski', numer = 222333444, ulica = 'biala', nrdomu='1B', nrmieszkania='2', miasto='Slupsk'),
                            WpisItem(name = "Alina",   nazwisko = 'Alinowicz', numer = 333444555, ulica = 'zolta', nrdomu='60', nrmieszkania='10', miasto='Grudziadz'),
                            WpisItem(name = "Piotr",   nazwisko = 'Piotrowski', numer = 444555666, ulica = 'wojewodzka', nrdomu='1', nrmieszkania='150', miasto='Warszawa'),
                            WpisItem(name = "Krystyna",   nazwisko = 'Krystynowicz', numer = 555666777, ulica = 'nowa', nrdomu='12', nrmieszkania='1', miasto='Lublin')
                        ]
                    )
                )
            ksiazka_repository.complete()
    except RepositoryException as e:
        print(e)

    print KsiazkaRepository().getById(1)



    try:
        with KsiazkaRepository() as ksiazka_repository:
            ksiazka_repository.delete( Ksiazka(id = 2) )
            ksiazka_repository.complete()
    except RepositoryException as e:
        print(e)
