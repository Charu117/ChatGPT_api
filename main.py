from flask import Flask, redirect, request,render_template, jsonify, session # include the flask library 
from flask import Flask
from flask_session import Session
from flask_redmail import RedMail
import json
import pymysql
import openai,os

app = Flask(__name__) 

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Dichiarare la chiave segreta utlizzata per la sessione
app.secret_key = '12345'

# Definire la variabile d'ambiente chiamata <openai_key>
os.environ['openai_key'] = ""

# Assegnare la chiave api dichiarate come variabile d'ambiente al api_key di openai
openai.api_key = os.environ["openai_key"]

# crea una connessione al database MySQL utilizzando la libreria Python PyMySQL
def connection():
    s = 'localhost' #server(host) name 
    d = 'Ripetizioni' 
    u = 'admin' #login user
    p = 'charu2001' #login password 
    conn = pymysql.connect(host=s, user=u, password=p, database=d)
    return conn

# L'annotazione @app.route('/') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'index.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.
@app.route('/')
def index():
   return render_template('index.html')

# L'annotazione @app.route('/home') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'home.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/home')
def home():
   if not session.get('username') :
      return redirect('/')
   return render_template('home.html')

# L'annotazione @app.route('/registra') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'registra.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/registra')
def registra():
   if session.get('username') == True:
      session.pop('username', default=None)
      return redirect('/')
   return render_template('registra.html')

# L'annotazione @app.route('/login') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'login.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/login')
def login():
   if session.get('username') == True:
      session.pop('username', default=None)
      return redirect('/')
   return render_template('login.html')

# L'annotazione @app.route('/materie') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'materie.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/materie')
def form():
   if not session.get('username') :
      return redirect('/')
   return render_template('materie.html')

# L'annotazione @app.route('/search') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'search.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.
@app.route('/search')
def search():
   if not session.get('username') :
      return redirect('/')
   return render_template('search.html')

# L'annotazione @app.route('/dashboard') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'dashboard.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/dashboard')
def dashboard():
   return render_template('dashboard.html')

# L'annotazione @app.route('/dashboardMenu') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'dashboardmenu.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.
@app.route('/dashboardMenu')
def dMenu():
   return render_template('dashboardmenu.html')

@app.route('/allQuestions')
def materieAdmin():
   return render_template('materieAdmin.html')

# Questa funzione restituisce il nome dell'utente corrente, che può essere un amministratore o un utente normale, prendendo il nome utente dalla sessione dell'utente e cercando il corrispondente nome nell'elenco degli utenti del database. 
# La funzione restituisce il nome dell'utente come una risposta JSON.
@app.route('/getCurrentUser')
def getCurrentUser():
   user = ""
   if session.get('adminUser') == True:
      user = session['adminUser']
   else:
      user = session['username']
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute('SELECT nome FROM utente WHERE email=%s', (user,))

   row = mycursor.fetchone()
   conn.close()
   return jsonify(row[0])

# Questa funzione riceve una richiesta POST contenente una domanda dell'utente e restituisce una risposta generata automaticamente utilizzando l'API di OpenAI. 
# La funzione utilizza il modello "text-davinci-002" per generare la risposta e restituisce la risposta come una risposta JSON.

@app.route('/sendData', methods= ['POST'])
def process():
  question = request.form['question']
  response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=question,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
   )

  return jsonify(response.choices[0].text.strip())

# Questa funzione riceve una richiesta POST contenente i dati di un nuovo utente da inserire nel database. 
# La funzione controlla e verifica  se l'utente esiste già nel database confrontando la password fornita con quella memorizzata nel database. Se l'utente esiste già, la funzione restituisce "NotLogged". Altrimenti, la funzione inserisce i dati dell'utente nel database e restituisce "Success". 
# La funzione utilizza anche la variabile di sessione "username" per memorizzare l'email dell'utente appena creato.
# Naturalmente, il commento dovrebbe essere adattato alle esigenze specifiche dell'applicazione.
@app.route('/insertUser', methods=['POST'])
def insertUser():
   nome = request.form['nome'].rstrip()
   cognome = request.form['cognome'].rstrip()
   email = request.form['email'].rstrip()
   password = request.form['password'].rstrip()

   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute('SELECT password FROM utente WHERE email=%s', (email,))
   row = mycursor.fetchone()

   if row and row[0] == password:
      conn.close()
      return "NotLogged"
   else:
      mycursor.execute('INSERT INTO utente VALUES (NULL, %s, %s,%s, %s, (SELECT idP FROM Profilo WHERE tipoProfilo=%s))',(nome,cognome,email,password, "Studente"))
      conn.commit()
      conn.close()
      session['username'] = email
      return "Success"

# Questa funzione riceve una richiesta POST contenente l'email e la password di un utente da verificare. La funzione cerca l'email fornita nel database e confronta la password fornita con quella memorizzata nel database. Se l'utente esiste e la password corrisponde, la funzione imposta la variabile di sessione "username" con l'email dell'utente e restituisce "Verified". 
# Altrimenti, la funzione restituisce "NotLogged".
@app.route('/verifyUser', methods=['POST'])
def verifyUser():
   email = request.form['email'].rstrip()
   password = request.form['password'].rstrip()

   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute('SELECT password FROM utente WHERE email=%s', (email,))
   row = mycursor.fetchone()
   session['username'] = email
   conn.close()
   if row and row[0] == password:
      return "Verified"
   else:
      return "NotLogged"

