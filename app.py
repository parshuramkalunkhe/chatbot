from flask import Flask, render_template, jsonify, request
from flask_pymongo import PyMongo
import openai
import time

openai.api_key = ""

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatbot"

mongo = PyMongo(app)

class RateLimiter:
    def __init__(self, max_requests, time_window):
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = max_requests
        self.last_refill_time = time.time()

    def get_tokens(self):
        now = time.time()
        if now - self.last_refill_time > self.time_window:
            self.tokens = self.max_requests
            self.last_refill_time = now
        return self.tokens

    def consume_token(self):
        tokens = self.get_tokens()
        if tokens > 0:
            self.tokens -= 1
            return True
        else:
            return False

limiter = RateLimiter(max_requests=10, time_window=60)  # 10 requests per minute

# Cache to store previously generated responses
response_cache = {}

@app.route("/")
def home():
    chatdata = mongo.db.chatdata.find({})
    myChatData = [chat for chat in chatdata]
    print(myChatData)
    return render_template("index.html", myChatData=myChatData)

@app.route("/api", methods=["GET", "POST"])
def qa():
    if request.method == "POST":
        print(request.json)
        question = request.json.get("input")
        chat = mongo.db.chatdata.find_one({"question": question})
        if chat:
            data = {"question": question, "result": f"{chat['answer']}"}
            print(data)
            return jsonify(data)
        else:
            if question in response_cache:
                # If the response is cached, retrieve it from the cache
                data = {"question": question, "answer": response_cache[question]}
                mongo.db.chatdata.insert_one({"question": question, "answer": response_cache[question]})
                return jsonify(data)
            elif limiter.consume_token():
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=question,
                    temperature=1,
                    max_tokens=256,
                    top_p=1,
                    frequency_penalty=0,
                    presence_penalty=0
                )
                answer = response["choices"][0]["text"]
                response_cache[question] = answer  # Cache the response
                data = {"question": question, "answer": answer}
                mongo.db.chatdata.insert_one({"question": question, "answer": answer})
                return jsonify(data)
            else:
                data = {"error": "Rate limit exceeded. Please try again later."}
                return jsonify(data), 429  # Return 429 status code for rate limit exceeded
    return jsonify(data)

app.run(debug=True)
