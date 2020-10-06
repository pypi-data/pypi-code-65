from unittest import TestCase, mock

from agent.commands.dispatcher import dispatch_command


def return_data(data):
    return data


class TestCommandsDispatcher(TestCase):

    @mock.patch.dict('agent.commands.dispatcher.commands_dispatcher', {'command': return_data,
                                                                       'command2': None})
    def test_dispatch_command(self):
        # when - then
        self.assertEqual(dispatch_command('command', {'data': 'data'}), {'data': 'data'})
