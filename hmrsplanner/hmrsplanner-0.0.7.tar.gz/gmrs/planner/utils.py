

def evaluate(model, context):
    outcomes = None
    if is_leaf(model):
        skill = get_skill(model, context)
        outcomes = evaluate_task(model, skill)
    else:
        pass

    outcomes = evaluate(model, context)
    return outcomes


def evaluate_task(task, skill):
    pass


def get_task(model):
    return model


def is_leaf(model):
    return True


def get_skill(task, context):
    return context.get(Skill, task['label'])

