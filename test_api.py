from src.serve.server import app


def test_get():
    response = app.test_client().get('/forecast')
    assert response.status_code == 200
