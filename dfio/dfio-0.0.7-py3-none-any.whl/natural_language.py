from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
from google.protobuf.json_format import MessageToJson

NLS = language.LanguageServiceClient()


def analyze_syntax(input_string):
    input_document = types.Document(content=input_string,
                                    type=enums.Document.Type.PLAIN_TEXT)

    document_syntax = NLS.analyze_syntax(input_document)
    document_syntax_json = MessageToJson(document_syntax)
    return document_syntax_json
