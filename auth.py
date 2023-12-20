from functools import wraps
import settings
import jwt
from flask import jsonify, request


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        # ensure the jwt-token is passed with the headers
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:  # throw error if no token provided
            return jsonify({"message": "A valid token is missing!"}), 401
        try:
           # decode the token to obtain user public_id
            data = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            # return jsonify(data)
        except:
            return jsonify({
                "status": "fail",
                "message": "Invalid token!"
            }), 401
        return f(*args, **kwargs)
    return decorator
