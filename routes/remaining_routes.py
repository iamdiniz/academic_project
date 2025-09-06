from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import login_required, current_user
from math import ceil
from datetime import datetime
import json
import pytz
import re
from urllib.parse import unquote
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError

from extensions.database import db
from models.instituicao import InstituicaodeEnsino
from models.chefe import Chefe
from models.aluno import Aluno
from models.curso import Curso
from models.skills import SkillsDoAluno
from models.acompanhamento import Acompanhamento
from models.historico import SkillsHistorico
from models.indicacao import Indicacao
from validators.decorators import bloquear_chefe, bloquear_instituicao
from utils.constants import HARD_SKILLS_POR_CURSO, SOFT_SKILLS, CURSOS_PADRAO


remaining_bp = Blueprint('remaining', __name__)


@remaining_bp.route('/instituicao_ensino', endpoint='instituicao_ensino')
@bloquear_instituicao
@login_required
def instituicao_ensino():
    instituicoes = InstituicaodeEnsino.query.all()
    for instituicao in instituicoes:
        instituicao.quantidade_de_alunos = Aluno.query.filter_by(
            id_instituicao=instituicao.id_instituicao).count()
    cursos_por_instituicao = {
        inst.id_instituicao: [curso.nome for curso in Curso.query.filter_by(
            id_instituicao=inst.id_instituicao).all()]
        for inst in instituicoes
    }
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(instituicoes)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    instituicoes_paginadas = instituicoes[start:end]
    return render_template(
        'instituicaoEnsino.html',
        instituicoes=instituicoes_paginadas,
        cursos_por_instituicao=cursos_por_instituicao,
        page=page,
        total_pages=total_pages
    )


@remaining_bp.route('/minhas_selecoes', endpoint='minhas_selecoes')
@bloquear_instituicao
@login_required
def minhas_selecoes():
    chefe_id = current_user.id_chefe
    indicacoes = Indicacao.query.filter_by(id_chefe=chefe_id).all()
    alunos = [indicacao.aluno for indicacao in indicacoes]
    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []
        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}
            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())
        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "periodo": aluno.periodo,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]
    return render_template('minhas_selecoes.html', alunos=alunos_paginados, page=page, total_pages=total_pages)


@remaining_bp.route('/acompanhar', endpoint='acompanhar')
@login_required
@bloquear_instituicao
def acompanhar():
    chefe_id = current_user.id_chefe
    acompanhamentos = Acompanhamento.query.filter_by(id_chefe=chefe_id).all()
    alunos_com_skills = []
    for ac in acompanhamentos:
        aluno = ac.aluno
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []
        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}
            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())
        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome_jovem": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]
    return render_template('acompanhar.html', alunos=alunos_paginados, page=page, total_pages=total_pages)


