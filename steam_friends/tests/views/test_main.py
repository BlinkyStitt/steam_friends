import cassette
import pytest


def test_error_handler(flask_app):
    # disable testing so we use our error handler
    flask_app.testing = False

    c = flask_app.test_client()

    rv = c.get('/test/error')
    print rv.data
    assert "Caught unhandled exception:" in rv.data


def test_index(flask_app_client):
    with cassette.play('data/test_index.yaml'):
        rv = flask_app_client.get('/')

        assert 'ARizzo' in rv.data
        assert 'Son of Themis' in rv.data
        assert 'No users found!' not in rv.data
        assert 'This app works a lot better with more than 2 users.' in rv.data
        # todo: assert some things


def test_index_with_args(flask_app_client):
    with cassette.play('data/test_index_with_args.yaml'):
        rv = flask_app_client.get('/', query_string={
            'ids_and_names': " nynjawitay \n 76561198060689354 76561197969428769 \n nynjawitaynynjawitaynynjawitay",
        })

        assert 'ARizzo' in rv.data
        assert 'Son of Themis' in rv.data
        assert 'No users found!' not in rv.data
        assert 'This app works a lot better with more than 2 users.' not in rv.data
        # todo: assert some things


def test_index_with_empty_args(flask_app_client):
    with cassette.play('data/test_index_with_empty_args.yaml'):
        rv = flask_app_client.get('/', query_string={
            'ids_and_names': " ",
        })

        assert 'No users found!' in rv.data
        assert 'This app works a lot better with more than 2 users.' not in rv.data
        # todo: assert some things


@pytest.mark.xfail
def test_index_with_login(flask_app_client):
    raise NotImplementedError
