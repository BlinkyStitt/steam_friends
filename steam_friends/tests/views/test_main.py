import cassette
import pytest


def test_error_handler(flask_app_client):
    with pytest.raises(Exception):
        flask_app_client.get('/test/error')

    # todo: tests disable our error handler :()


def test_index(flask_app_client):
    with cassette.play('data/test_index.yaml'):
        rv = flask_app_client.get('/')

        assert 'ARizzo' in rv.data
        assert 'Son of Themis' in rv.data
        # todo: assert some things
