import datetime
import decimal

from pyramid.config import Configurator
from pyramid.renderers import JSON
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from hermes.settings import settings


def db(request):
    maker = request.registry.dbmaker
    session = maker()

    def cleanup(request):
        if request.exception is not None:
            session.rollback()
        else:
            session.commit()
        session.close()
    request.add_finished_callback(cleanup)

    return session


def main(global_config, **config_blob):
    config = Configurator(settings=config_blob)
    config.include("pyramid_chameleon")

    engine = create_engine(settings.POSTGRES_DSN)
    config.registry.dbmaker = sessionmaker(bind=engine)
    config.add_request_method(db, reify=True)

    json_renderer = JSON()

    def datetime_adapter(obj, request):
        return obj.isoformat()

    def timedelta_adapter(obj, request):
        return obj.total_seconds()

    def decimal_adapter(obj, request):
        return str(obj)

    json_renderer.add_adapter(datetime.datetime, datetime_adapter)
    json_renderer.add_adapter(datetime.date, datetime_adapter)
    json_renderer.add_adapter(datetime.timedelta, timedelta_adapter)
    json_renderer.add_adapter(decimal.Decimal, decimal_adapter)

    config.add_renderer("json", json_renderer)

    # Trade views
    config.add_route("hermes_report", "/report/{alias}")
    config.add_route("hermes_drill", "/report/{alias}/drill")
    config.add_route("hermes_filter", "/report/{alias}/filter/{filter}")

    config.scan(".views")
    config.scan("web_error.handler.pyramid")

    return config.make_wsgi_app()
