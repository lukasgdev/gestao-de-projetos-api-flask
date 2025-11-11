from flask import Blueprint, jsonify,request

user_route = Blueprint('users', __name__)

@user_route.route('/register', methods=['POST'])
def cadastrar_usuario():
    return jsonify(msg="registro de usuario")

@user_route.route('/login', methods=['POST'])
def login():
    return jsonify(msg="login de usuario")

@user_route.route('/user')
def info_usuarios():
    return jsonify(msg="informações do usuario logado")