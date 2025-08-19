import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models import Base, engine, SessionLocal, User  # noqa: E402
from app import app  # noqa: E402


def setup_module(module):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    db.query(User).delete()
    db.commit()
    db.close()


def test_register_login_and_graphql():
    client = app.test_client()
    resp = client.post('/api/register', json={'email': 'test@example.com', 'password': 'secret'})
    assert resp.status_code == 201
    token = resp.get_json()['verification_token']

    verify_resp = client.get(f'/api/verify/{token}')
    assert verify_resp.status_code == 200

    login_resp = client.post('/api/login', json={'email': 'test@example.com', 'password': 'secret'})
    assert login_resp.status_code == 200
    jwt_token = login_resp.get_json()['token']
    assert jwt_token

    query = {'query': '{ users { email isVerified } }'}
    gql_resp = client.post('/graphql', json=query)
    data = gql_resp.get_json()
    assert data['data']['users'][0]['email'] == 'test@example.com'
    assert data['data']['users'][0]['isVerified'] is True
