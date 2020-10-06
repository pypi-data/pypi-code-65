from enstadtpfaff_platform_mock_api.event import Event
from enstadtpfaff_platform_mock_api.util.topic_util import name_for_shared_topic


class ChatMessagesEventBuilder:
    SHARED_TOPIC_ID = "chat-messages"
    CHAT_MESSAGES_TOPIC = name_for_shared_topic(SHARED_TOPIC_ID)

    @staticmethod
    def chat_message(application_name: str, from_: str, to: str, message: str) -> Event:
        return Event(
            topic=ChatMessagesEventBuilder.CHAT_MESSAGES_TOPIC,
            payload={
                'senderApplication': application_name,
                'from': from_,
                'to': to,
                'message': message
            }
        )
