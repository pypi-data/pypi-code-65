""" spell checker bot based on Peter Norvig's spell checker """

from qary.etl.spell import make_spelling_corrections


class Skill:
    def reply(self, statement):
        r""" Chatbot "main" function to respond to a user command or statement

        >>> skill = Skill()
        >>> skill.reply('What is probabillity?')
        'What is probability?'
        >>> skill.reply('When was the telefone inventid?')
        'When was the telephone invented?'
        """
        return make_spelling_corrections(statement)
