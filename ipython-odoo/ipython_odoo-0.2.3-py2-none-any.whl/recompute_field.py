

def recompute_field(model_name, field_name):
    model = env['stock.picking']
    env.add_todo(model._fields['production_number'], model.search([]))
    model.recompute()
