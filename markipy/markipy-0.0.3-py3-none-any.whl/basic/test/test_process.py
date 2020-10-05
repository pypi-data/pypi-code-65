import unittest
import HtmlTestRunner

from markipy.basic import Process

_process_ps_ = {'class': 'ProcessPS', 'version': 1}


class PS(Process):
    def __init__(self, cmd):
        Process.__init__(self, cmd=cmd, process_name='Unittest.PS')
        self._init_atom_register_class(_process_ps_)
        self.ps = []

    def stdout_callback(self, line):
        self.ps.append(line)


class TestProcess(unittest.TestCase):

    def test_process(self):
        p = Process('Unittest')
        p.execute(['ls', '-ashu'])

    def test_custom_process(self):
        ps_cmd = ['ps', '-aux']
        ps = PS(cmd=ps_cmd)
        ps.start()
        ps.log.debug(ps.ps)


if __name__ == '__main__':
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='/tmp/markpy_unittest/'))
