steam_friends
=============


Developing
----------

Initial Setup::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-dev.txt
    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    cd static
    npm install && bower install

Before Developing::

    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    . env/bin/activate

Building static files::

    cd static
    grunt

Running the app::

    STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y STEAM_FRIENDS_DEBUG=1 ./serve.py

    open http://127.0.0.1:10000/


Testing
----------

Running the python tests::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-tests.txt
    STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y py.test


Production
----------

Setup nginx to proxy your domain to port 10000

Then run the app::

    virtualenv env
    env/bin/pip install -r requirements.txt
    STEAMODD_API_KEY=X STEAM_FRIENDS_SECRET_KEY=Y STEAM_FRIENDS_PROXY_FIX=1 ./env/bin/python ./serve.py
