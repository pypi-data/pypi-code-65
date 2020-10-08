import os
from google.cloud import translate

CTS = translate.TranslationServiceClient()
project_id = os.environ["GCP_PROJECT"]


def translate_text(source_sentence, target_language):

    parent = "projects/" + project_id + "/locations/global"

    translate_response = CTS.translate_text(
        parent=parent,
        mime_type="text/plain",
        contents=[source_sentence],
        target_language_code=target_language)

    target_sentence = translate_response.translations[0].translated_text
    detected_source_language = translate_response.translations[0].detected_language_code

    return {"source_language": detected_source_language, "target_sentence": target_sentence}
