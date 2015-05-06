import os

from flask import Flask
from flask import render_template
import steamapi


app = Flask(__name__)

# commited secrets. yey!
STEAM_API_KEY = os.environ.get("STEAM_API_KEY", "DA0509DA52BC706F282F2D315D3C61BB")


@app.route('/')
def index():
    steamapi.core.APIConnection(api_key=STEAM_API_KEY)

    # todo: this should be from a form
    name = 'nynjawitay'

    app.logger.debug("Checking name: %s", name)

    try:
        steam_user = steamapi.user.SteamUser(userid=int(name))
    except ValueError:  # Not an ID, but a vanity URL.
        steam_user = steamapi.user.SteamUser(userurl=name)

    app.logger.debug("steam_user: %r", steam_user)

    name = steam_user.name

    try:
        content = "You have {} friends and {} games.".format(
            len(steam_user.friends),
            len(steam_user.games),
        )
        img = steam_user.avatar
    except steamapi.errors.APIUnauthorized:
        app.logger.exception("Unable to query user data")
        # We might not have permission to the user's friends list or games, so just carry on with a blank message.
        content = None
        img = None

    return render_template('index.html', name=name, content=content, img=img)


if __name__ == '__main__':
    app.debug = True
    app.run()
