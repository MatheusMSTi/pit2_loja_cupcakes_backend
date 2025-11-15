import pytest
from app import app, db, popular_banco
import json


@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.test_client() as client:
        with app.app_context():
            popular_banco()

        yield client


# Testes Unitários

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

    assert 'nome' in cupcakes[0]
    assert 'preco' in cupcakes[0]
    assert cupcakes[0]['nome'] == 'Red Velvet'
    