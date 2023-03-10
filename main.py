from flask import Flask, render_template, session, request, redirect, url_for
from flask_session import Session
from sklearn.neural_network import MLPRegressor
import joblib
import hashlib
import psycopg2

def dbConnect():
    dbConnection = psycopg2.connect(host='localhost',database='heairt',user='postgres',password='postgres')
    return dbConnection
def normalizuj(minv,maxv,x,norm_min=-1,norm_max=1):
	x = float(x)
	xnorm = (norm_max - norm_min) * (x - minv) / (maxv - minv) + norm_min
	return xnorm

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def index():
	return render_template("index.html")
    
@app.route('/tips')
def tips():
	return render_template("tips.html")
    
@app.route('/login')
def logowanie():
	
	if 'login' in session:
		return redirect("/")
	
	return render_template("logowanie.html")
@app.route("/form")
def formularz():
	return render_template("formularz.html")
		
@app.route('/logowanie_action', methods=["POST"])
def logowanie_action():
	if 'login' in session:
		return redirect("/")
	if request.method == "POST":
		login = request.form["login"]
		haslo = request.form["haslo"]
		if login=="" or haslo=="":
			msg = "Nie wszystkie pola zostały wypełnione"
		else:
			haslo = hashlib.sha256(haslo.encode('utf-8')).hexdigest()
			dbConnection = dbConnect()
			dbCursor = dbConnection.cursor()
			dbCursor.execute("SELECT id_uzytkownika, haslo FROM uzytkownik WHERE nazwa_uzytkownika = '{}'".format(login))
			haslo2 = dbCursor.fetchall()
			if len(haslo2)==0 or haslo!=haslo2[0][1]:
				msg = "Niepoprawne dane logowania"
			else:
				session['login'] = login
				session['userid'] = haslo2[0][0]
				return redirect("/")
		return render_template("logowanie.html", msg=msg)	
	return render_template("logowanie.html")
	
@app.route('/rejestracja')
def rejestracja():
	if 'login' in session:
		return redirect("/")
	return render_template("rejestracja.html")
	
@app.route('/rejestracja_action', methods=['POST'])
def rejestracja_action():
	if 'login' in session:
		return redirect("/")
	if request.method == "POST":
		login = request.form["nazwa_uzytkownika"]
		haslo = request.form["haslo"]
		haslo2 = request.form["haslo2"]	
		if haslo != haslo2:
			msg = "Hasła nie są takie same"
		elif login=="" or haslo=="" or haslo2=="":
			msg = "Nie wszystkie pola zostały wypełnione"
		else:
			dbConnection = dbConnect()
			dbCursor = dbConnection.cursor()
			dbCursor.execute("SELECT nazwa_uzytkownika FROM uzytkownik WHERE nazwa_uzytkownika = '{}';".format(login))
			check = dbCursor.fetchall()
			if len(check)!=0:
				msg = "Istnieje już użytkownik o podanej nazwie"
			else:
				haslo = hashlib.sha256(haslo.encode('utf-8')).hexdigest()
				dbCursor.execute("INSERT INTO uzytkownik VALUES (default, '{}', '{}', CURRENT_DATE);".format(login,haslo))
				dbConnection.commit()
				msg = "Konto utworzone prawidłowo"
			dbCursor.close()
			dbConnection.close()
	return render_template("rejestracja.html", msg=msg)
	
@app.route('/wyloguj')
def wyloguj():
	session.clear()
	return redirect("/")
	
