from flask_httpauth import HTTPTokenAuth

auth = HTTPTokenAuth(scheme='Bearer')

tokens = {
    'admin' : 'admin'
}

@auth.verify_token
def verify_token(token):
    if token in tokens:
        return tokens[token]