@remaining_bp.route('/perfil', methods=['GET', 'POST'], endpoint='perfil')
@login_required
def perfil():
    tipo_usuario = session.get('tipo_usuario')

    if request.method == 'POST':
        if tipo_usuario == 'chefe':
            chefe = Chefe.query.get_or_404(current_user.id_chefe)

            nome = request.form['nome'].strip()
            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', nome):
                flash(
                    "O nome deve ter entre 2 e 30 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))

            novo_email = request.form['email']
            email_existente = Chefe.query.filter(
                Chefe.email == novo_email, Chefe.id_chefe != chefe.id_chefe).first()
            if email_existente:
                flash("Já existe um chefe cadastrado com este e-mail.", "danger")
                return redirect(url_for('perfil'))

            chefe.nome = request.form['nome']
            cargo = request.form['cargo']
            if cargo not in ['CEO', 'Gerente', 'Coordenador']:
                flash("Selecione um cargo válido.", "danger")
                return redirect(url_for('perfil'))
            chefe.cargo = cargo
            chefe.nome_empresa = request.form.get('nome_empresa')
            chefe.email = novo_email
            if request.form['senha']:
                chefe.senha = generate_password_hash(request.form['senha'])
            try:
                db.session.commit()
                flash("Perfil atualizado com sucesso!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Já existe um chefe cadastrado com este e-mail.", "danger")
                return redirect(url_for('perfil'))

        elif tipo_usuario == 'instituicao':
            instituicao = InstituicaodeEnsino.query.get_or_404(
                current_user.id_instituicao)
            nome_instituicao = request.form['nome_instituicao'].strip()
            reitor = request.form['reitor'].strip()

            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,50}$', nome_instituicao):
                flash(
                    "O nome da instituição deve ter entre 2 e 50 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))
            if not re.match(r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]{2,30}$', reitor):
                flash(
                    "O nome do reitor deve ter entre 2 e 30 letras e não pode conter números.", "danger")
                return redirect(url_for('perfil'))

            novo_email = request.form['email']
            email_existente = InstituicaodeEnsino.query.filter(
                InstituicaodeEnsino.email == novo_email,
                InstituicaodeEnsino.id_instituicao != instituicao.id_instituicao
            ).first()
            if email_existente:
                flash("Já existe uma instituição cadastrada com este e-mail.", "danger")
                return redirect(url_for('perfil'))

            instituicao.nome_instituicao = request.form['nome_instituicao']
            instituicao.endereco_instituicao = request.form['endereco_instituicao']
            instituicao.reitor = request.form['reitor']
            instituicao.infraestrutura = request.form['infraestrutura']

            nota_mec = request.form['nota_mec']
            if nota_mec not in ['1', '2', '3', '4', '5']:
                flash("Nota MEC deve ser um valor entre 1 e 5.", "danger")
                return redirect(url_for('perfil'))
            instituicao.nota_mec = int(nota_mec)

            modalidades = request.form['modalidades']
            if modalidades not in ['Presencial', 'Hibrido', 'EAD']:
                flash("Selecione uma modalidade válida.", "danger")
                return redirect(url_for('perfil'))
            instituicao.modalidades = modalidades

            instituicao.email = novo_email
            if request.form['senha']:
                instituicao.senha = generate_password_hash(
                    request.form['senha'])
            try:
                db.session.commit()
                flash("Perfil atualizado com sucesso!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("Já existe uma instituição cadastrada com este e-mail.", "danger")
                return redirect(url_for('perfil'))

    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = Curso.query.filter_by(
            id_instituicao=current_user.id_instituicao).all()
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('main.home'))

    return render_template('perfil.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao)


@remaining_bp.route('/configuracoes', methods=['GET', 'POST'], endpoint='configuracoes')
@login_required
def configuracoes():
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario == 'chefe':
        usuario = Chefe.query.get_or_404(current_user.id_chefe)
        cursos_da_instituicao = []
    elif tipo_usuario == 'instituicao':
        usuario = InstituicaodeEnsino.query.get_or_404(
            current_user.id_instituicao)
        cursos_da_instituicao = Curso.query.filter_by(
            id_instituicao=current_user.id_instituicao).all()
    else:
        flash("Tipo de usuário inválido.", "danger")
        return redirect(url_for('main.home'))
    return render_template('configuracoes.html', usuario=usuario, cursos_da_instituicao=cursos_da_instituicao)


@remaining_bp.route('/detalhes_instituicao/<int:id_instituicao>', endpoint='detalhes_instituicao')
@login_required
def detalhes_instituicao(id_instituicao):
    instituicao = InstituicaodeEnsino.query.get_or_404(id_instituicao)
    cursos = Curso.query.filter_by(id_instituicao=id_instituicao).all()
    return render_template('detalhes_instituicao.html', instituicao=instituicao, cursos=cursos)


@remaining_bp.route('/cursos', methods=['GET', 'POST'], endpoint='cursos')
@login_required
def cursos():
    tipo_usuario = session.get('tipo_usuario')
    if tipo_usuario != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('main.home'))
    instituicao_id = current_user.id_instituicao

    if request.method == 'POST':
        # Processar cadastro de curso
        nome_curso = request.form.get('curso')
        if nome_curso:
            try:
                novo_curso = Curso(
                    nome=nome_curso, id_instituicao=instituicao_id)
                db.session.add(novo_curso)
                db.session.commit()
                flash("Curso adicionado com sucesso!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Erro ao adicionar curso: {str(e)}", "danger")

        # Redirecionar após POST (padrão Post-Redirect-Get)
        return redirect(url_for('remaining.cursos'))

    # GET - Buscar e exibir cursos
    cursos_instituicao = Curso.query.filter_by(
        id_instituicao=instituicao_id).all()
    return render_template('cursos.html', cursos=cursos_instituicao, CURSOS_PADRAO=CURSOS_PADRAO)


@remaining_bp.route('/alunos_instituicao', methods=['GET', 'POST'], endpoint='alunos_instituicao')
@bloquear_chefe
@login_required
def alunos_instituicao():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('main.home'))
    instituicao_id = current_user.id_instituicao
    filtro_curso = request.args.get('curso', '')
    query = Aluno.query.filter_by(id_instituicao=instituicao_id)
    if filtro_curso:
        query = query.filter_by(curso=filtro_curso)
    alunos = query.all()

    # Adiciona dados de skills para cada aluno
    alunos_com_skills = []
    for aluno in alunos:
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []

        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}
            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        # Cria um objeto com os dados do aluno e suas skills
        aluno_data = {
            'id_aluno': aluno.id_aluno,
            'nome': aluno.nome_jovem,
            'curso': aluno.curso,
            'periodo': aluno.periodo,
            'data_nascimento': aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            'contato_jovem': aluno.contato_jovem,
            'email': aluno.email,
            'endereco_jovem': aluno.endereco_jovem,
            'formacao': aluno.formacao,
            'hard_labels': hard_labels,
            'hard_skills': hard_skills,
            'soft_labels': soft_labels,
            'soft_skills': soft_skills
        }
        alunos_com_skills.append(aluno_data)

    cursos_instituicao = Curso.query.filter_by(
        id_instituicao=instituicao_id).all()
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    # Prepara lista de nomes de cursos para o modal de cadastro
    cursos_disponiveis = [curso.nome for curso in cursos_instituicao]
    
    # Debug: verificar se há cursos cadastrados
    print(f"DEBUG: Instituição ID: {instituicao_id}")
    print(f"DEBUG: Cursos encontrados: {[curso.nome for curso in cursos_instituicao]}")
    print(f"DEBUG: Cursos disponíveis: {cursos_disponiveis}")

    return render_template('alunos_instituicao.html',
                           alunos=alunos_paginados,
                           cursos=cursos_disponiveis,
                           cursos_disponiveis=cursos_disponiveis,
                           SOFT_SKILLS=SOFT_SKILLS,
                           HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
                           filtro_curso=filtro_curso,
                           page=page,
                           total_pages=total_pages)


