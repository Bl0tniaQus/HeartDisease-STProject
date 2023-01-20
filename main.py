from flask import Flask, render_template
import psycopg2

def dbConnect():
    dbConnection = psycopg2.connect(host='localhost',database='heairt',user='postgres',password='postgres')
    return dbConnection


app = Flask(__name__)


@app.route('/')
def index():
	return render_template("index.html")
    
@app.route('/login')
def login():
	return render_template("logowanie.html")

if __name__ == "__main__":
    app.run(debug=True)

