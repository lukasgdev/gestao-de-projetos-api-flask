from flask import Flask, jsonify
from routes.users import user_route

app = Flask(__name__)

app.register_blueprint(user_route)

@app.route("/")
def api():
    return jsonify(msg="Api funcionando.")

if __name__ == '__main__':
    app.run(debug=True)