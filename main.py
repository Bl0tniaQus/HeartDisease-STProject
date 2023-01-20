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
    
@app.route('/login')
def logowanie():
	
	if 'login' in session:
		return redirect("/")
	
	return render_template("logowanie.html")
@app.route("/form")
def formularz():
	wynik=""
	if 'wynik' in session:
		wynik=session['wynik']
		session.pop('wynik')
	return render_template("formularz.html",wynik=wynik)
		
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
			dbCursor.execute("SELECT haslo FROM uzytkownik WHERE nazwa_uzytkownika = '{}'".format(login))
			haslo2 = dbCursor.fetchall()
			if len(haslo2)==0 or haslo!=haslo2[0][0]:
				msg = "Niepoprawne dane logowania"
			else:
				session['login'] = login
				print("zalogowano jako ",session['login'])
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
				dbCursor.execute("INSERT INTO uzytkownik VALUES (default, '{}', '{}', 0);".format(login,haslo))
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
		bounds = joblib.load('static/boundsext.ptk')
		
		result = normalizuj(bounds[0],bounds[1],network.predict([dane]),0,1)
		if result>=0 and result<25:
			wynik = "Niskie"
		if result>=25 and result<50:
			wynik = "Podwyższone"
		if result>=50 and result<75:
			wynik = "Duże"
		if result>=75 and result<=100:
			wynik = "Bardzo duże"
		session['wynik'] = wynik
	return redirect("/form")	
	
if __name__ == "__main__":
    app.run(debug=True)


		