@app.route('/form_extended', methods=["POST"])
def form_extended():
	if request.method == "POST":
		dane = [None]*12
		dane_pokazowe = [None] * 12
		err=False
		msg = ""
		wynik="Nie okkreślono"
		
		if request.form['plec'] == "0":
			plec = "Kobieta"
		else:
			plec = "Mężczyzna"
			
		if request.form['bol']=="0":
			bol = "Brak"
		elif request.form['bol']=="1":
			bol = "Angina"
		elif request.form['bol']=="2":
			bol = "Atypowa angina"
		elif request.form['bol']=="3":
			bol = "Ból nieanginowy"
		elif request.form['bol']=="4":
			bol = "Ból asymptomatyczny"
			
		if request.form['cukier']=="1":
			cukier = ">120mg/dl"
		else:
			cukier = "<120mg/dl"
		
		if request.form['ekg']=="0":
			ekg = "W normie"
		elif request.form['ekg']=="1":
			ekg = "Anomalie fali ST-T"
		else:
			ekg= "Hipertrofia"
		
		if request.form['bolw'] == "0":
			bolw = "Brak"
		else:
			bolw = "Występuje"
			
		if request.form['nachylenie']=="1":
			nachylenie = "W górę"
		elif request.form['nachylenie']=="2":
			nachylenie = "Płasko"
		else:
			nachylenie = "W dół"
		
		if request.form['talasemia'] == "3":
			talasemia = "Brak"
		elif request.form['talasemia'] == "6":
			talasemia = "Miejscowa niedokrwistość"
		else:
			talasemia = "Ogólna niedokrwistość"
		
		
		
		table = "<tr><td>Wiek: {}</td><td>Płeć: {}</td></tr>".format(request.form['wiek'], plec)
		table = table + "<tr><td>Ból klatki: {}</td><td>Ból klatki podczas wysiłku: {}</td></tr>".format(bol,bolw)
		table = table + "<tr><td>Wynik EKG: {}</td><td>Ciśnienie spoczynkowe: {}mmHg</td></tr>".format(ekg,int(request.form['cisnienie']))
		table = table + "<tr><td>Nachylenie ST: {}</td><td>Cholesterol całkowity: {}mg/dl</td></tr>".format(nachylenie,int(request.form['cholesterol']))
		table = table + "<tr><td>Różnica ST spoczynek/wysiłek: {}</td><td>Poziom cukru we krwi: {}</td></tr>".format(float(request.form['st']),cukier)
		table = table + "<tr><td>Talasemia: {}</td><td>Bicie serca (wysiłek): {}bpm</td></tr>".format(talasemia,int(request.form['bicieserca']))
		
		if int(request.form["wiek"])<18:
			msg+="<li>Podany wiek wynosi {} lat. Mając w takim wieku jakiekolwiek wątpliwości co do swojego stanu zdrowia zdecydowanie nie powinno się ich ignorować</li>".format(int(request.form["wiek"]))
			err=True
		if int(request.form["wiek"])>80:
			msg+="<li>Podany wiek wynosi {} lat. W takim wieku problemy zdrowotne mogą mieć bardzo dużo różnych źródeł, dlatego otrzymany wynik naszego testu mógłby być mylący</li>".format(int(request.form["wiek"]))
			err=True
		if int(request.form["cisnienie"])<94:
			msg+="<li>Ciśnienie skurczowe krwi w wysokości {} mmHg jest bardzo niską, niebezpieczną dla zdrowia wartością</li>".format(int(request.form["cisnienie"]))
			err=True
		if int(request.form["cisnienie"])>200:
			msg+="<li>Ciśnienie skurczowe krwi w wysokości {} mmHg jest niebezpieczną wartością, mogącą wskazywać na nadciśnienie</li>".format(int(request.form["cisnienie"]))
			err=True
		if int(request.form["cholesterol"])<120:
			msg+="<li>Poziom całkowitego cholesterolu we krwi wynoszący {} mg/dl jest poniżej wartości normalnej, co może być przejawem różnych chorób, nawet tych nie związanych bezpośrednio z układem krążenia </li>".format(int(request.form["cholesterol"]))
			err=True
		if int(request.form["cholesterol"])>600:
			msg+="<li>Poziom całkowitego cholesterolu we krwi wynoszący {} mg/dl jest skrajnie wysoki i niebezpieczny, który trzeba bezzwłocznie skonsultować</li>".format(int(request.form["cholesterol"]))
			err=True
		if int(request.form["bicieserca"])<70:
			msg+="<li>Tempo bicia serca po wysiłku równe {} uderzeń na minutę jest nienaturalnie niskie nawet wśród osób wysportowanych i może z dużym prawdopodobieństwem wskazywać na problemy z układem krążenia</li>".format(int(request.form["bicieserca"]))	
			err=True
		if int(request.form["bicieserca"])>210:
			msg+="<li>Tempo bicia serca po wysiłku równe {} uderzeń na minutę jest wysokie niezależnie od wieku i zdecydowanie warto się pod tym kątem zdiagnozować u specjalisty</li>".format(int(request.form["bicieserca"]))	
			err=True
		if float(request.form["st"])>6.5:
			msg+="<li>Różnica długości odcinka ST pomiędzy stanem spoczynku a wysiłkiem wynosząca {} jest skrajnie nienaturalna i jest oznaką nieprawidłowej pracy serca</li>".format(float(request.form["st"]))	
			err=True

		if err==False:
			dane[0] = normalizuj(18,80,request.form["wiek"])
			dane[1] = normalizuj(0,1,request.form["plec"])
			dane[2] = normalizuj(0,4,request.form["bol"])
			dane[3] = normalizuj(90,200,request.form["cisnienie"])
			dane[4] = normalizuj(120,600,request.form["cholesterol"])
			dane[5] = normalizuj(1,2,request.form["cukier"])
			dane[6] = normalizuj(0,2,request.form["ekg"])
			dane[7] = normalizuj(70,210,request.form["bicieserca"])
			dane[8] = normalizuj(0,1,request.form["bolw"])
			dane[9] = normalizuj(0,6.5,request.form["st"])
			dane[10] = normalizuj(1,3,request.form["nachylenie"])
			dane[11] = normalizuj(3,7,request.form["talasemia"])
			network = joblib.load('static/network_extended.ptk')
			result = network.predict([dane])
			if result>=0 and result<0.25:
				wynik = '<span style="color:#5ad449;">Niskie</span>'
			if result>=0.25 and result<0.50:
				wynik = '<span style="color:#d1dc0c;">Podwyższone</span>'
			if result>=0.50 and result<0.75:
				wynik = '<span style="color:#ef662b;">Wysokie</span>'
			if result>=0.75 and result<=1:
				wynik = '<span style="color:#e02d2d;">Bardzo wysokie</span>'
		table = "<tr><td>Test rozszerzony</td><td>Ryzyko choroby: {}</td></tr>".format(wynik) + table
		return render_template("wynik.html", msg=msg,table=table, wynik=wynik)
	return redirect("/form")
	