# Questa funzione riceve una richiesta POST contenente l'email e la password di un utente amministratore da verificare. 
# La funzione cerca l'email fornita nel database e confronta la password fornita con quella memorizzata nel database. 
# Se l'utente esiste e la password corrisponde, la funzione imposta la variabile di sessione "username" con l'email dell'utente e restituisce "Verified". 
# Altrimenti, la funzione restituisce "NotLogged".
@app.route('/verifyAdmin', methods=['POST'])   
def verifyAdmin():
   email = request.form['email'].rstrip()
   password = request.form['password'].rstrip()

   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute('SELECT password FROM utente, Profilo WHERE utente.profilo=Profilo.idP AND tipoProfilo=%s AND utente.email=%s', ("admin",email))
   row = mycursor.fetchone()
   session['adminUser'] = email
   conn.close()
   if row and row[0] == password:
      return "Verified"
   else:
      return "NotLogged"

# Questa funzione restituisce tutte le materie disponibili nel database come un oggetto JSON. 
# La funzione esegue una query per selezionare tutte le materie dal database e crea un oggetto JSON contenente l'ID e il nome della materia. 
# La funzione restituisce l'oggetto JSON che contiene i risultati della query.
@app.route('/materieUda')
def materieUda():
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT * FROM Materia")
   rows = mycursor.fetchall()
   result = []
   for row in rows:
      d = {}
      d['idM'] = row[0]
      d['nomeMateria'] = row[1]
      result.append(d)
   json_result = json.dumps(result)
   return jsonify(json_result)

# Questa funzione restituisce tutte le Unità di Apprendimento (Uda) associate alla materia specificata come parametro. 
# La funzione riceve come input il nome della materia, esegue una query SQL per selezionare le Uda associate alla materia e restituisce un oggetto JSON che contiene i risultati della query. 
@app.route('/getUda', methods=['POST'])
def getUda():
   uda = request.form['uda']
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT idUda, nomeUda FROM Uda, Materia WHERE Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (uda))
   rows = mycursor.fetchall()
   result = []
   for row in rows:
      d = {}
      d['idUda'] = row[0]
      d['nomeUda'] = row[1]
      result.append(d)
   json_result = json.dumps(result)
   return jsonify(json_result)

# l'inserimento di una nuova domanda nel database.
@app.route('/newDomanda', methods=['POST'])
def insertDomanda():
   username = session['username']
   uda = (request.form['uda'])
   question = request.form['question'].rstrip()
   answer = request.form['answer'].rstrip()
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute('INSERT INTO Domande VALUES ((SELECT idU FROM utente WHERE email=%s), (SELECT idUda FROM Uda WHERE Uda.idUda=%s), %s, %s)',(username, uda, question,answer))
   conn.commit()
   conn.close()
   return "Done"

# estrarre tutte le domande in base alla materia e l'uda
@app.route('/getAllQuestions', methods=['POST'])
def getAllQuestions():
   materia = request.form['materia']
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT Uda.idUda, domanda, risposta, nomeUda Uda FROM Domande,utente,Uda,Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (materia))
   rows = mycursor.fetchall()
   result = []

   for row in rows:
      d = {}
      d['idUda'] = row[0]
      d['domanda'] = row[1]
      d['risposta'] = row[2]
      d['Uda'] = row[3]
      result.append(d)

   json_result = json.dumps(result)
   return jsonify(json_result)

# estrarre tutte le domande in base alla materia e l'uda che un utente ha fatto

@app.route('/getDomandeRis', methods=['POST'])
def getDomande():
   materia = request.form['materia']
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT Uda.idUda, domanda, risposta, nomeUda Uda FROM Domande,utente,Uda,Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND utente.email=%s AND Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (session['username'],materia))
   rows = mycursor.fetchall()
   result = []

   for row in rows:
      d = {}
      d['idUda'] = row[0]
      d['domanda'] = row[1]
      d['risposta'] = row[2]
      d['Uda'] = row[3]
      result.append(d)

   json_result = json.dumps(result)
   return jsonify(json_result)

@app.route('/searchWord', methods=['POST'])
def searchWord():
   word = '%' + request.form['word'] + '%'
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT Domande.idUda, domanda, risposta, nomeUda, Materia.nomeMateria FROM Domande,utente,Uda, Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND utente.email=%s AND Uda.fk_materia=Materia.idM GROUP BY domanda, risposta, nomeUda, Domande.idUda, Materia.nomeMateria HAVING domanda LIKE %s OR risposta LIKE %s", (session['username'],word,word))
   rows = mycursor.fetchall()
   result = []

   for row in rows:
      d = {}
      d['idUda'] = row[0]
      d['domanda'] = row[1]
      d['risposta'] = row[2]
      d['Uda'] = row[3]
      d['materia'] = row[4]
      result.append(d)

   json_result = json.dumps(result)
   return jsonify(json_result)

@app.route('/getChartData')
def sendChartData():
   conn = connection()
   mycursor = conn.cursor()
   mycursor.execute("SELECT nomeMateria, COUNT(nomeMateria) conteggio FROM Domande,Uda,Materia WHERE Domande.idUda=Uda.idUda AND Uda.fk_materia=Materia.idM GROUP BY Materia.nomeMateria")
   rows = mycursor.fetchall()
   result = []

   for row in rows:
      d = {}
      d['materia'] = row[0]
      d['conteggio'] = row[1]
      result.append(d)

   json_result = json.dumps(result)
   return jsonify(json_result)
  
@app.route('/logOut')
def deleteSession():
   session.pop('username', default=None)
   return redirect('/')

@app.route('/logOutAdmin')
def deleteSessionAdmin():
   session.pop('userAdmin', default=None)
   return redirect('/')

if __name__ == '__main__': 
   app.run(port=5000, debug=True) # application will start listening for web request on port 5000
