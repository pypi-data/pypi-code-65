from pdfminer3.pdfdocument import PDFDocument
from pdfminer3.pdfparser import PDFParser


class DateMiner():

    def parse_date(self, pdf_path):
        """Retrieve the creation date of a PDF file

        Args:
            pdf_path (str): path to the PDF file to parse

        Returns:
            str: Year of creation
        """

        pdf = open(pdf_path, 'rb')
        parser = PDFParser(pdf)
        doc = PDFDocument(parser)
        creation_date = str(doc.info[0]["CreationDate"])

        try:
            creation_year = self.retrieve_year(creation_date)
        except IndexError:
            creation_year = None

        return creation_year


    def retrieve_year(self, creation_date):
        """From the creation date retrieved from the PDFDocument, parse it
        to retrienve solely the year of creation

        Args:
            creation_date (str): Full date of creation

        Returns:
            str: year of creation of the PDF file
        """

        creation_year = creation_date.split("D:")
        creation_year = creation_year[1][:4]

        return creation_year
