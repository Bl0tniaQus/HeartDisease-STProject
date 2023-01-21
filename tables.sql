DROP TABLE IF EXISTS uzytkownik CASCADE;
DROP TABLE IF EXISTS wynik;
CREATE TABLE uzytkownik (
    id_uzytkownika serial PRIMARY KEY,
    nazwa_uzytkownika VARCHAR ( 50 ) UNIQUE NOT NULL,
    haslo CHAR(64) NOT NULL,
    data_dolaczenia DATE NOT NULL
);
CREATE TABLE wynik (
    id_wyniku serial PRIMARY KEY,
    wynik_id_uzytkownika INTEGER NOT NULL,
    tytul VARCHAR(30) NOT NULL,
    opis VARCHAR(250),
	content VARCHAR(600) NOT NULL,
    data_dodania DATE NOT NULL,
    CONSTRAINT fk_wynik FOREIGN KEY(wynik_id_uzytkownika) REFERENCES uzytkownik(id_uzytkownika)
);
