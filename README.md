steam_friends
=============


Developing
----------

Initial Setup::

    brew install redis
    virtualenv env
    . env/bin/activate
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    cd static
    npm install && bower install

Before Developing::

    export PATH=$(pwd)/static/node_modules/.bin:$PATH
    . env/bin/activate
    pip install -r requirements-dev.txt

Build the static files::

    cd static
    grunt

Start the cache/queue server::

    redis-server --port 10002

Run the development async workers::

    ./cli.py celery

Run the development server::

    ./cli.py http

Soon: Use uwsgi to start all of the above::

    uwsgi dev.ini

View the development server::

    open http://127.0.0.1:10000/
    open http://127.0.0.1:10000/api/steam_app/239140?with_details=1
    open http://127.0.0.1:10000/api/steam_user/Arizzo?with_friends=1&with_games=1


Testing
----------

Setup the python tests::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-tests.txt

Run the python tests::

    ./test.sh

Recording new HTTP fixtures::

    STEAM_FRIENDS_TEST_RECORD_HTTP=once ./test.sh

Re-recording all HTTP fixtures::

    STEAM_FRIENDS_TEST_RECORD_HTTP=all ./test.sh

Production
----------

Setup nginx to uwsgi_pass to port 10000

Setup the production app::

    virtualenv env
    env/bin/pip install -r requirements-prod.txt

Run the production async workers::

    ./cli.py --env prod celery

Run the production app::

    uwsgi prod.ini

Run the production app on FreeBSD::

    SSL_CERT_FILE=/usr/local/share/certs/ca-root-nss.crt uwsgi prod.ini


Troubleshooting
---------------

If you are serving the app through nginx and the responses are being truncated,
run `nginx -V` and make sure all of the paths listed exist and are owned by the
propert user.


Todo
----

* Better handle cache being unavailable
* Cost of the games
* Links to buy the games that not everyone has
* Show gift copies of games
* Better definition of display name vs steamid vs steamid64.
* Online/offline icons for all the players
* Have a button to auth with steam so we can fetch their userid without them looking it up
* Show friends lists for all the queried users with check boxes to add the friends without having to type any names or look up any 64-bit ids
* Only include actually installed games. I’m not sure this is possible
* Filesize of the games
* Handle Caching be unavailable
* Rate-limiting
* Better CSS than Bootstrap
