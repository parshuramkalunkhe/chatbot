from flask import Flask, render_template, jsonify, request
 
app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api", methods=["GET", "POST"])
def qa():
   
    if request.method == "POST":
        print(request.json)
        question = request.json.get("input")
        data = {"result": question}
        return jsonify(data)
    return ""

app.run(debug=True)

