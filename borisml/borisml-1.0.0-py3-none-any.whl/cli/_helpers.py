DOCS = 'https://lightly.readthedocs.io'


def notify(task='train'):
    msg = ''
    msg += 'The borisml Python package has been renamed to lightly.\n'
    msg += f'Instead of boris-{task}, please try out lightly-{task}.\n'
    msg += f'Check out the documentation: {DOCS}'
    print(msg)
