from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user
from flask import session
from models.chefe import Chefe
from models.instituicao import InstituicaodeEnsino
from extensions.database import db
from sqlalchemy.exc import IntegrityError

class AuthService:
    """Serviço para operações de autenticação"""
    
    @staticmethod
    def login_chefe(email, senha):
        """
        Autentica um chefe
        
        Args:
            email (str): E-mail do chefe
            senha (str): Senha do chefe
        
        Returns:
            tuple: (chefe, mensagem_erro) - (objeto_chefe, None) se sucesso, (None, mensagem) se erro
        """
        chefe = Chefe.query.filter_by(email=email).first()
        if chefe and check_password_hash(chefe.senha, senha):
            session['user_id'] = chefe.id_chefe
            session['tipo_usuario'] = 'chefe'
            login_user(chefe)
            return chefe, None
        return None, "E-mail ou senha inválidos."
    
    @staticmethod
    def login_instituicao(email, senha):
        """
        Autentica uma instituição de ensino
        
        Args:
            email (str): E-mail da instituição
            senha (str): Senha da instituição
        
        Returns:
            tuple: (instituicao, mensagem_erro) - (objeto_instituicao, None) se sucesso, (None, mensagem) se erro
        """
        instituicao = InstituicaodeEnsino.query.filter_by(email=email).first()
        if instituicao and check_password_hash(instituicao.senha, senha):
            session['user_id'] = instituicao.id_instituicao
            session['tipo_usuario'] = 'instituicao'
            login_user(instituicao)
            return instituicao, None
        return None, "E-mail ou senha inválidos."
    
    @staticmethod
    def cadastrar_chefe(nome, email, senha, empresa_nome, cargo):
        """
        Cadastra um novo chefe
        
        Args:
            nome (str): Nome do chefe
            email (str): E-mail do chefe
            senha (str): Senha do chefe
            empresa_nome (str): Nome da empresa
            cargo (str): Cargo do chefe
        
        Returns:
            tuple: (chefe, mensagem_erro) - (objeto_chefe, None) se sucesso, (None, mensagem) se erro
        """
        try:
            novo_chefe = Chefe(
                nome=nome,
                email=email,
                senha=generate_password_hash(senha),
                nome_empresa=empresa_nome,
                cargo=cargo
            )
            db.session.add(novo_chefe)
            db.session.commit()
            return novo_chefe, None
        except IntegrityError:
            db.session.rollback()
            return None, "E-mail já cadastrado."
    
    @staticmethod
    def cadastrar_instituicao(nome_instituicao, email, senha, endereco, infraestrutura, 
                             nota_mec, modalidades, cursos_selecionados, reitor):
        """
        Cadastra uma nova instituição de ensino
        
        Args:
            nome_instituicao (str): Nome da instituição
            email (str): E-mail da instituição
            senha (str): Senha da instituição
            endereco (str): Endereço da instituição
            infraestrutura (str): Descrição da infraestrutura
            nota_mec (str): Nota MEC
            modalidades (str): Modalidades de ensino
            cursos_selecionados (list): Lista de cursos selecionados
            reitor (str): Nome do reitor
        
        Returns:
            tuple: (instituicao, mensagem_erro) - (objeto_instituicao, None) se sucesso, (None, mensagem) se erro
        """
        try:
            nova_instituicao = InstituicaodeEnsino(
                nome_instituicao=nome_instituicao,
                email=email,
                senha=generate_password_hash(senha),
                infraestrutura=infraestrutura,
                nota_mec=nota_mec,
                areas_de_formacao=", ".join(cursos_selecionados),
                modalidades=modalidades,
                quantidade_de_alunos=0,
                reitor=reitor,
                endereco_instituicao=endereco
            )
            db.session.add(nova_instituicao)
            db.session.commit()
            return nova_instituicao, None
        except IntegrityError:
            db.session.rollback()
            return None, "E-mail ou instituição já cadastrados."
