import os
import shutil
import qrcode
from flask import Blueprint, render_template, request, redirect, session, send_file
from io import BytesIO
from app import db
from app.models import Empresa, Usuario, Equipamento, Documento
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

main = Blueprint("main", __name__)
UPLOAD_FOLDER = "app/static/uploads"

@main.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario:
            from werkzeug.security import check_password_hash
            if check_password_hash(usuario.senha_hash, senha):
                session["usuario_id"] = usuario.id
                session["tipo_usuario"] = usuario.tipo_usuario
                if usuario.tipo_usuario == "admin":
                    return redirect("/admin")
                session["empresa_id"] = usuario.empresa_id
                return redirect("dashboard")
    return render_template("login.html")

@main.route("/cadastro", methods=["GET","POST"])
def cadastro():
    if request.method == "POST":
        empresa_id = request.form["empresa_id"]
        email = request.form["email"]
        senha = request.form["senha"] 
        senha_hash = generate_password_hash(senha)
        novo_usuario = Usuario(
            empresa_id = empresa_id,
            email = email,
            senha_hash = senha_hash
        )
        db.session.add(novo_usuario)
        db.session.commit()
        return redirect("/")
    empresas = Empresa.query.all()
    return render_template("cadastro.html", empresas = empresas)

@main.route("/admin", methods=["GET","POST"])
def admin():
    if "usuario_id" not in session:
        return redirect("/")
    if session.get("tipo_usuario") != "admin":
        return redirect("/dashboard")
    if request.method == "POST":
        tipo_form =request.form.get("tipo_form")
        #cadastrar empresa
        if tipo_form == "nova_empresa":
            nome_empresa = request.form.get("nome_empresa")
            if nome_empresa:
                empresa = Empresa(nome=nome_empresa)
                db.session.add(empresa)
                db.session.commit()
        #cadastrar equipamento
        elif tipo_form == "novo_equipamento":
            nome = request.form.get("nome")
            descricao = request.form.get("descricao")
            codigo = request.form.get("codigo")
            empresa_id = request.form.get("empresa_id")
            equipamento = Equipamento(nome = nome, descricao = descricao, codigo = codigo, empresa_id = empresa_id)
            db.session.add(equipamento)
            db.session.commit()
        return redirect("/admin")
    empresa_id = request.args.get("empresa_id")

    if empresa_id:
        equipamentos = Equipamento.query.filter_by(empresa_id=empresa_id).all()
    else:
        equipamentos = Equipamento.query.all()
    empresas = Empresa.query.all()
    return render_template("admin.html",empresas = empresas, equipamentos = equipamentos)

@main.route("/dashboard")
def dashboard():
    if "empresa_id" not in session:
        return redirect("/")
    empresa = Empresa.query.get(session["empresa_id"])
    equipamentos  = Equipamento.query.filter_by(empresa_id = session["empresa_id"]).all()
    return render_template("dashboard.html", equipamentos = equipamentos, empresa = empresa)

@main.route("/equipamento/<int:id>")
def documentacao_equipamento(id):
    if "empresa_id" not in session:
        return redirect("/")
    equipamento = Equipamento.query.filter_by(id = id, empresa_id = session["empresa_id"]).first()
    if not equipamento:
        return "Equipamento não encontrado ou acesso negado"
    documentos = Documento.query.filter_by(equipamento_id = id).all()
    return render_template("documentacao_equipamento.html",equipamento = equipamento, documentos = documentos)

@main.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@main.route("/admin/deletar/<int:id>")
def deletar_equipamento(id):
    if session.get("tipo_usuario") != "admin":
        return redirect("/")
    equipamento = Equipamento.query.get(id)
    if equipamento:
        empresa_nome = equipamento.empresa.nome
        equipamento_nome = equipamento.nome
        pasta = os.path.join(UPLOAD_FOLDER,empresa_nome,equipamento_nome)
        # apagar pasta inteira do equipamento
        if os.path.exists(pasta):
            shutil.rmtree(pasta)
        Documento.query.filter_by(equipamento_id=id).delete()
        db.session.delete(equipamento)
        db.session.commit()
    return redirect("/admin")

@main.route("/admin/editar/<int:id>", methods = ["GET", "POST"])
def editar_documentos(id):
    if session.get("tipo_usuario") != "admin":
        return redirect("/")
    equipamento = Equipamento.query.get(id)
    if request.method == "POST":
        arquivo = request.files.get("arquivo")
        nome = request.form.get("nome")
        if arquivo:
            nome_arquivo = secure_filename(arquivo.filename)
            empresa_nome = equipamento.empresa.nome
            equipamento_nome = equipamento.nome
            pasta_empresa = os.path.join(UPLOAD_FOLDER, empresa_nome)
            pasta_equipamento = os.path.join(pasta_empresa, equipamento_nome)
            # criar pastas se não existirem
            os.makedirs(pasta_equipamento, exist_ok=True)
            caminho = os.path.join(pasta_equipamento, nome_arquivo)
            arquivo.save(caminho)
            caminho_relativo = f"{empresa_nome}/{equipamento_nome}/{nome_arquivo}"
            documento = Documento(nome=nome,arquivo=caminho_relativo,equipamento_id=id)
            db.session.add(documento)
            db.session.commit()
        return redirect(f"/admin/editar/{id}")
    documentos = Documento.query.filter_by(equipamento_id=id).all()
    return render_template("admin_documentos.html",equipamento=equipamento,documentos=documentos)

@main.route("/admin/documento/deletar/<int:id>")
def deletar_documentos(id):
    if session.get("tipo_usuario") != "admin":
        return redirect("/")
    documento = Documento.query.get(id)
    equipamento_id = documento.equipamento_id
    if documento:
        caminho = os.path.join(UPLOAD_FOLDER, documento.arquivo)
        if os.path.exists(caminho):
            os.remove(caminho)
        db.session.delete(documento)
        db.session.commit()
    return redirect(f"/admin/editar/{equipamento_id}")

@main.route("/qrcode/equipamento/<int:id>")
def gerar_qrcode(id):
    url = f"http:localhost:5000/equipamento/{id}"
    qr = qrcode.make(url)
    img_io = BytesIO()
    qr.save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype = "image/png")
