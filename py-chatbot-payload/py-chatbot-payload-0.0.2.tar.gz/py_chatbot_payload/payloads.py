# from abc import ABC
import inspect
from .helpers import check_type
from .facebook_chat import *
from .line_chat import *


def parse_line(rows: list):
    result = []
    for row in rows:
        data = row["data"]
        if row["type"] == "text":
            result.append(line_text_message(message=data.get("text", None)))

        if row["type"] == "sticker":
            result.append(line_sticker_message(package_id=data.get("packageId", None),
                                               sticker_id=data.get("stickerId", None)))

        if row["type"] == "image":
            result.append(line_image_message(original_content_url=data.get("original_content_url", None),
                                             preview_image_url=data.get("preview_image_url", None)))

        if row["type"] == "video":
            result.append(line_video_message(original_content_url=data.get("original_content_url", None),
                                             preview_image_url=data.get("preview_image_url", None),
                                             tracking_id=data.get("tracking_id", None)))

    return result


def parse_facebook(rows: list):
    result = []
    for row in rows:
        data = row["data"]
        data_type = row["type"]

        if data_type == "text":
            result.append(facebook_text_message(message=data.get("text", None)))

        if data_type == "image":
            result.append(facebook_image_message(attachment_id=data.get("attachment_id", None),
                                                 url=data.get("url", None)))

        if data_type == "video":
            result.append(
                facebook_video_message(attachment_id=data.get("attachment_id", None),
                                       url=data.get("url", None)))

    return result


