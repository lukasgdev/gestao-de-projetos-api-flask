from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from datetime import timedelta
from routes.users import user_route
from routes.projects import projects_route
from routes.lists import list_route

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "8d5111adeddaafe18a2118d05d12281ffd05af27248cabccbde3dec49d9e987f"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=1)
jwt = JWTManager(app)

app.register_blueprint(user_route)
app.register_blueprint(projects_route, url_prefix='/user')
app.register_blueprint(list_route, url_prefix='/user/projects')

@app.route("/")
def api():
    return jsonify(msg="Api funcionando.")

if __name__ == '__main__':
    app.run(debug=True)