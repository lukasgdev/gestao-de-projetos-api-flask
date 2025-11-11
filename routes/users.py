from flask import Blueprint, jsonify,request
from services.csv_service import save_user, find_user_by_email, get_next_user_id, find_user_by_id
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

user_route = Blueprint('users', __name__)

@user_route.route('/register', methods=['POST'])
def cadastrar_usuario():
    data = request.json
    email = data.get('email', '')
    password = data.get('senha', '')
    name = data.get('nome', '')

    if not email or not name or not password:
        return jsonify({"msg": 'Email, senha e nome são obrigatorios'}), 400
    
    if find_user_by_email(email):
        return jsonify({"msg": 'Email ja cadastrado'}), 400
    
    password_hash = generate_password_hash(password)
    new_id = get_next_user_id()

    new_user = {
        "user_id": new_id,
        "name": name,
        "password_hash": password_hash,
        "email": email
    }

    save_user(new_user)

    return jsonify(msg="Usuário cadastrado com sucesso!"), 201

@user_route.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('senha', '')

    if not email or not password:
        return jsonify({"msg": 'Email e senha são obrigatorios'}), 400
    
    user = find_user_by_email(email)

    if not user:
        return jsonify({"msg": 'Email ou senha inválidos'}), 401
    
    user_hash = user.get('password_hash')
    if check_password_hash(user_hash, password):
        user_id = user.get('user_id')

        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        return jsonify(access_token=access_token, refresh_token=refresh_token), 200
    
    else:
        return jsonify({"msg": "Email ou senha inválidos"}), 401
    

@user_route.route('/user')
@jwt_required()
def info_usuarios():
    current_user_id = get_jwt_identity()

    user = find_user_by_id(current_user_id)

    if not user:
        return jsonify({"msg": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": user.get("user_id"),
        "nome": user.get("name"),
        "email": user.get("email")
    }), 200