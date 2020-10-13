from .helpers import check_type as __type_check


def line_text_message(message: str):
    __type_check(message, str, can_be_none=False)
    return {
        "type": "text",
        "text": message[:5000]
    }


def line_sticker_message(package_id: str, sticker_id: str):
    __type_check(package_id, str, can_be_none=False)
    __type_check(sticker_id, str, can_be_none=False)
    return {
        "type": "sticker",
        "packageId": package_id,
        "stickerId": sticker_id
    }


def line_image_message(original_content_url: str, preview_image_url: str):
    __type_check(original_content_url, str, can_be_none=False)
    __type_check(preview_image_url, str, can_be_none=False)
    return {
        "type": "image",
        "originalContentUrl": original_content_url,
        "previewImageUrl": preview_image_url
    }


def line_video_message(original_content_url: str, preview_image_url: str, tracking_id: str):
    __type_check(original_content_url, str, can_be_none=False)
    __type_check(preview_image_url, str, can_be_none=False)
    __type_check(tracking_id, str, can_be_none=True)

    return {
        "type": "video",
        "originalContentUrl": original_content_url,
        "previewImageUrl": preview_image_url,
        "tracking_id": tracking_id
    }
