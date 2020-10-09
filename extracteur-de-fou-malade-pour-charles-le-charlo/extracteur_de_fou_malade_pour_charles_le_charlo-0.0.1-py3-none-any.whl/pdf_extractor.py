import pdf_extractor.text_summarizer as ts
from pdf_extractor.date_miner import DateMiner
from pdf_extractor.text_extraction import text_extraction

class PDFExtractor():
    """Retrieve the content, the summary and the year of publication of a given
    PDF
    """

    def __init__(self):
        self.dm = DateMiner()
    
    def extract_data(self, pdf_path, n_sentences, force_summarization=False):
        """Extract data from the PDF

        Args:
            pdf_path (str): path to the PDF file to parse
            n_sentences (int): Number of sentences considered for the resume
            force_summarization (bool, optional): Whether to force the parsing
            for non-english PDF. Defaults to False.

        Returns:
            dict: Extracted data
        """

        pdf_content = text_extraction(pdf_path)
        pdf_summary = ts.summarize_text(
            text=pdf_content, n_sentences=n_sentences, force=force_summarization)
        pdf_year = self.dm.parse_date(pdf_path)
        data = {
            "content": pdf_content,
            "summary": pdf_summary,
            "yearOfPublication": pdf_year
        }

        return data


