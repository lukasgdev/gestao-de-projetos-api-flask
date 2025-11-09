from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def main():
    return jsonify({"message" : "API Funcionando"})

if __name__ == "__main__":
    app.run(debug=True)