@remaining_bp.route('/cadastrar_aluno', methods=['POST'], endpoint='cadastrar_aluno')
@bloquear_chefe
@login_required
def cadastrar_aluno():
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('main.home'))
    try:
        nome_jovem = request.form['nome_jovem']
        data_nascimento = datetime.strptime(
            request.form['data_nascimento'], '%Y-%m-%d')
        curso = request.form['curso']
        periodo = request.form['periodo']
        contato_jovem = request.form['contato_jovem']
        email = request.form['email']
        endereco_jovem = request.form.get('endereco_jovem', '')
        formacao = request.form.get('formacao', '')

        # Verificar se o email já existe
        email_existente = Aluno.query.filter_by(email=email).first()
        if email_existente:
            flash("Já existe um aluno cadastrado com este e-mail.", "danger")
            return redirect(url_for('remaining.alunos_instituicao'))

        novo_aluno = Aluno(
            nome_jovem=nome_jovem,
            data_nascimento=data_nascimento,
            curso=curso,
            periodo=periodo,
            contato_jovem=contato_jovem,
            email=email,
            endereco_jovem=endereco_jovem,
            formacao=formacao,
            id_instituicao=current_user.id_instituicao
        )
        db.session.add(novo_aluno)
        db.session.flush()  # Para obter o ID do aluno

        # Processar skills
        hard_skills_dict = {}
        soft_skills_dict = {}

        # Processar hard skills (formato: hard_nome_da_skill)
        for key, value in request.form.items():
            if key.startswith('hard_') and value and key != 'hard_skills_json':
                skill_name = key.replace('hard_', '').replace('_', ' ')
                try:
                    skill_value = int(value)
                    if 0 <= skill_value <= 10:
                        hard_skills_dict[skill_name] = skill_value
                except ValueError:
                    pass

        # Processar soft skills (formato: nome_da_skill)
        soft_skills_list = SOFT_SKILLS  # Lista de soft skills válidas
        for key, value in request.form.items():
            if value and key in [skill.lower().replace(' ', '_') for skill in soft_skills_list]:
                skill_name = key.replace('_', ' ')
                try:
                    skill_value = int(value)
                    if 0 <= skill_value <= 10:
                        soft_skills_dict[skill_name] = skill_value
                except ValueError:
                    pass

        # Criar registro de skills se houver dados
        if hard_skills_dict or soft_skills_dict:
            skills_do_aluno = SkillsDoAluno(
                id_aluno=novo_aluno.id_aluno,
                hard_skills_json=json.dumps(
                    hard_skills_dict) if hard_skills_dict else None,
                soft_skills_json=json.dumps(
                    soft_skills_dict) if soft_skills_dict else None
            )
            db.session.add(skills_do_aluno)

        db.session.commit()
        flash("Aluno cadastrado com sucesso!", "success")
        return redirect(url_for('remaining.alunos_instituicao'))
    except IntegrityError as e:
        db.session.rollback()
        if "Duplicate entry" in str(e) and "email" in str(e):
            flash("Já existe um aluno cadastrado com este e-mail.", "danger")
        else:
            flash(
                "Erro de integridade do banco de dados. Verifique se os dados estão corretos.", "danger")
        return redirect(url_for('remaining.alunos_instituicao'))
    except Exception as e:
        db.session.rollback()
        flash(f"Erro ao cadastrar aluno: {str(e)}", "danger")
        return redirect(url_for('remaining.alunos_instituicao'))


