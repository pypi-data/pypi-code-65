from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import warnings
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from future import standard_library
standard_library.install_aliases()
from gcloud.rest.auth import BUILD_GCLOUD_REST  # pylint: disable=no-name-in-module


def test_importable():
    assert True


if BUILD_GCLOUD_REST:
    pass


else:
    from gcloud.rest.pubsub.subscriber_client import FlowControl
    from gcloud.rest.pubsub.subscriber_client import SubscriberClient
    from gcloud.rest.pubsub.subscriber_message import SubscriberMessage  # pylint: disable=unused-import


    def test_construct_subscriber_client():
        SubscriberClient()


    def test_construct_flow_control():
        FlowControl()


    def test_flow_control_getattr():
        f = FlowControl(
            max_messages=1,
            max_bytes=100,
            max_lease_duration=10,
            max_duration_per_lease_extension=0)

        assert f.max_messages == 1
        assert f.max_bytes == 100
        assert f.max_lease_duration == 10
        assert f.max_duration_per_lease_extension == 0
