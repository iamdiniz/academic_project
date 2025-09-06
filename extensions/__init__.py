# Extensões do Flask
from .database import db, init_db
from .login import login_manager, init_login
from .user_loader import load_user

__all__ = ['db', 'init_db', 'login_manager', 'init_login', 'load_user']
