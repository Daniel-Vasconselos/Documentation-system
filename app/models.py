from app import db

class Empresa(db.Model):
    __tablename__ = "empresas"
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    
class Usuario(db.Model):
    __tablename__ = "usuario"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"),nullable=True)
    email = db.Column(db.String(120), unique=True)
    senha_hash = db.Column(db.String(255))
    tipo_usuario = db.Column(db.String(20), default='empresa')

class Equipamento(db.Model):
    __tablename__ = "equipamentos"
    id = db.Column(db.Integer, primary_key=True)
    empresa_id = db.Column(db.Integer, db.ForeignKey("empresas.id"))
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    codigo = db.Column(db.String(50))
    empresa = db.relationship("Empresa", backref="equipamentos")

class Documento(db.Model):
    __tablename__ = "documentos"
    id = db.Column(db.Integer, primary_key=True)
    equipamento_id = db.Column(db.Integer, db.ForeignKey("equipamentos.id"))
    nome = db.Column(db.String(100))
    arquivo = db.Column(db.String(255))