@remaining_bp.route('/detalhes_aluno/<int:id_aluno>', endpoint='detalhes_aluno')
@login_required
def detalhes_aluno(id_aluno):
    aluno = Aluno.query.get_or_404(id_aluno)
    previous = request.args.get(
        'previous', url_for('remaining.instituicao_ensino'))
    skills = aluno.skills
    hard_labels = []
    hard_skills = []
    soft_labels = []
    soft_skills = []
    hard_dict = {}
    soft_dict = {}
    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}
        hard_labels = list(hard_dict.keys())
        hard_skills = list(hard_dict.values())
        soft_labels = list(soft_dict.keys())
        soft_skills = list(soft_dict.values())

    # Garantir que os dicionários não tenham valores None
    hard_dict = {k: v for k, v in hard_dict.items() if v is not None}
    soft_dict = {k: v for k, v in soft_dict.items() if v is not None}

    return render_template('detalhes_aluno.html',
                           aluno=aluno,
                           hard_labels=hard_labels,
                           hard_skills=hard_skills,
                           hard_values=hard_skills,  # Alias para compatibilidade com template
                           soft_labels=soft_labels,
                           soft_skills=soft_skills,
                           soft_values=soft_skills,  # Alias para compatibilidade com template
                           hard_dict=hard_dict,
                           soft_dict=soft_dict,
                           previous=previous)


