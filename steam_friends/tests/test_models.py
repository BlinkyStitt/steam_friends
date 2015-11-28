from __future__ import absolute_import, print_function

import pytest

from steam_friends import models


def test_id_from_openid(flask_app):
    fake_openid = 'http://steamcommunity.com/openid/id/test'
    with flask_app.test_request_context():
        assert models.SteamUser.id_from_openid(fake_openid) == 'test'


def test_bad_id_from_openid(flask_app):
    fake_openid = 'http://notsteamcommunity.com/openid/id/test'
    with flask_app.test_request_context():
        with pytest.raises(ValueError):
            models.SteamUser.id_from_openid(fake_openid)


@pytest.vcr.use_cassette()
def test_id_to_id64(flask_app):
    with flask_app.test_request_context():
        assert models.SteamUser.id_to_id64('nynjawitay') == '76561197980747796'


@pytest.vcr.use_cassette()
def test_bad_id_to_id64(flask_app):
    with flask_app.test_request_context():
        steamid64 = models.SteamUser.id_to_id64('nynjawitaynynjawitaynynjawitay')
        assert steamid64 is None


def test_steam_app(flask_app):
    with flask_app.test_request_context():
        appid0 = models.SteamApp(
            appid='appid0',
            name='name0',
            img_logo_url='img_logo_url0',
            img_icon_url='img_icon_url0',
        )
        appid1 = models.SteamApp(
            appid='appid1',
            name='name1',
            img_logo_url='img_logo_url1',
            img_icon_url='img_icon_url1',
        )

        print("appid0:", repr(appid0))
        print("appid1:", repr(appid1))

        assert appid0 == appid0
        assert appid0 < appid1
        assert appid0 != appid1
        assert appid0 != ""
        assert None is not appid0
        assert appid0.appid == 'appid0'
        assert appid0.name == 'name0'
        assert appid0.img_icon_url == "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg".format(
            appid="appid0",
            hash="img_icon_url0",
        )
        assert appid0.img_logo_url == "http://media.steampowered.com/steamcommunity/public/images/apps/{appid}/{hash}.jpg".format(
            appid="appid0",
            hash="img_logo_url0",
        )


def test_steam_user_init():
    models.SteamUser(
        avatar='avatar',
        avatarmedium='avatarmedium',
        avatarfull='avatarfull',
        steamid='steamid',
        personaname='personaname',
        personastate='personastate',
    )


@pytest.vcr.use_cassette()
def test_steam_user_from_steamid64(flask_app):
    with flask_app.test_request_context():
        steam_user = models.SteamUser.get_user('76561198060689354')

        assert steam_user.personaname == 'ARizzo'


@pytest.vcr.use_cassette()
def test_failed_steam_user_from_steamid64(flask_app):
    with flask_app.test_request_context():
        steam_user = models.SteamUser.get_user('0000')

        assert steam_user is None
