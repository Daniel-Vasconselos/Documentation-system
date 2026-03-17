class Config:
    SECRET_KEY = "chave_secreta"
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost/machine_docs"
    SQLALCHEMY_TRACK_MODIFICATIONS = False