steam_friends
=============

This application was quickly written to find common steam games between friends. There are a lot of ideas on how to make this better, but it currently just does the basics.


Developing
----------

Install requirements:

 * redis: `brew install redis`
 * node: `brew install nvm`, setup nvm, `nvm install 5`
 * python virtualenv: `pip install virtualenv`

Initial setup:

    cd steam_friends

    cp env.example env.dev
    $EDITOR env.dev

    virtualenv env
    . env.dev
    pip install --upgrade pip
    pip install -r requirements-dev.txt
    pushd steam_friends/static
    npm install && bower install
    popd

Before Developing:

    cd steam_friends
    . env.dev
    pip install -r requirements-dev.txt

Build the static files:

    cd steam_friends/static
    grunt

    ctrl+c to exit

Start the cache/queue server:

    redis-server --port 10002

    ctrl+c to exit

Run the development async workers (optional):

    ./cli.py celery

    ctrl+c to exit

Run the development server:

    ./cli.py http

    ctrl+c to exit

View the development server:

    open http://127.0.0.1:10000/
    open http://127.0.0.1:10000/api/steam_app/239140?with_details=1
    open http://127.0.0.1:10000/api/steam_user/Arizzo?with_friends=1&with_games=1


Testing
----------

Setup the python tests:

    env/bin/pip install -r requirements-tests.txt

Run the python tests:

    ./test.sh

Recording new HTTP fixtures:

    . env.dev
    SF_TEST_RECORD_HTTP=once ./test.sh

Re-recording all HTTP fixtures:

    . env.dev
    SF_TEST_RECORD_HTTP=all ./test.sh

Production
----------

Setup nginx to uwsgi_pass to port 10000

Setup the production app:

    virtualenv env
    env/bin/pip install -r requirements-prod.txt
    pushd steam_friends/static
    npm install && bower install
    popd

Run the production async workers:

    . env.prod
    ./cli.py --env prod celery

Run the production app:

    uwsgi prod.ini

Run the production app on FreeBSD:

    SSL_CERT_FILE=/usr/local/share/certs/ca-root-nss.crt uwsgi prod.ini


Troubleshooting
---------------

If you are serving the app through nginx and the responses are being truncated,
run `nginx -V` and make sure all of the paths listed exist and are owned by the
propert user.


Todo
----

* More comments
* More tests
* Pretty frontend
* Better handle cache being unavailable
* Cost of the games
* Links to buy the games that not everyone has
* Show gift copies of games if you own any
* Better definition of display name vs steamid vs steamid64.
* Online/offline icons for all the players
* Show friends lists for all the queried users with check boxes to add the friends without having to type any names or look up any 64-bit ids
* Only include actually installed games. I’m not sure this is possible
* Filesize of the games
* Rate-limiting steam API requests
* Better CSS than Bootstrap
* move node_modules and friends out of the static dir and into the root. then change grunt to build into our static dir
* Use pip-compile for requirements
* Document Docker
