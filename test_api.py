import pytest
from app import app, db, popular_banco
from models import Usuario, Cupcake
import json

# fixture: config de ambiente de teste

@pytest.fixture(scope='module')
def client():

    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            popular_banco()


            user_comum = Usuario(email="teste_comum@cupcakes.com", is_admin=False)
            user_comum.set_password("teste456")
            db.session.add(user_comum)

            db.session.commit()

        yield client


# testes de Rota principal

def test_api_status(client):
    response = client.get('/api/status')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'API da Loja de Cupcakes Online!'


def test_listar_cupcakes_sucesso(client):
    response = client.get('/api/cupcakes')
    assert response.status_code == 200
    cupcakes = json.loads(response.data)
    assert len(cupcakes) == 12


# testes de Login e Rota Protegida

def test_login_admin_sucesso(client):
    response = client.post('/api/login', json={
        "email": "admin@cupcakes.com",
        "password": "admin123"
    })
    data = json.loads(response.data)
    assert response.status_code == 200
    assert 'access_token' in data
    assert data['is_admin'] == True


def test_login_falha(client):
    response = client.post('/api/login', json={
        "email": "admin@cupcakes.com",
        "password": "senha_errada"
    })
    assert response.status_code == 401
    assert json.loads(response.data)['msg'] == 'Email ou senha incorretos'


def test_acesso_protegido_sem_token(client):
    response = client.get('/api/protected')
    assert response.status_code == 401


# testes para Adicionar Cupcake

def get_admin_token(client):
    response = client.post('/api/login', json={
        "email": "admin@cupcakes.com",
        "password": "admin123"
    })
    return json.loads(response.data)['access_token']


def test_adicionar_cupcake_admin_sucesso(client):
    admin_token = get_admin_token(client)

    response = client.post('/api/cupcakes', json={
        "nome": "Choco Teste",
        "descricao": "Cupcake de teste de admin",
        "preco": 9.99,
        "estoque": 5
    }, headers={
        'Authorization': f'Bearer {admin_token}'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['nome'] == 'Choco Teste'
    assert Cupcake.query.count() == 13


def test_adicionar_cupcake_nao_admin_falha(client):
    response_login = client.post('/api/login', json={
        "email": "teste_comum@cupcakes.com",
        "password": "teste456"
    })
    comum_token = json.loads(response_login.data)['access_token']

    response = client.post('/api/cupcakes', json={
        "nome": "Barrado",
        "descricao": "Tentativa de usuário comum",
        "preco": 1.00
    }, headers={
        'Authorization': f'Bearer {comum_token}'
    })

    assert response.status_code == 403
    assert json.loads(response.data)['msg'].startswith('Acesso negado')
