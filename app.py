from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, Cupcake, Usuario, bcrypt
import os
from flask_jwt_extended import create_access_token, jwt_required, JWTManager, get_jwt_identity

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'loja_cupcakes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "super-secret-key-para-o-pit2"
app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_CSRF_PROTECT"] = False

db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)


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

    admin = Usuario(email="admin@cupcakes.com", is_admin=True)
    admin.set_password("admin123")
    db.session.add(admin)

    db.session.commit()
    print("Banco de dados populado com 12 cupcakes e usuário admin (Senha: admin123).")


# rotas de autenticação (Controller)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    is_admin = data.get('is_admin', False)

    if Usuario.query.filter_by(email=email).first():
        return jsonify({"msg": "Email já registrado"}), 400

    new_user = Usuario(email=email, is_admin=is_admin)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"msg": "Usuário registrado com sucesso", "email": email}), 201


@app.route('/api/cupcakes', methods=['GET', 'POST'])
@jwt_required(optional=True)
def cupcakes_handler():
    if request.method == 'GET':
        cupcakes = Cupcake.query.all()
        cupcakes_json = [cupcake.to_dict() for cupcake in cupcakes]
        return jsonify(cupcakes_json)

    elif request.method == 'POST':

        user_id = get_jwt_identity()
        if not user_id:
            return jsonify({"msg": "Token de autenticação ausente ou inválido."}), 401

        user = Usuario.query.get(user_id)
        if not user or not user.is_admin:
            return jsonify(
                {"msg": "Acesso negado: Somente administradores podem adicionar cupcakes."}), 403

        data = request.get_json()
        try:
            new_cupcake = Cupcake(
                nome=data['nome'],
                descricao=data['descricao'],
                preco=data['preco'],
                estoque=data.get('estoque', 1)
            )
            db.session.add(new_cupcake)
            db.session.commit()
            return jsonify(new_cupcake.to_dict()), 201

        except Exception as e:
            db.session.rollback()
            return jsonify({"msg": "Erro ao adicionar cupcake", "error": str(e)}), 400

    return jsonify({"msg": "Método não permitido."}), 405


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = Usuario.query.filter_by(email=email).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))

        return jsonify(access_token=access_token, is_admin=user.is_admin, user_id=user.id), 200

    return jsonify({"msg": "Email ou senha incorretos"}), 401


@app.route('/api/protected', methods=['GET'])
@jwt_required()
def protected():

    current_user_id = get_jwt_identity()
    return jsonify(logged_in_as=current_user_id, message="Você está logado e tem acesso a este recurso!"), 200

if __name__ == '__main__':
    with app.app_context():
        popular_banco()

    app.run(debug=True, port=5000)