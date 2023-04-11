from flask import json, jsonify
from logic.dao.dao import Dao

class QuizDao:
    connection = Dao()
    def saveQuiz(self, type, quiz, topic, uda):
        self.type = type
        self.quiz = quiz
        self.topic = topic
        self.uda = uda
        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        
        mycursor.execute('SELECT argomento FROM argomento WHERE argomento=%s', (self.topic,))
        row = mycursor.fetchone()

        if row and row[0] == "":
            mycursor.execute('INSERT INTO argomento VALUES (NULL,%s ,(SELECT idUda FROM Uda WHERE Uda.idUda=%s))',(self.topic, self.uda))
            conn.commit()

        if type == "multiChoice":
            for item in self.quiz:
                # Extract the question and answers
                question = item['domanda']
                answer1 = item['risposte'][0]
                answer2 = item['risposte'][1]
                answer3 = item['risposte'][2]
                correct_answer = item['risposta_corretta']
                
                mycursor.execute('INSERT INTO domande_del_quiz VALUES (NULL, %s, %s , (SELECT idA FROM argomento WHERE argomento.argomento=%s))',(question, self.type ,self.topic))
                conn.commit()
                if (answer1 == correct_answer):
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, TRUE, (SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer1, question))
                    conn.commit()
                else: 
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, FALSE, (SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer1, question))
                    conn.commit()
                if (answer2 == correct_answer):
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, TRUE ,(SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer2, question))
                    conn.commit()
                else:
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, FALSE, (SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer2, question))
                    conn.commit()
                if (answer3 == correct_answer):
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, TRUE ,(SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer3, question))
                    conn.commit()
                else:
                    mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, FALSE ,(SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer3, question))
                    conn.commit()

        if type == "vF":
            for item in self.quiz:
                # Extract the question and answers
                question = item['domanda']
                answer = item['risposta_corretta']

                mycursor.execute('INSERT INTO domande_del_quiz VALUES (NULL, %s, %s , (SELECT idA FROM argomento WHERE argomento.argomento=%s))',(question, self.type ,self.topic))
                conn.commit()
                
                mycursor.execute('INSERT INTO risposte VALUES (NULL, %s ,TRUE, (SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer, question))
                conn.commit()
                
        if type == "aperta":
            for item in self.quiz:
                # Extract the question and answers
                question = item['domanda']
                answer = item['risposta']

                mycursor.execute('INSERT INTO domande_del_quiz VALUES (NULL, %s, %s , (SELECT idA FROM argomento WHERE argomento.argomento=%s LIMIT 1))',(question, self.type ,self.topic))
                mycursor.execute('INSERT INTO risposte VALUES (NULL, %s, TRUE ,(SELECT idDQ FROM domande_del_quiz WHERE domanda=%s))',(answer, question))
        conn.commit()
        conn.close()
        return "done"
    
    def getTopicByUda(self, uda):
        self.uda = uda
        conn = self.connection.getConnection()
        mycursor = conn.cursor()

        mycursor.execute('SELECT idA, argomento FROM argomento, Uda WHERE Uda.idUda=%s', (self.uda,))
        rows = mycursor.fetchall()
        result = []

        for row in rows:
            d = {}
            d['idA'] = row[0]
            d['argomento'] = row[1]
            result.append(d)
        json_result = json.dumps(result)
        return jsonify(json_result)
    
    def getQuiz(self, topic, type):
        self.topic = topic
        self.type = type
        conn = self.connection.getConnection()
        mycursor = conn.cursor()
        result = ''

        if type == "multiChoice":
            query = '''SELECT domanda, risposta, flag_corretto
                    FROM domande_del_quiz JOIN risposte ON domande_del_quiz.idDQ = risposte.idDomanda
                    WHERE idArgomento = %s AND tipo = %s'''
            mycursor.execute(query, (self.topic, self.type))
            rows = mycursor.fetchall()
            
            result = []
            for row in rows:
                question_text = row[0]
                answer_text = row[1]
                is_correct = row[2]
                
                # Find the dictionary for the current question, or create a new one if it doesn't exist yet
                question_dict = next((q for q in result if q['domanda'] == question_text), None)
                if question_dict is None:
                    question_dict = {'domanda': question_text, 'risposte': [], 'risposta_corretta': ''}
                    result.append(question_dict)
                
                # Append the answer choice to the current question's 'risposte' list
                question_dict['risposte'].append(answer_text)
                
                # Set the current answer choice as the correct answer if applicable
                if is_correct:
                    question_dict['risposta_corretta'] = answer_text

        json_result = json.dumps(result)
        
        if type == "vF":
            query = '''SELECT domanda, risposta, flag_corretto
                    FROM domande_del_quiz JOIN risposte ON domande_del_quiz.idDQ = risposte.idDomanda
                    WHERE idArgomento = %s AND tipo = %s'''
            mycursor.execute(query, (self.topic, self.type))
            rows = mycursor.fetchall()
            
            result = []
            for row in rows:
                d = {}
                d['domanda'] = row[0]
                d['risposta'] = row[1]
                
                result.append(d)
                
        json_result = json.dumps(result)

        if type == "aperta":
            query = '''SELECT domanda, risposta, flag_corretto
                    FROM domande_del_quiz JOIN risposte ON domande_del_quiz.idDQ = risposte.idDomanda
                    WHERE idArgomento = %s AND tipo = %s'''
            mycursor.execute(query, (self.topic, self.type))
            rows = mycursor.fetchall()
            
            result = []
            for row in rows:
                d = {}
                d['domanda'] = row[0]
                d['risposta'] = row[1]
                
                result.append(d)
                
        json_result = json.dumps(result)

        return jsonify(json.loads(json_result))        
