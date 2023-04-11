from flask import Flask, redirect, request,render_template, jsonify, session # include the flask library 
from flask import Flask
from flask_session import Session
import json
import openai,os

from logic.dao.userDao import UserDao
from logic.dao.appDao import Subject
from logic.dao.quizDao import QuizDao
from logic.service.serviceQuiz import QuizService

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
user = UserDao()
subject = Subject()
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

# L'annotazione @app.route('/dashboard') indica che questa funzione gestirà le richieste all'URL principale del sito web. 
# restituisce il contenuto della pagina HTML 'dashboard.html' (si trova sulla cartella di templates) utilizzando il metodo 'render_template' fornito dal framework Flask.

@app.route('/dashboard')
def dashboard():
   return render_template('dashboard.html')

@app.route('/quiz')
def deployQuiz():
   return render_template('quiz.html')

@app.route('/quizStudent')
def deployQuizStudent():
   return render_template('quizStudent.html')

# Questa funzione restituisce il nome dell'utente corrente, che può essere un amministratore o un utente normale, prendendo il nome utente dalla sessione dell'utente e cercando il corrispondente nome nell'elenco degli utenti del database. 
# La funzione restituisce il nome dell'utente come una risposta JSON.
@app.route('/getCurrentUser')
def getCurrentUser():
   userEmail = ""
   if session.get('adminUser') == True:
      userEmail = session['adminUser']
   else:
      userEmail = session['username']

   return user.getByEmail(userEmail)

# Questa funzione riceve una richiesta POST contenente una domanda dell'utente e restituisce una risposta generata automaticamente utilizzando l'API di OpenAI. 
# La funzione utilizza il modello "text-davinci-002" per generare la risposta e restituisce la risposta come una risposta JSON.

@app.route('/sendData', methods= ['POST'])
def process():
  question = request.form['question']
  response = openai.Completion.create(
        engine="text-davinci-003",
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

   is_verified = user.insert(nome, cognome, email, password)

   if is_verified == "Success":
      session['username'] = email
   return is_verified

# Questa funzione riceve una richiesta POST contenente l'email e la password di un utente da verificare. La funzione cerca l'email fornita nel database e confronta la password fornita con quella memorizzata nel database. Se l'utente esiste e la password corrisponde, la funzione imposta la variabile di sessione "username" con l'email dell'utente e restituisce "Verified". 
# Altrimenti, la funzione restituisce "NotLogged".
@app.route('/verifyUser', methods=['POST'])
def verifyUser():
   email = request.form['email'].rstrip()
   password = request.form['password'].rstrip()

   is_verified = user.verify(email, password)

   if is_verified == "Verified":
      session['username'] = email
   return is_verified

# Questa funzione riceve una richiesta POST contenente l'email e la password di un utente amministratore da verificare. 
# La funzione cerca l'email fornita nel database e confronta la password fornita con quella memorizzata nel database. 
# Se l'utente esiste e la password corrisponde, la funzione imposta la variabile di sessione "username" con l'email dell'utente e restituisce "Verified". 
# Altrimenti, la funzione restituisce "NotLogged".
@app.route('/verifyAdmin', methods=['POST'])   
def verifyAdmin():
   email = request.form['email'].rstrip()
   password = request.form['password'].rstrip()

   return user.verifyAdmin(email, password)

# Questa funzione restituisce tutte le materie disponibili nel database come un oggetto JSON. 
# La funzione esegue una query per selezionare tutte le materie dal database e crea un oggetto JSON contenente l'ID e il nome della materia. 
# La funzione restituisce l'oggetto JSON che contiene i risultati della query.
@app.route('/materieUda')
def materieUda():
   return subject.getAllSubjects()

# Questa funzione restituisce tutte le Unità di Apprendimento (Uda) associate alla materia specificata come parametro. 
# La funzione riceve come input il nome della materia, esegue una query SQL per selezionare le Uda associate alla materia e restituisce un oggetto JSON che contiene i risultati della query. 
@app.route('/getUda', methods=['POST'])
def getUda():
   materia = request.form['materia']
   return subject.getUdaByName(materia)
   

# l'inserimento di una nuova domanda nel database.
@app.route('/newDomanda', methods=['POST'])
def insertDomanda():
   username = session['username']
   uda = (request.form['uda'])
   question = request.form['question'].rstrip()
   answer = request.form['answer'].rstrip()
   subject.insertQuestion(username, uda, question, answer)

# estrarre tutte le domande in base alla materia e l'uda
@app.route('/getAllQuestions', methods=['POST'])
def getAllQuestions():
   materia = request.form['materia']
   return subject.getAllQuestions(materia)


# estrarre tutte le domande in base alla materia e l'uda che un utente ha fatto

@app.route('/getDomandeRis', methods=['POST'])
def getDomande():
   materia = request.form['materia']
   return subject.getQuestionsOfUser(session['username'], materia)
   

@app.route('/searchWord', methods=['POST'])
def searchWord():
   word = '%' + request.form['word'] + '%'
   return subject.search(session['username'], word)
   

@app.route('/getChartData')
def sendChartData():
   return subject.getChartData()

@app.route('/newQuiz', methods=['POST'])
def newQuiz():
   topic = request.form['topic']
   quantity = request.form['quantity']
   type = request.form['type']

   quizS = QuizService()
   return quizS.generateQuiz(topic, quantity, type)

@app.route('/saveQuiz', methods=['POST'])
def saveQuiz():
   type = request.form['type']
   topic = request.form['topic']
   uda = request.form['uda']
   answer = json.loads(request.form['quiz'])

   quiz = QuizDao()

   return quiz.saveQuiz(type ,answer, topic, uda)   

@app.route('/getTopic', methods=['POST'])
def getTopic():
   uda = request.form['uda']

   quiz = QuizDao()
   return quiz.getTopicByUda(uda)   

@app.route('/getQuiz', methods=['POST'])
def getQuiz():
   uda = request.form['uda']
   type = request.form['type']
   quiz = QuizDao()
   return quiz.getQuiz(uda, type)   


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