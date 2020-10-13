import argparse
import os
import pathlib
import datetime
from string import Template

import sys

APP_DEC = """                                                                           
YYYYYYY       YYYYYYY          QQQQQQQQQ           NNNNNNNN        NNNNNNNN
Y:::::Y       Y:::::Y        QQ:::::::::QQ         N:::::::N       N::::::N
Y:::::Y       Y:::::Y      QQ:::::::::::::QQ       N::::::::N      N::::::N
Y::::::Y     Y::::::Y     Q:::::::QQQ:::::::Q      N:::::::::N     N::::::N
YYY:::::Y   Y:::::YYY     Q::::::O   Q::::::Q      N::::::::::N    N::::::N
   Y:::::Y Y:::::Y        Q:::::O     Q:::::Q      N:::::::::::N   N::::::N
    Y:::::Y:::::Y         Q:::::O     Q:::::Q      N:::::::N::::N  N::::::N
     Y:::::::::Y          Q:::::O     Q:::::Q      N::::::N N::::N N::::::N
      Y:::::::Y           Q:::::O     Q:::::Q      N::::::N  N::::N:::::::N
       Y:::::Y            Q:::::O     Q:::::Q      N::::::N   N:::::::::::N
       Y:::::Y            Q:::::O  QQQQ:::::Q      N::::::N    N::::::::::N
       Y:::::Y            Q::::::O Q::::::::Q      N::::::N     N:::::::::N
       Y:::::Y            Q:::::::QQ::::::::Q      N::::::N      N::::::::N
    YYYY:::::YYYY          QQ::::::::::::::Q       N::::::N       N:::::::N
    Y:::::::::::Y            QQ:::::::::::Q        N::::::N        N::::::N
    YYYYYYYYYYYYY              QQQQQQQQ::::QQ      NNNNNNNN         NNNNNNN
                                       Q:::::Q                             
                                        QQQQQQ                             
                                                                           
"""

templates = {
    'project': [
        '$gitignore',
        '$dockerignore',
        '__init__$py',
        'entrypoint$sh',
        'entrypoint_test$sh',
        'gunicorn_config$py',
        'gunicorn_config_test$py',
        'infer$dockerfile',
        'infer_test$dockerfile',
        'model_url_config_local$yml',
        'model_url_config_online$yml',
        'project_config$py',
        'project_config_flask$py',
        'project_train$py',
        'requirements$txt',
        'template_flask$py',
        'template_flask_local$py',
    ],
}


def capitalize(name):
    return name.capitalize()


def get_args_parser():
    from yqn_cli import __version__
    parser = argparse.ArgumentParser(description='create project base on yqn pytorch framework')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-n', '--name', type=str, required=True, help='project name exp: "key_attention"')
    parser.add_argument('-i', '--app_id', type=str, required=True, help='app_id name exp: "22001"')
    parser.add_argument('-o', '--out', type=str, default='./', help='file output path')
    parser.add_argument('-a', '--author', type=str, default='yqn', help='author')
    return parser


def get_name_for_class(module_name):
    return ''.join(list(map(capitalize, module_name.split('_'))))


def output_gen_files(args, template_dir):
    project_name, app_id, output_dir, author = args.name, args.app_id, args.out, args.author
    today = datetime.datetime.now().strftime('%Y%m%d')
    for sub_dir in templates:
        files = templates[sub_dir]
        for file in files:
            lines = []
            template_file_path = os.path.join(template_dir,
                                              sub_dir,
                                              file)
            out_name = file.replace("template_", project_name + "_").replace("$", ".")
            gen_file_path = os.path.join(output_dir, out_name)
            template_file = open(template_file_path)
            gen_file = open(gen_file_path, "w")
            tmp = Template(template_file.read())
            lines.append(tmp.safe_substitute(project_name=project_name, today=today, app_id=app_id))
            gen_file.writelines(lines)
            template_file.close()
            gen_file.close()


def parse_command(parser_fn=get_args_parser, printed=True):
    root_project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    # 项目次目录
    module_dir = os.path.join(root_project_dir, "yqn_project_cli")
    print(module_dir)
    template_dir = os.path.join(module_dir, 'template')
    args = parser_fn().parse_args()
    if printed:
        param_str = '\n'.join(['%20s = %s' % (k, v) for k, v in sorted(vars(args).items())])
        print('usage: %s\n%20s   %s\n%s\n%s\n' % (' '.join(sys.argv), 'ARG', 'VALUE', '_' * 50, param_str))
    output_gen_files(args, template_dir)


def main():
    print(APP_DEC)
    parse_command()


if __name__ == "__main__":
    main()