@remaining_bp.route('/detalhes_aluno_instituicao/<int:id_aluno>', methods=['GET', 'POST'], endpoint='detalhes_aluno_instituicao')
@bloquear_chefe
@login_required
def detalhes_aluno_instituicao(id_aluno):
    if session.get('tipo_usuario') != 'instituicao':
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('main.home'))

    aluno = Aluno.query.get_or_404(id_aluno)
    if aluno.id_instituicao != current_user.id_instituicao:
        flash("Acesso não permitido.", "danger")
        return redirect(url_for('remaining.alunos_instituicao'))

    # Processar requisição POST (salvamento)
    if request.method == 'POST':
        try:
            # Atualizar dados básicos do aluno
            aluno.nome_jovem = request.form['nome_jovem']
            aluno.data_nascimento = datetime.strptime(
                request.form['data_nascimento'], '%Y-%m-%d')
            aluno.contato_jovem = request.form['contato_jovem']
            aluno.email = request.form['email']
            aluno.endereco_jovem = request.form.get('endereco_jovem', '')
            aluno.curso = request.form['curso']
            aluno.formacao = request.form.get('formacao', '')
            aluno.periodo = int(request.form['periodo'])

            # Verificar se o email já existe em outro aluno
            email_existente = Aluno.query.filter(
                Aluno.email == aluno.email,
                Aluno.id_aluno != aluno.id_aluno
            ).first()
            if email_existente:
                flash("Já existe outro aluno cadastrado com este e-mail.", "danger")
                return redirect(url_for('remaining.detalhes_aluno_instituicao', id_aluno=id_aluno))

            # Processar skills
            hard_skills_dict = {}
            soft_skills_dict = {}

            # Processar hard skills (formato: hard_nome_da_skill)
            for key, value in request.form.items():
                if key.startswith('hard_') and value and key != 'hard_skills_json':
                    skill_name = key.replace('hard_', '').replace('_', ' ')
                    try:
                        skill_value = int(value)
                        if 0 <= skill_value <= 10:
                            hard_skills_dict[skill_name] = skill_value
                    except ValueError:
                        pass

            # Processar soft skills (formato: nome_da_skill)
            soft_skills_list = SOFT_SKILLS
            for key, value in request.form.items():
                if value and key in [skill.lower().replace(' ', '_') for skill in soft_skills_list]:
                    skill_name = key.replace('_', ' ')
                    try:
                        skill_value = int(value)
                        if 0 <= skill_value <= 10:
                            soft_skills_dict[skill_name] = skill_value
                    except ValueError:
                        pass

            # Atualizar ou criar registro de skills
            skills_do_aluno = aluno.skills
            if not skills_do_aluno:
                skills_do_aluno = SkillsDoAluno(id_aluno=aluno.id_aluno)
                db.session.add(skills_do_aluno)

            skills_do_aluno.hard_skills_json = json.dumps(
                hard_skills_dict) if hard_skills_dict else None
            skills_do_aluno.soft_skills_json = json.dumps(
                soft_skills_dict) if soft_skills_dict else None

            db.session.commit()
            flash("Aluno atualizado com sucesso!", "success")
            return redirect(url_for('remaining.detalhes_aluno_instituicao', id_aluno=id_aluno))

        except IntegrityError as e:
            db.session.rollback()
            if "Duplicate entry" in str(e) and "email" in str(e):
                flash("Já existe outro aluno cadastrado com este e-mail.", "danger")
            else:
                flash(
                    "Erro de integridade do banco de dados. Verifique se os dados estão corretos.", "danger")
            return redirect(url_for('remaining.detalhes_aluno_instituicao', id_aluno=id_aluno))
        except Exception as e:
            db.session.rollback()
            flash(f"Erro ao atualizar aluno: {str(e)}", "danger")
            return redirect(url_for('remaining.detalhes_aluno_instituicao', id_aluno=id_aluno))

    # Processar requisição GET (exibição)
    skills = aluno.skills
    hard_labels = []
    hard_skills = []
    soft_labels = []
    soft_skills = []
    hard_dict = {}
    soft_dict = {}
    if skills:
        hard_dict = json.loads(
            skills.hard_skills_json) if skills.hard_skills_json else {}
        soft_dict = json.loads(
            skills.soft_skills_json) if skills.soft_skills_json else {}
        hard_labels = list(hard_dict.keys())
        hard_skills = list(hard_dict.values())
        soft_labels = list(soft_dict.keys())
        soft_skills = list(soft_dict.values())

    # Garantir que os dicionários não tenham valores None
    hard_dict = {k: v for k, v in hard_dict.items() if v is not None}
    soft_dict = {k: v for k, v in soft_dict.items() if v is not None}

    # Obter cursos disponíveis para o dropdown
    cursos_disponiveis = Curso.query.filter_by(
        id_instituicao=current_user.id_instituicao).all()
    cursos_list = [curso.nome for curso in cursos_disponiveis]

    return render_template('detalhes_aluno_instituicao.html',
                           aluno=aluno,
                           hard_labels=hard_labels,
                           hard_skills=hard_skills,
                           soft_labels=soft_labels,
                           soft_skills=soft_skills,
                           hard_dict=hard_dict,
                           soft_dict=soft_dict,
                           cursos_disponiveis=cursos_list,
                           HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
                           SOFT_SKILLS=SOFT_SKILLS)


