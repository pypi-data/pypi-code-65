from pyramid.renderers import render_to_response
from pyramid.view import view_config

from hermes.report import BaseRenderer
from hermes.report import BaseReport


reports = {r.__alias__: r for r in BaseReport.__subclasses__()}
renderers = {r.__alias__: r for r in BaseRenderer.__subclasses__()}


@view_config(route_name="hermes_report", renderer="json", request_method="GET")
def report(request):
    alias = request.matchdict["alias"]
    report = reports[alias](request.db)
    renderer = renderers[alias]()

    filters = {k: v for k, v in request.GET.items()}

    return render_to_response(
        "hermes:templates/report.pt",
        dict(
            selected_filters=filters,
            data=report.report(request.db, **filters),
            pagination=report.pagination(request.db, **filters),
            **renderer.template_data,
        ),
        request=request,
    )


@view_config(route_name="hermes_drill", renderer="json", request_method="GET")
def drill(request):
    alias = request.matchdict["alias"]
    report = reports[alias](request.db)
    renderer = renderers[alias]()

    filters = {k: v for k, v in request.GET.items() if k not in ["order", "page", "per_page"]}

    return render_to_response(
        "hermes:templates/drill.pt",
        dict(
            data=report.drill(request.db, **filters),
            **renderer.drill_data,
        ),
        request=request,
    )


@view_config(route_name="hermes_filter", renderer="json", request_method="GET")
def filter(request):
    alias = request.matchdict["alias"]
    report = reports[alias](request.db)

    filters = {k: v for k, v in request.GET.items()}

    return report.filter(request.db, request.matchdict["filter"], **filters)
