DROP TABLE IF EXISTS uzytkownik;
CREATE TABLE uzytkownik (
    id_uzytkownika serial PRIMARY KEY,
    nazwa_uzytkownika VARCHAR ( 50 ) UNIQUE NOT NULL,
    haslo CHAR(64) NOT NULL,
    typ_konta CHAR(1) NOT NULL 
);
