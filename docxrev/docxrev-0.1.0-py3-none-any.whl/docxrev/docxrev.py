"""
Microsoft Word review tools (comments, markup, etc.) with Python
"""

from docxrev import com
from docxrev.com import Document


def quit_word():
    """Quit Word."""
    com.WORD.Quit()


def quit_word_safely():
    """Quit Word if no documents are open."""
    if not com.WORD.Documents:
        quit_word()


def get_active_document() -> Document:
    """Get the current document."""
    return Document(com.WORD.ActiveDocument.FullName)
