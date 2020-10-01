import os
import unittest

from jsonasobj import as_json

from biolinkml.generators.jsonldcontextgen import ContextGenerator
from biolinkml.generators.pythongen import PythonGenerator
from biolinkml.utils.yamlutils import as_rdf
from tests.test_issues.environment import env
from tests.utils.python_comparator import compare_python, compile_python
from tests.utils.test_environment import TestEnvironmentTestCase


class Issue80TestCase(TestEnvironmentTestCase):
    env = env

    def header(self, txt: str) -> str:
        return '\n' + ("=" * 20) + f" {txt} " + ("=" * 20)

    def test_issue_80(self):
        """ Make sure that types are generated as part of the output """
        env.generate_single_file('issue_80.py',
                                 lambda: PythonGenerator(env.input_path('issue_80.yaml')).serialize(),
                                 comparator=compare_python, value_is_returned=True)
        module = compile_python(env.expected_path('issue_80.py'))
        example = module.Person("http://example.org/person/17", "Fred Jones", 43)

        # Create output for various forms
        def output_generator(dirname) -> None:
            with open(os.path.join(dirname, 'issue_80.json'), 'w') as f:
                f.write(as_json(example))
            context = os.path.join(dirname, 'issue_80.context.jsonld')
            with open(context, 'w') as f:
                f.write(ContextGenerator(env.input_path('issue_80.yaml')).serialize())
            with open(os.path.join(dirname, 'issue_80.ttl'), 'w') as f:
                f.write(as_rdf(example, contexts=context).serialize(format="turtle").decode())

        env.generate_directory('issue_80', lambda dirname: output_generator(dirname))


if __name__ == '__main__':
    unittest.main()
