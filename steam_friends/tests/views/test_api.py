import pytest

from steam_friends import models


@pytest.fixture
def example_steam_app():
    return models.SteamApp(
        appid='appid',
        name='name',
        img_logo_url='img_logo_url',
        img_icon_url='img_icon_url',
    )
