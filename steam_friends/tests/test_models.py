from steam_friends import models


def test_steam_app():
    models.SteamApp(
        appid='appid',
        name='name',
        img_logo_url='img_logo_url',
        img_icon_url='img_icon_url',
    )
    # todo: assert things


def test_steam_user():
    models.SteamUser(
        avatar='avatar',
        avatarmedium='avatarmedium',
        avatarfull='avatarfull',
        steamid='steamid',
        personaname='personaname',
        personastate='personastate',
    )
    # todo: assert things
