""" Converts pdf to text """

import PyPDF2


def pdf_to_text(input_pdf, output_text):
    """
        converts pdf to text

        Param:
        str: input_file
        str: output_file

    """
    pdf = PyPDF2.PdfFileReader(input_pdf)

    with open(output_text, "w", encoding="utf-8") as o:

        for page in range(pdf.getNumPages()):
            data = pdf.getPage(page).extractText()
            o.write(data)