@app.route('/form_simplified', methods=["POST"])
def form_simplified():
	if request.method == "POST":
		dane = [None]*8
		err=False
		msg = ""
		wynik="Nie okkreślono"
		
		if request.form['plec'] == "0":
			plec = "Kobieta"
		else:
			plec = "Mężczyzna"
		if request.form['bol']=="0":
			bol = "Brak"
		elif request.form['bol']=="1":
			bol = "Angina"
		elif request.form['bol']=="2":
			bol = "Atypowa angina"
		elif request.form['bol']=="3":
			bol = "Ból nieanginowy"
		elif request.form['bol']=="4":
			bol = "Ból asymptomatyczny"
			
		if request.form['cukier']=="1":
			cukier = ">120mg/dl"
		else:
			cukier = "<120mg/dl"
		
		if request.form['bolw'] == "0":
			bolw = "Brak"
		else:
			bolw = "Występuje"
			
		table = "<tr><td>Wiek: {}</td><td>Płeć: {}</td></tr>".format(request.form['wiek'], plec)
		table = table + "<tr><td>Ból klatki: {}</td><td>Ból klatki podczas wysiłku: {}</td></tr>".format(bol,bolw)
		table = table + "<tr><td>Cholesterol całkowity ~{}</td><td>Bicie serca (wysiłek): {}bpm</td></tr>".format(int(request.form['cholesterol']),int(request.form['bicieserca']))
		table = table + "<tr><td>Poziom cukru we krwi: {}</td><td>Ciśnienie spoczynkowe: ~{}mmHg</td></tr>".format(cukier,int(request.form['cisnienie']))
		
		if int(request.form["wiek"])<18:
			msg+="<li>Podany wiek wynosi {} lat. Mając w takim wieku jakiekolwiek wątpliwości co do swojego stanu zdrowia zdecydowanie nie powinno się ich ignorować</li>".format(int(request.form["wiek"]))
			err=True
		if int(request.form["wiek"])>80:
			msg+="<li>Podany wiek wynosi {} lat. W takim wieku problemy zdrowotne mogą mieć bardzo dużo różnych źródeł, dlatego otrzymany naszego wynik mógłby być mylący</li>".format(int(request.form["wiek"]))
			err=True
			
		
				
		if err==False:
			dane[0] = normalizuj(18,80,request.form["wiek"])
			dane[1] = normalizuj(0,1,request.form["plec"])
			dane[2] = normalizuj(0,4,request.form["bol"])
			dane[3] = normalizuj(90,200,request.form["cisnienie"])
			dane[4] = normalizuj(120,600,request.form["cholesterol"])
			dane[5] = normalizuj(1,2,request.form["cukier"])
			dane[6] = normalizuj(70,210,request.form["bicieserca"])
			dane[7] = normalizuj(0,1,request.form["bolw"])

			network = joblib.load('static/network_simplified.ptk')
			result = network.predict([dane])
			
			if result>=0 and result<0.25:
				wynik = '<span style="color:#5ad449;">Niskie</span>'
			if result>=0.25 and result<0.50:
				wynik = '<span style="color:#d1dc0c;">Podwyższone</span>'
			if result>=0.50 and result<0.75:
				wynik = '<span style="color:#ef662b;">Wysokie</span>'
			if result>=0.75 and result<=1:
				wynik = '<span style="color:#e02d2d;">Bardzo wysokie</span>'
		table = "<tr><td>Test podstawowy</td><td>Ryzyko choroby: {}</td></tr>".format(wynik) + table
		return render_template("wynik.html", msg=msg, wynik=wynik,table=table)
	return redirect("/form")	
