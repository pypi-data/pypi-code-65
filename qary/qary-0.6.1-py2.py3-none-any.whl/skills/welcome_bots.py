""" Chatbot that moves the conversation along with a helpful prompt """


class Bot:
    """ A chatbot that can reply to greetings to move conversation along

    >>> b = Bot()
    >>> b.reply('Hi!')
    'How can I help?'
    >>> b.greetings = ('hello',)
    >>> b.reply('Hi')
    >>> b.reply('Hello!')
    'How can I help?'
    >>> b = Bot(('goodbye',))
    >>> b.reply('hi')
    >>> b.reply('Goodbye')
    'How can I help?'
    """
    greetings = (
        'hi', 'hello', "what's up", 'yo', 'konichiwa', 'wusup',
    )

    def __init__(self, greetings=None):
        if greetings is not None:
            self.greetings = greetings
        self.greetings = tuple(g.lower() for g in self.greetings)

    def reply(self, statement):
        r""" Reply to any uninformative greeting with helpful responses that move the conversation along

        >>> reply('Hi!')
        'How can I help?'
        >>> reply('Who was Ginsberg?')
        >>> reply('Hello!')
        'How can I help?'
        """
        replies = [
            (.1, 'How can I help?'),
        ]

        statement = statement.lower()
        for g in self.greetings:
            if statement.startswith(g):
                return replies
        return None
