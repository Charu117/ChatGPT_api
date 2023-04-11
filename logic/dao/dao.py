import pymysql

class Dao:
    def getConnection(self):
        self.server = 'localhost' #server(host) name 
        self.db = 'Ripetizioni' 
        self.username = 'admin' #login user
        self.passwd = 'charu2001' #login password 
        conn = pymysql.connect(host=self.server, user=self.username, password=self.passwd, database=self.db)
        return conn 