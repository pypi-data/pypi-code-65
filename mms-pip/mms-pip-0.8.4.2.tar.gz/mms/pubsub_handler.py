from google.cloud import pubsub
import hashlib
import time
import json
from datetime import datetime
import pytz


class Pubsub(object):

    def __init__(self, project_id=None, publish_batch_max_messages=100, publish_batch_max_baytes=1024, publish_batch_max_latency=10):
        self.project_id = project_id
        self.batch_pubsub_settings = pubsub.types.BatchSettings(
            max_messages=publish_batch_max_messages,
            max_bytes=publish_batch_max_baytes,  # in kB
            max_latency=publish_batch_max_latency,  # in ms
        )
        self.publisher_client = pubsub.PublisherClient(self.batch_pubsub_settings)
        self.futures = dict()

    @staticmethod
    def get_time(time_zone='UTC'):
        tz = pytz.timezone(time_zone)
        return datetime.now(tz)

    def create_topic(self, topic_name: str, project_id=None):
        if project_id is None:
            project_id = self.project_id
        topic_path = "projects/{}/topics/{}".format(project_id, topic_name)
        return self.publisher_client.create_topic(request={"name": topic_path})

    def create_pull_subscription(self, subscription_name: str, topic_path: str, project_id=None, ack_deadline_seconds=10):
        if project_id is None:
            project_id = self.project_id
        subscription_path = "projects/{}/subscriptions/{}".format(project_id, subscription_name)
        subscriber_client = pubsub.SubscriberClient()
        return subscriber_client.create_subscription(request={"name": subscription_path,
                                                              "topic": topic_path,
                                                              "ack_deadline_seconds": ack_deadline_seconds,
                                                              "expiration_policy": {"ttl": None}})

    def publish_messages(self, data, topic_path: str, wait_until_all_published=True, encoding="utf-8"):

        def get_callback(future, key):
            def callback(future):
                message_id = future.result()
                self.futures.pop(key)
            return callback

        for item in data:
            key = hashlib.sha256("{}-{}".format(item, str(self.get_time())).encode()).hexdigest()
            self.futures.update({key: None})
            # When you publish a message, the client returns a future.
            future = self.publisher_client.publish(topic_path, json.dumps(item).encode(encoding))
            self.futures[key] = future
            # Publish failures shall be handled in the callback function.
            future.add_done_callback((get_callback(future, key)))

        if wait_until_all_published:
            # Wait for all the publish futures to resolve before exiting.
            self.wait_for_publishing()

    def wait_for_publishing(self):
        while self.futures:
            time.sleep(0.01)

    def publish_message(self, data, topic_path: str, encoding="utf-8"):
        data = json.dumps(data).encode(encoding)
        future = self.publisher_client.publish(topic_path, data)
        return "{}".format(future.result())  # message_id


if __name__ == '__main__':


    # Init pubsub_handler with default project:
    pubsub_handler = Pubsub(project_id="playground-josef")


    # Create Pubsub Topic in default project:
    topic = pubsub_handler.create_topic("test-topic")
    print(topic)

    # Create Pubsub Topic in other project:
    topic = pubsub_handler.create_topic("test-topic", "spielwiese-tobias")
    print(topic)

    # Create pull Subscription in default project:
    subscription = pubsub_handler.create_pull_subscription(subscription_name="test-subs",
                                                           topic_path="projects/playground-josef/topics/temp-test",
                                                           ack_deadline_seconds=100)
    print(subscription)

    # Create pull Subscription in other project:
    subscription = pubsub_handler.create_pull_subscription(subscription_name="test-subs",
                                                           project_id="spielwiese-tobias",
                                                           topic_path="projects/spielwiese-tobias/topics/test-topic",
                                                           ack_deadline_seconds=30)
    print(subscription)


    # Publish messages - batch (if one bundle to publish) - optional: encoding (default="utf-8"):
    data = [{"column1": i, "column2": "value {}".format(i)} for i in range(10000)]
    pubsub_handler.publish_messages(data=data,
                                    topic_path="projects/playground-josef/topics/temp-test",
                                    wait_until_all_published=True)

    # Publish messages - batch (if more than one bundle to publish) - optional: encoding (default="utf-8"):
    data = [{"column1": i, "column2": "value {}".format(i)} for i in range(10000)]
    for i in range(10):
        pubsub_handler.publish_messages(data=data,
                                        topic_path="projects/playground-josef/topics/temp-test",
                                        wait_until_all_published=False)
    pubsub_handler.wait_for_publishing()
    
    # Publish message - just one message, waiting until message is published - optional: encoding (default="utf-8"). 
    data = {"column1": 1, "column2": "value 1"}
    message_id = pubsub_handler.publish_message(data=data, topic_path="projects/playground-josef/topics/temp-test")
    print(message_id)

