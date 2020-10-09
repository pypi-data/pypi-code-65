from pdf_extractor.cleaning_encoding import clean_encoding
import textract

def text_extraction(file_path):
    """Extracting text from PDF

    Args:
        file_path (str): path of the PDF file to parse

    Returns:
        str: text retrieved from the PDF
    """

    text = textract.process(file_path, encoding="ascii")
    text = text.decode("utf-8")
    text = clean_encoding().clean(text)

    return text