@app.route('/dodaj_wynik', methods=["POST"])
def dodaj_wynik():
	if request.method == "POST" and 'userid' in session:
		tytul = request.form["tytul"][0:29]
		opis = request.form["opis"][0:249]
		tresc = request.form["tresc"]
		userid = request.form['userid']
		dbConnection = dbConnect()
		dbCursor = dbConnection.cursor()
		dbCursor.execute("INSERT INTO wynik VALUES (default, {}, '{}', '{}', '{}', CURRENT_DATE)".format(int(userid), tytul, opis, tresc))
		dbConnection.commit()
		dbCursor.close()
		dbConnection.close()
	return redirect("/profil")		

@app.route('/wyniki')
def wyniki():
	
	if 'login' in session:
		
		dbConnection = dbConnect()
		dbCursor = dbConnection.cursor()
		dbCursor.execute("SELECT * FROM wynik WHERE wynik_id_uzytkownika = {} ORDER BY data_dodania,id_wyniku DESC".format(session['userid']))
		wyniki = dbCursor.fetchall()
		dbCursor.close()
		dbConnection.close()
		return render_template("wyniki_uzytkownika.html", wyniki = wyniki, dl = len(wyniki))
	return redirect("/")

@app.route('/usun_wpis', methods=["POST"])
def usun_wpis():
	if request.method == 'POST' and 'login' in session:
		id = request.form['delete']
		dbConnection = dbConnect()
		dbCursor = dbConnection.cursor()
		dbCursor.execute("DELETE FROM wynik WHERE id_wyniku = {}".format(int(id)))
		dbConnection.commit()
		dbCursor.close()
		dbConnection.close()
		return redirect("/wyniki")
	return redirect("/")	
@app.route("/profil")		
def profil():
	dbConnection = dbConnect()
	dbCursor = dbConnection.cursor()
	dbCursor.execute("SELECT data_dolaczenia FROM uzytkownik WHERE id_uzytkownika = {}".format(session['userid']))
	session['data_dolaczenia'] = dbCursor.fetchall()[0][0]
	dbCursor.execute("SELECT count(*) FROM wynik WHERE wynik_id_uzytkownika = {}".format(session['userid']))
	session['count']  = dbCursor.fetchall()[0][0]
	dbCursor.close()
	dbConnection.close()
	return render_template("profil.html")
@app.route("/usun_konto", methods=["POST"])
def usun_konto():
	msg=""
	if 'userid' in session and request.method == "POST":
		dbConnection = dbConnect()
		dbCursor = dbConnection.cursor()
		dbCursor.execute("DELETE FROM wynik WHERE wynik_id_uzytkownika = {}".format(int(session['userid'])))
		dbCursor.execute("DELETE FROM uzytkownik WHERE id_uzytkownika = {}".format(int(session['userid'])))
		dbConnection.commit()
		dbCursor.close()
		dbConnection.close()
		return redirect("/wyloguj")
	return redirect("/")
@app.route("/zmiana_hasla", methods=["POST"])
def zmiana_hasla():
	if 'userid' in session and request.method =="POST":
		haslo_stare = request.form['haslo_stare']
		haslo_nowe = request.form['haslo_nowe']
		haslo_nowe2 = request.form['haslo_nowe2']
		dbConnection = dbConnect()
		dbCursor = dbConnection.cursor()
		dbCursor.execute("SELECT haslo FROM uzytkownik WHERE id_uzytkownika = {}".format(session['userid']))
		haslo = dbCursor.fetchall()[0][0]
		if (haslo_nowe != haslo_nowe2) or (haslo!=hashlib.sha256(haslo_stare.encode('utf-8')).hexdigest()):
			msg = "Hasła się nie zgadzają"
		else:
			if haslo_stare==haslo_nowe:
				msg="Nie można ustawić hasła na bieżące"
			else:
				haslo_zmieniane = hashlib.sha256(haslo_nowe.encode('utf-8')).hexdigest()
				dbCursor.execute("UPDATE uzytkownik SET haslo = '{}' WHERE id_uzytkownika = {}".format(haslo_zmieniane,session['userid']))
				print("UPDATE uzytkownik SET haslo = '{}' WHERE id_uzytkownika = {}".format(haslo_zmieniane,session['userid']))
				dbConnection.commit()
				msg = "Hasło zmienione pomyślnie"
		dbCursor.close()
		dbConnection.close()	
	return render_template("profil.html", haslo_msg=msg)	
if __name__ == "__main__":
    app.run(debug=True)
