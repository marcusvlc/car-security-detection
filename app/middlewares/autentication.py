from app import models
from functools import wraps
import jwt
from flask import request, jsonify, current_app


def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = None
        token_from_args = False

        if 'authorization' in request.headers:
            token = request.headers['authorization']

        if 'token' in request.args:
            token = request.args.get('token')
            token_from_args = True

        if not token:
            return jsonify({"error": "Sem permissões para acessar essa rota"}), 403
        
        if not token_from_args and not "Bearer" in token:
             return jsonify({"error": "Campo de autorização mal formatado ou inválido"}), 401

        try:
            if not token_from_args:
                only_token = token.replace("Bearer ", "")
            else:
                only_token = token
            decoded_token = jwt.decode(only_token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = models.User.query.get(decoded_token['id'])
        except:
            return jsonify({"error": "Token inválido"}), 403

        return f(current_user=current_user, *args, **kwargs)
    
    return wrapper