class Payloads:
    PLATFORM_BOTNOI_SME = "botnoi_sme"
    SUPPORTED_PLATFORMS = [PLATFORM_BOTNOI_SME]
    CHAT_BOT_LINE = "line"
    CHAT_BOT_FACEBOOK = "facebook"
    SUPPORTED_CHAT_BOTS = [CHAT_BOT_LINE, CHAT_BOT_FACEBOOK]

    def __init__(self, chat_bots: list = ["line"], platform: str = PLATFORM_BOTNOI_SME):
        """
        :param chatbots: list of available chatbots to create payloads
        :param platform: specify platform to use (now support only botnoi-sme)
        """
        # Verify parameter types
        check_type(chat_bots, list, can_be_none=False)
        check_type(platform, str, can_be_none=False)

        # Verify supported chatbot and platform
        if not set(chat_bots).issubset(self.SUPPORTED_CHAT_BOTS):
            raise Exception(f"chatbots {chat_bots} are not supported in {self.SUPPORTED_CHAT_BOTS}")

        if platform not in self.SUPPORTED_PLATFORMS:
            raise Exception("Platform {platform} is not supported")

        # keep internal variables
        self.__platform = platform
        self.__chat_bots = chat_bots
        self.__data = {k: [] for k in self.__chat_bots}

    def __iter__(self):
        # should translate into specific platform's payloads
        keys = self.__data.keys()
        data = {}
        for key in keys:
            # self.CHAT_BOT_LINE
            # print("Key: ", key)
            # print("Data", self.__data[key])
            if key == self.CHAT_BOT_LINE:
                data[key] = parse_line(self.__data[key])

            # self.CHAT_BOT_FACEBOOK
            if key == self.CHAT_BOT_FACEBOOK:
                data[key] = parse_facebook(self.__data[key])

            yield key, data[key]

    def __check_if_chatbot_is_available(self, chat_bot, possible_chat_bots=[]):
        is_supported_chatbot = chat_bot in self.__chat_bots and chat_bot in possible_chat_bots
        if not is_supported_chatbot:
            raise Exception(f"Chatbot {chat_bot} not supported by function {inspect.stack()[1][3]}")

    def __raise_exception(self, exception_description: str):
        raise Exception(f"Exception: {exception_description} from {inspect.stack()[1][3]}")

    # public functions
    def text_message(self, message: str, chat_bot: str = CHAT_BOT_LINE):
        """
        Create a text message payload

        :param message: (str) Text message to reply
        :param chat_bot: (str) one of instance.CHAT_BOT_LINE, instance.CHAT_BOT_FACEBOOK
        :return: None
        """
        self.__check_if_chatbot_is_available(chat_bot=chat_bot,
                                             possible_chat_bots=[self.CHAT_BOT_LINE, self.CHAT_BOT_FACEBOOK])
        self.__data[chat_bot].append({
            "type": "text",
            "data": {"text": message}
        })

    def sticker_message(self, package_id: str, sticker_id: str, chat_bot: str = CHAT_BOT_LINE):
        """
        Create a sticker message payload (now available only line chatbot)
        :param package_id: (str) Sticker package id
        :param sticker_id: (str) Sticker id
        :param chat_bot: (str) only instance.CHAT_BOT_LINE
        :return: None
        """
        self.__check_if_chatbot_is_available(chat_bot=chat_bot,
                                             possible_chat_bots=[self.CHAT_BOT_LINE])

        self.__data[chat_bot].append({
            "type": "sticker",
            "data": {
                "packageId": package_id,
                "stickerId": sticker_id
            }
        })

    def image_message(self, **kwargs):
        """
        Create a image message payload
        :param kwargs:
            [line] (str)original_content_url, (str)preview_image_url are required
            [facebook] (str)attachment_id or (str)url is required
        :return: None
        """
        chat_bot = kwargs["chatbot"]
        self.__check_if_chatbot_is_available(chat_bot=chat_bot,
                                             possible_chat_bots=[self.CHAT_BOT_LINE, self.CHAT_BOT_FACEBOOK])

        data = {"type": "image", "data": {}}
        if chat_bot == self.CHAT_BOT_LINE:
            original_content_url = kwargs["original_content_url"]
            preview_image_url = kwargs["preview_image_url"]
            check_type(original_content_url, str, can_be_none=False)
            check_type(preview_image_url, str, can_be_none=False)
            data['data'] = {
                "original_content_url": original_content_url,
                "preview_image_url": preview_image_url
            }

        if chat_bot == self.CHAT_BOT_FACEBOOK:
            attachment_id = kwargs["attachment_id"] if "attachment_id" in kwargs else None
            url = kwargs["url"] if "url" in kwargs else None
            check_type(attachment_id, str, can_be_none=True)
            check_type(url, str, can_be_none=True)
            if attachment_id is None and url is None:
                self.__raise_exception("attachment_id or url must be specified in chatbot {self.CHAT_BOT_FACEBOOK}")

            if attachment_id is not None and url is not None:
                self.__raise_exception("Please specify only attachment_id or url")

            if attachment_id is not None:
                data["data"] = {
                    "attachment_id": attachment_id
                }

            if url is not None:
                data["data"] = {
                    "url": url
                }

        self.__data[chat_bot].append(data)

    def video_message(self, **kwargs):
        """

        :param kwargs:
            [line] (str)original_content_url, (str)preview_image_url are required and (str)tracking_id is optional
            [facebook] (str)attachment_id or (str)url is required
        :return:
        """
        chat_bot = kwargs["chatbot"]
        self.__check_if_chatbot_is_available(chat_bot=chat_bot,
                                             possible_chat_bots=[self.CHAT_BOT_LINE, self.CHAT_BOT_FACEBOOK])

        data = {"type": "video", "data": {}}
        if chat_bot == self.CHAT_BOT_LINE:
            original_content_url = kwargs.get("original_content_url", None)
            preview_image_url = kwargs.get("preview_image_url", None)
            tracking_id = kwargs.get("tracking_id", None)

            check_type(original_content_url, str, can_be_none=False)
            check_type(preview_image_url, str, can_be_none=False)
            check_type(tracking_id, str, can_be_none=True)

            data['data'] = {
                "original_content_url": original_content_url,
                "preview_image_url": preview_image_url,
                "tracking_id": tracking_id
            }

        if chat_bot == self.CHAT_BOT_FACEBOOK:
            attachment_id = kwargs.get("attachment_id", None)
            url = kwargs.get("url", None)
            check_type(attachment_id, str, can_be_none=True)
            check_type(url, str, can_be_none=True)
            if attachment_id is None and url is None:
                self.__raise_exception("attachment_id or url must be specified in chatbot {self.CHAT_BOT_FACEBOOK}")

            if attachment_id is not None and url is not None:
                self.__raise_exception("Please specify only attachment_id or url")

            if attachment_id is not None:
                data["data"] = {
                    "attachment_id": attachment_id
                }

            if url is not None:
                data["data"] = {
                    "url": url
                }

        self.__data[chat_bot].append(data)
