FROM bwstitt/python-alpine:python2

# install the code in a two step process to keep the cache smarter
ADD requirements.txt /src/requirements.txt
RUN su-exec abc pip install -r /src/requirements.txt

COPY . /src
# todo: i wish copy would keep the user...
RUN chown -R abc:abc /src

# install the app as the user, run the --help once to make sure it works
USER abc
WORKDIR /src
RUN ./cli.py --help

ENTRYPOINT ["python", "cli.py"]
CMD ["--help"]
