import inspect
from typing import Callable, List

import libcst as cst


class LambdaCollector(cst.CSTVisitor):
    def __init__(self):
        self.lambdas = []

    def visit_Lambda(self, node: cst.Lambda):
        self.lambdas.append(node)


def _code_obj_similar(c1, c2):
    if c1.co_argcount != c2.co_argcount:
        return False
    if c1.co_cellvars != c2.co_cellvars:
        return False
    if c1.co_code != c2.co_code:
        return False
    if c1.co_consts != c2.co_consts:
        return False
    if c1.co_freevars != c2.co_freevars:
        return False
    if c1.co_kwonlyargcount != c2.co_kwonlyargcount:
        return False
    if c1.co_names != c2.co_names:
        return False
    return True


def _gen_lambda_code_obj(cst_module, cst_lambda: cst.Lambda):
    code = cst_module.code_for_node(cst_lambda)
    outer_module_code_obj = compile(code, '', 'single')
    lambda_code_obj = outer_module_code_obj.co_consts[0]
    return lambda_code_obj


def _find_matching_lambda(lambda_code_obj_needle,
                          lambda_code_objs_in_src_line: List[cst.Lambda],
                          cst_module) -> cst.Lambda:
    for cst_lambda in lambda_code_objs_in_src_line:
        lambda_code_obj = _gen_lambda_code_obj(cst_module, cst_lambda)
        if _code_obj_similar(lambda_code_obj, lambda_code_obj_needle):
            return cst_lambda
    return None


def get_lambda_source(lambda_callable: Callable):
    code_obj = lambda_callable.__code__
    source_line = inspect.getsourcelines(lambda_callable)[0][0].lstrip()
    cst_module = cst.parse_module(source_line)
    visitor = LambdaCollector()
    cst_module.visit(visitor)
    lambdas = visitor.lambdas
    matching_lambda = _find_matching_lambda(code_obj, lambdas, cst_module)
    if not matching_lambda:
        raise Exception('Unable to find matching lambda, this should not happen, please report a bug.')
    return cst_module.code_for_node(matching_lambda)