@remaining_bp.route('/indicar_aluno/<int:id_aluno>', methods=['POST'], endpoint='indicar_aluno')
@bloquear_instituicao
@login_required
def indicar_aluno(id_aluno):
    if session.get('tipo_usuario') != 'chefe':
        return jsonify({'error': 'Acesso não permitido'}), 403
    try:
        chefe_id = current_user.id_chefe
        indicacao_existente = Indicacao.query.filter_by(
            id_chefe=chefe_id, id_aluno=id_aluno).first()
        if indicacao_existente:
            return jsonify({'message': 'Aluno já foi indicado por você!'})
        nova_indicacao = Indicacao(
            id_chefe=chefe_id, id_aluno=id_aluno, data_indicacao=datetime.now())
        db.session.add(nova_indicacao)
        db.session.commit()
        return jsonify({'message': 'Aluno indicado com sucesso!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao indicar aluno: {str(e)}'}), 500


@remaining_bp.route('/ver_alunos_por_curso', methods=['GET'], endpoint='cardAlunos')
@login_required
def ver_alunos_por_curso():
    curso = request.args.get('curso', '')
    # Corrigido: era 'instituicao_id', agora é 'inst_id'
    instituicao_id = request.args.get('inst_id', type=int)
    periodo = request.args.get('periodo', type=int)
    habilidades = request.args.getlist('habilidade')

    query = Aluno.query
    if curso:
        query = query.filter_by(curso=curso)
    if instituicao_id:
        query = query.filter_by(id_instituicao=instituicao_id)
    if periodo:
        query = query.filter_by(periodo=periodo)

    alunos = query.all()
    alunos_com_skills = []

    for aluno in alunos:
        skills = aluno.skills
        hard_labels = []
        hard_skills = []
        soft_labels = []
        soft_skills = []

        if skills:
            hard_dict = json.loads(
                skills.hard_skills_json) if skills.hard_skills_json else {}
            soft_dict = json.loads(
                skills.soft_skills_json) if skills.soft_skills_json else {}
            hard_labels = list(hard_dict.keys())
            hard_skills = list(hard_dict.values())
            soft_labels = list(soft_dict.keys())
            soft_skills = list(soft_dict.values())

        alunos_com_skills.append({
            "id_aluno": aluno.id_aluno,
            "nome": aluno.nome_jovem,
            "data_nascimento": aluno.data_nascimento.strftime('%d/%m/%Y') if aluno.data_nascimento else 'N/A',
            "curso": aluno.curso,
            "periodo": aluno.periodo,
            "contato_jovem": aluno.contato_jovem,
            "email": aluno.email,
            "hard_labels": hard_labels,
            "hard_skills": hard_skills,
            "soft_labels": soft_labels,
            "soft_skills": soft_skills
        })

    # Implementar paginação
    page = request.args.get('page', 1, type=int)
    per_page = 12
    total = len(alunos_com_skills)
    total_pages = (total + per_page - 1) // per_page  # Arredondar para cima

    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos_com_skills[start:end]

    # Importar constantes necessárias
    from utils.constants import HARD_SKILLS_POR_CURSO, SOFT_SKILLS

    return render_template('cardAlunos.html',
                           alunos=alunos_paginados,
                           curso=curso,  # Corrigido: era 'curso_filtro', agora é 'curso'
                           inst_id=instituicao_id,  # Corrigido: era 'instituicao_id', agora é 'inst_id'
                           page=page,
                           total_pages=total_pages,
                           HARD_SKILLS_POR_CURSO=HARD_SKILLS_POR_CURSO,
                           SOFT_SKILLS=SOFT_SKILLS)


