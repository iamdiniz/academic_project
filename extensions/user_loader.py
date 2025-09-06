from flask import session
from models.chefe import Chefe
from models.instituicao import InstituicaodeEnsino

def load_user(user_id):
    """
    Carrega o usuário baseado no tipo armazenado na sessão
    Esta função é usada pelo Flask-Login
    """
    tipo_usuario = session.get('tipo_usuario')
    
    if tipo_usuario == 'chefe':
        return Chefe.query.get(int(user_id))
    elif tipo_usuario == 'instituicao':
        return InstituicaodeEnsino.query.get(int(user_id))
    return None
