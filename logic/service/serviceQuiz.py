from flask import jsonify, json
import openai,os

os.environ['openai_key'] = ""
openai.api_key = os.environ["openai_key"]

class QuizService:
    def generateQuiz(self, topic, quantity, type):
        self.topic = topic
        self.quantity = quantity
        self.type = type
        if self.type == "multiChoice":
            self.prompt = 'Genera un quiz in formato JSON in italiano sul tema di ' + self.topic + 'con' + self.quantity + ' domande a 3 risposte multiple e con la risposta corretta come il seguente: [{ "domanda": " ", "risposte": [ " ", " ", " " ], "risposta_corretta": " "}]'
        if self.type == "vF":
            self.prompt = 'Genera un quiz in formato JSON in italiano sul tema di ' + self.topic + 'con' + self.quantity + ' domande a vero o falso e e con la risposta corretta come il seguente: [{ "domanda": " ", "risposta_corretta": " "}]'
        if self.type == "aperta":
            self.prompt = 'Genera un quiz in formato JSON in italiano sul tema di ' + self.topic + 'con' + self.quantity + ' domande a risposta aperta come il seguente: [{ "domanda": " ", "risposta": " "}]'
        
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=self.prompt,
            max_tokens=1024,
            n=1,
            stop=None,
            temperature=0.7,
        )
        return jsonify(response.choices[0].text.strip())