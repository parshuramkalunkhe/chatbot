from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo

import openai

openai.api_key = ""

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatbot" # add your mongo db connection string in my i am using local storage with chatbot database.

mongo = PyMongo(app)
@app.route("/")
def home():
    chatdata = mongo.db.chatdata.find({})
    myChatData = [chat for chat in chatdata]
    print(myChatData)
    return render_template("index.html", myChatData = myChatData)

@app.route("/api", methods=["GET", "POST"])
def qa():
   
    if request.method == "POST":
        print(request.json)
        question = request.json.get("input")
        chat = mongo.db.chatdata.find_one({"question": question})
        if chat:
            data = {"question": question, "result": f"{chat['answer']}"}
            return jsonify(data)
        else:
            response = openai.Completion.create(
                            model="text-davinci-003",
                            prompt=question,
                            temperature=1,
                            max_tokens=256,
                            top_p=1,
                            frequency_penalty=0,
                            presence_penalty=0
                        )
            data = {"question": question, "answer": response["choices"][0]["text"]}
            mongo.db.chatdata.insert_one({"question": question, "answer": response["choices"][0]["text"]})
            return jsonify(data)
    return jsonify(data)

app.run(debug=True)

