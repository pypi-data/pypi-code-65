import pypd

from dagster import Field, resource


class PagerDutyService(object):
    """Integrates with PagerDuty via the pypd library.

    See:
        https://v2.developer.pagerduty.com/docs/events-api-v2
        https://v2.developer.pagerduty.com/docs/send-an-event-events-api-v2
        https://support.pagerduty.com/docs/services-and-integrations#section-events-api-v2
        https://github.com/PagerDuty/pagerduty-api-python-client

    for documentation and more information.
    """

    def __init__(self, routing_key):
        self.routing_key = routing_key

    def EventV2_create(
        self,
        summary,
        source,
        severity,
        event_action="trigger",
        dedup_key=None,
        timestamp=None,
        component=None,
        group=None,
        event_class=None,
        custom_details=None,
    ):
        """Events API v2 enables you to add PagerDuty's advanced event and incident management
        functionality to any system that can make an outbound HTTP connection.

        Arguments:
            summary {string} -- A high-level, text summary message of the event. Will be used to
                                construct an alert's description.

                                Example: "PING OK - Packet loss = 0%, RTA = 1.41 ms" "Host
                                         'acme-andromeda-sv1-c40 :: 179.21.24.50' is DOWN"

            source {string} -- Specific human-readable unique identifier, such as a hostname, for
                               the system having the problem.

                               Examples:
                               "prod05.theseus.acme-widgets.com"
                               "171.26.23.22"
                               "aws:elasticache:us-east-1:852511987:cluster/api-stats-prod-003"
                               "9c09acd49a25"

            severity {string} -- How impacted the affected system is. Displayed to users in lists
                                 and influences the priority of any created incidents. Must be one
                                 of {info, warning, error, critical}

        Keyword Arguments:
            event_action {str} -- There are three types of events that PagerDuty recognizes, and
                                  are used to represent different types of activity in your
                                  monitored systems. (default: 'trigger')
                * trigger: When PagerDuty receives a trigger event, it will either open a new alert,
                           or add a new trigger log entry to an existing alert, depending on the
                           provided dedup_key. Your monitoring tools should send PagerDuty a trigger
                           when a new problem has been detected. You may send additional triggers
                           when a previously detected problem has occurred again.

                * acknowledge: acknowledge events cause the referenced incident to enter the
                               acknowledged state. While an incident is acknowledged, it won't
                               generate any additional notifications, even if it receives new
                               trigger events. Your monitoring tools should send PagerDuty an
                               acknowledge event when they know someone is presently working on the
                               problem.

                * resolve: resolve events cause the referenced incident to enter the resolved state.
                           Once an incident is resolved, it won't generate any additional
                           notifications. New trigger events with the same dedup_key as a resolved
                           incident won't re-open the incident. Instead, a new incident will be
                           created. Your monitoring tools should send PagerDuty a resolve event when
                           the problem that caused the initial trigger event has been fixed.

            dedup_key {string} -- Deduplication key for correlating triggers and resolves. The
                                  maximum permitted length of this property is 255 characters.

            timestamp {string} -- Timestamp (ISO 8601). When the upstream system detected / created
                                  the event. This is useful if a system batches or holds events
                                  before sending them to PagerDuty.

                                  Optional - Will be auto-generated by PagerDuty if not provided.

                                  Example:
                                  2015-07-17T08:42:58.315+0000

            component {string} -- The part or component of the affected system that is broken.

                                  Examples:
                                  "keepalive"
                                  "webping"
                                  "mysql"
                                  "wqueue"

            group {string} -- A cluster or grouping of sources. For example, sources
                              "prod-datapipe-02" and "prod-datapipe-03" might both be part of
                              "prod-datapipe"

                              Examples:
                              "prod-datapipe"
                              "www"
                              "web_stack"

            event_class {string} -- The class/type of the event.

                                    Examples:
                                    "High CPU"
                                    "Latency"
                                    "500 Error"

            custom_details {Dict[str, str]} -- Additional details about the event and affected
                                               system.

                                               Example:
                                               {"ping time": "1500ms", "load avg": 0.75 }
        """

        data = {
            "routing_key": self.routing_key,
            "event_action": event_action,
            "payload": {"summary": summary, "source": source, "severity": severity},
        }

        if dedup_key is not None:
            data["dedup_key"] = dedup_key

        if timestamp is not None:
            data["payload"]["timestamp"] = timestamp

        if component is not None:
            data["payload"]["component"] = component

        if group is not None:
            data["payload"]["group"] = group

        if event_class is not None:
            data["payload"]["class"] = event_class

        if custom_details is not None:
            data["payload"]["custom_details"] = custom_details

        return pypd.EventV2.create(data=data)


@resource(
    {
        "routing_key": Field(
            str,
            description="""The routing key provisions access to your PagerDuty service. You
                    will need to include the integration key for your new integration, as a
                    routing_key in the event payload.""",
        )
    },
    description="""This resource is for posting events to PagerDuty.""",
)
def pagerduty_resource(context):
    """A resource for posting events (alerts) to PagerDuty.

    Example:

    .. code-block:: python

        @solid(required_resource_keys={'pagerduty'})
        def pagerduty_solid(context):
            context.resources.pagerduty.EventV2_create(
                summary='alert from dagster'
                source='localhost',
                severity='error',
                event_action='trigger',
            )

        @pipeline(
            mode_defs=[ModeDefinition(resource_defs={'pagerduty': pagerduty_resource})],
        )
        def pd_pipeline():
            pagerduty_solid()

        execute_pipeline(
            pd_pipeline,
            {
                'resources': {
                    'pagerduty': {'config': {'routing_key': '0123456789abcdef0123456789abcdef'}}
                }
            },
        )
    """
    return PagerDutyService(context.resource_config.get("routing_key"))
