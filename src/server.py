#!/usr/bin/python

from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response


def sample(request):
    file = open("./home/output/sample.json", "r")
    data = file.read()

    return Response(
        data.encode("utf-8"),
        content_type="application/json",
    )


config = Configurator()

config.add_route("sample", "/")
config.add_view(sample, route_name="sample")

app = config.make_wsgi_app()
server = make_server('0.0.0.0', 8080, app)
server.serve_forever()
