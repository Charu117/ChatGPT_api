from flask import jsonify
from logic.dao.dao import Dao

class UserDao:
    connection = Dao()

    def insert(self, name, surname, email,password):
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password
        self.type = "Studente"

        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute('SELECT password FROM utente WHERE email=%s', (self.email,))
        row = mycursor.fetchone()

        if row and row[0] == password:
            conn.close()
            return "NotLogged"
        else:
            mycursor.execute('INSERT INTO utente VALUES (NULL, %s, %s,%s, %s, (SELECT idP FROM Profilo WHERE tipoProfilo=%s))',(self.name,self.surname,self.email,self.password, self.type))
            conn.commit()
            conn.close()
            
            return "Success"
    
    def verify(self, email, password):
        self.email = email
        self.password = password
        conn = self.connection.getConnection()        
        mycursor = conn.cursor()
        mycursor.execute('SELECT password FROM utente WHERE email=%s', (self.email,))
        row = mycursor.fetchone()
        conn.close()
        if row and row[0] == self.password:
            return "Verified"
        else:
            return "NotLogged"
        
    def getByEmail(self, email):
        self.email = email
        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute('SELECT nome FROM utente WHERE email=%s', (self.email,))

        row = mycursor.fetchone()
        conn.close()
        return jsonify(row[0])
    
    def verifyAdmin(self, email, password):
        self.email = email
        self.password = password

        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        mycursor.execute('SELECT password FROM utente, Profilo WHERE utente.profilo=Profilo.idP AND tipoProfilo=%s AND utente.email=%s', ("admin",email))
        row = mycursor.fetchone()
        conn.close()
        if row and row[0] == password:
            return "Verified"
        else:
            return "NotLogged"
    