@remaining_bp.route('/acompanhar_aluno/<int:id_aluno>', methods=['POST'], endpoint='acompanhar_aluno')
@login_required
@bloquear_instituicao
def acompanhar_aluno(id_aluno):
    try:
        chefe_id = current_user.id_chefe
        ac_existente = Acompanhamento.query.filter_by(
            id_chefe=chefe_id, id_aluno=id_aluno).first()
        if ac_existente:
            return jsonify({'message': 'Aluno já está sendo acompanhado!'})

        novo_acompanhamento = Acompanhamento(
            id_chefe=chefe_id, id_aluno=id_aluno)
        db.session.add(novo_acompanhamento)
        db.session.commit()
        return jsonify({'message': 'Aluno adicionado à sua lista de acompanhamento!'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Erro ao acompanhar aluno: {str(e)}'}), 500


@remaining_bp.route('/remover_acompanhamento/<int:id_aluno>', methods=['POST'], endpoint='remover_acompanhamento')
@login_required
@bloquear_instituicao
def remover_acompanhamento(id_aluno):
    chefe_id = current_user.id_chefe
    ac = Acompanhamento.query.filter_by(
        id_chefe=chefe_id, id_aluno=id_aluno).first()
    if ac:
        db.session.delete(ac)
        db.session.commit()
        flash("Aluno removido do acompanhamento.", "success")
    else:
        flash("Acompanhamento não encontrado.", "danger")
    return redirect(url_for('remaining.acompanhar'))


@remaining_bp.route('/status_aluno/<int:id_aluno>', endpoint='status_aluno')
@login_required
@bloquear_instituicao
def status_aluno(id_aluno):
    chefe_id = current_user.id_chefe
    historicos = SkillsHistorico.query.filter_by(
        id_aluno=id_aluno, id_chefe=chefe_id).order_by(SkillsHistorico.data.desc()).all()
    aluno = Aluno.query.get_or_404(id_aluno)
    historicos_dict = []
    fuso_brasil = pytz.timezone('America/Recife')
    for hist in historicos:
        data_brasil = hist.data
        if data_brasil and data_brasil.tzinfo is None:
            data_brasil = pytz.utc.localize(
                data_brasil).astimezone(fuso_brasil)
        elif data_brasil:
            data_brasil = data_brasil.astimezone(fuso_brasil)
        hard = json.loads(
            hist.hard_skills_json) if hist.hard_skills_json else {}
        soft = json.loads(
            hist.soft_skills_json) if hist.soft_skills_json else {}
        historicos_dict.append(
            {'data': data_brasil, 'hard_skills': hard, 'soft_skills': soft})
    historico_pares = []
    if len(historicos_dict) > 1:
        for i in range(len(historicos_dict) - 1):
            atual = historicos_dict[i]
            anterior = historicos_dict[i + 1]
            historico_pares.append(
                {'data': atual['data'], 'atual': atual, 'anterior': anterior})
    elif len(historicos_dict) == 1:
        historico_pares.append(
            {'data': historicos_dict[0]['data'], 'atual': historicos_dict[0], 'anterior': None})
    return render_template('status_aluno.html', historicos=historicos_dict, historico_pares=historico_pares, aluno=aluno)


@remaining_bp.route('/alunos_indicados', endpoint='alunos_indicados')
@bloquear_chefe
@login_required
def alunos_indicados():
    """Lista todos os alunos que foram indicados por chefes"""
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Busca todas as indicações com informações dos alunos e chefes
    indicacoes = db.session.query(Indicacao, Aluno, Chefe).join(
        Aluno, Indicacao.id_aluno == Aluno.id_aluno
    ).join(
        Chefe, Indicacao.id_chefe == Chefe.id_chefe
    ).order_by(Indicacao.data_indicacao.desc()).all()

    # Formata os dados para o template
    alunos = []
    for indicacao, aluno, chefe in indicacoes:
        alunos.append({
            'id_aluno': aluno.id_aluno,
            'nome': aluno.nome_jovem,
            'curso': aluno.curso,
            'periodo': aluno.periodo,
            'chefe_nome': chefe.nome,
            'chefe_empresa': chefe.nome_empresa,
            'data_indicacao': indicacao.data_indicacao.strftime('%d/%m/%Y')
        })

    # Paginação
    total = len(alunos)
    total_pages = ceil(total / per_page)
    start = (page - 1) * per_page
    end = start + per_page
    alunos_paginados = alunos[start:end]

    return render_template(
        'alunos_indicados.html',
        alunos=alunos_paginados,
        page=page,
        total_pages=total_pages
    )


def register_remaining_routes(app):
    app.register_blueprint(remaining_bp)

    # Cria aliases de endpoint sem o prefixo do blueprint para compatibilidade legada
    try:
        existing_endpoints = {
            rule.endpoint: rule.rule for rule in app.url_map.iter_rules()}
        for rule in list(app.url_map.iter_rules()):
            if rule.endpoint.startswith('remaining.'):
                simple_endpoint = rule.endpoint.split('.', 1)[1]
                if simple_endpoint not in existing_endpoints:
                    app.add_url_rule(
                        rule.rule,
                        endpoint=simple_endpoint,
                        view_func=app.view_functions[rule.endpoint],
                        methods=rule.methods
                    )
    except Exception:
        # Em caso de qualquer incompatibilidade, ignorar silenciosamente
        pass
