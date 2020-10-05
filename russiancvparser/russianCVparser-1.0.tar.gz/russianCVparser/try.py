from russianCVparser import CVparser, Document, show_json

parser = CVparser()
document = Document('CVex.docx')
data = parser.parse_text(document.text)
show_json(data)