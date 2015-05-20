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
    pip install -r requirements-dev.txt

Build the static files::

    cd static
    grunt

Run the development server::

    ./dev.py

View the development server::

    open http://127.0.0.1:10000/


Testing
----------

Setup the python tests::

    virtualenv env
    . env/bin/activate
    pip install -r requirements-tests.txt

Run the python tests::
    ./test.sh


Production
----------

Setup nginx to uwsgi_pass to port 10000

Setup the production app::

    virtualenv env
    env/bin/pip install -r requirements-prod.txt

Run the production app::

    uwsgi prod.ini

Run the production app on FreeBSD::

    SSL_CERT_FILE=/usr/local/share/certs/ca-root-nss.crt uwsgi prod.ini
