from flask import Flask, jsonify
from flask_cors import CORS
from models import db, Cupcake, Usuario
import os

app = Flask(__name__)

CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'loja_cupcakes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route('/api/cupcakes', methods=['GET'])
def listar_cupcakes():
    """Rota para retornar a lista de todos os cupcakes disponíveis."""

    cupcakes = Cupcake.query.all()

    cupcakes_json = [cupcake.to_dict() for cupcake in cupcakes]

    return jsonify(cupcakes_json)

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({"status": "API da Loja de Cupcakes Online!"})

def popular_banco():
    db.drop_all()
    db.create_all()

    cupcakes_data = [
        Cupcake("Red Velvet", "Bolo de cacau vermelho com cobertura de cream cheese.", 12.00, 15),
        Cupcake("Chocolate Belga", "Massa fofa de chocolate com ganache cremoso.", 15.00, 20),
        Cupcake("Limão Siciliano", "Sabor cítrico e refrescante com cobertura de merengue.", 11.50, 10),
        Cupcake("Cenoura com Brigadeiro", "Massa de cenoura clássica com cobertura de brigadeiro gourmet.", 13.00, 25),
        Cupcake("Baunilha e Doce de Leite", "Massa de baunilha com recheio de doce de leite argentino.", 14.00, 12),
        Cupcake("Oreo", "Massa e cobertura com pedacinhos do famoso biscoito.", 16.00, 18),
        Cupcake("Morango e Chantilly", "Massa leve de morango com cobertura fresca de chantilly.", 12.50, 14),
        Cupcake("Café e Cardamomo", "Sabor exótico de café e especiarias.", 14.50, 8),
        Cupcake("Churros", "Massa de canela com cobertura de açúcar e doce de leite.", 13.50, 16),
        Cupcake("Abacaxi com Coco", "Sabor tropical e úmido.", 11.00, 11),
        Cupcake("Menta e Chocolate", "Combinação refrescante e intensa.", 15.50, 13),
        Cupcake("Pistache", "Sabor sofisticado e delicado.", 17.00, 9),
    ]

    for cupcake in cupcakes_data:
        db.session.add(cupcake)

    admin = Usuario("admin@cupcakes.com", "senha_hash_segura", is_admin=True)
    db.session.add(admin)

    db.session.commit()
    print("Banco de dados populado com 12 cupcakes e usuário admin.")

if __name__ == '__main__':
    with app.app_context():
        popular_banco()

    app.run(debug=True, port=5000)
