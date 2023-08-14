import pytest
from unittest import mock


@pytest.fixture
def app():
    from app import create_app
    app = create_app()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mocked_openai_chat_completion():
    with mock.patch('app.gpt.openai.ChatCompletion.create') as mocked:
        yield mocked


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'TranslateGPT' in response.data


def test_index_post_empty_text(client):
    response = client.post('/', data={'text': '', 'language': 'English'})
    assert response.status_code == 200
    assert b'TranslateGPT' in response.data


def test_index_post(client, mocked_openai_chat_completion):
    mocked_openai_chat_completion.return_value = {
        'choices': [
            {'message': {'content': 'Translated text'}}
        ]
    }
    response = client.post('/', data={'text': 'Привет', 'language': 'English'})
    assert response.status_code == 200
    assert b'Translated text' in response.data


def test_index_post_empty_prompt(client, mocked_openai_chat_completion):
    response = client.post('/', data={'text': '', 'language': 'English'})
    assert response.status_code == 200
    assert b'TranslateGPT' in response.data


def test_index_post_no_prompt(client, mocked_openai_chat_completion):
    response = client.post('/', data={'text': 'Привет', 'language': 'English'})
    assert response.status_code == 200
    assert b'TranslateGPT' in response.data


def test_index_post_api_error(client, mocked_openai_chat_completion):
    mocked_openai_chat_completion.side_effect = Exception('API error')
    response = client.post('/', data={'text': 'Привет', 'language': 'English'})
    print(response.data)
    assert response.status_code == 500
    assert b'TranslateGPT' in response.data


