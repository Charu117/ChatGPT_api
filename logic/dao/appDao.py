from flask import jsonify
import json
from logic.dao.dao import Dao

class Subject:
    connection = Dao()
    def getAllSubjects(self):
        conn = self.connection.getConnection()
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
    
    def getUdaByName(self, materia):
        self.materia = materia
        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute("SELECT idUda, nomeUda FROM Uda, Materia WHERE Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (self.materia))
        rows = mycursor.fetchall()
        result = []
        for row in rows:
            d = {}
            d['idUda'] = row[0]
            d['nomeUda'] = row[1]
            result.append(d)
        json_result = json.dumps(result)
        return jsonify(json_result)
    
    def insertQuestion(self, email, uda, question, answer):
        self.email = email
        self.uda = uda
        self.question = question
        self.answer= answer

        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute('INSERT INTO Domande VALUES ((SELECT idU FROM utente WHERE email=%s), (SELECT idUda FROM Uda WHERE Uda.idUda=%s), %s, %s)',(self.email, self.uda, self.question, self.answer))
        conn.commit()
        conn.close()
        return "Done"
    
    def getAllQuestions(self, subject):
        self.subject = subject
        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute("SELECT Uda.idUda, domanda, risposta, nomeUda Uda FROM Domande,utente,Uda,Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (self.subject))
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
    
    def getQuestionsOfUser(self, email, subject):
        self.email = email
        self.subject = subject

        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute("SELECT Uda.idUda, domanda, risposta, nomeUda Uda FROM Domande,utente,Uda,Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND utente.email=%s AND Uda.fk_materia=Materia.idM AND Materia.nomeMateria=%s", (self.email,self.subject))
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

    def getChartData(self):
        conn = self.connection.getConnection()
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
    
    def search(self, email, word):
        self.email = email
        self.word = word

        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute("SELECT Domande.idUda, domanda, risposta, nomeUda, Materia.nomeMateria FROM Domande,utente,Uda, Materia WHERE Uda.idUda=Domande.idUda AND Domande.idU=utente.idU AND utente.email=%s AND Uda.fk_materia=Materia.idM GROUP BY domanda, risposta, nomeUda, Domande.idUda, Materia.nomeMateria HAVING domanda LIKE %s OR risposta LIKE %s", (self.email, self.word, self.word))
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