from gmrs.planner.outcome import Result


class VariabilityModelBuilder():
    macro_lib = None
    skill_lib = None

    def instantiate_variability_model(self, task, mission, unit,
                                      environment_context):
        context = environment_context.extend(task.parameters, unit.context,
                                             environment_context)
        # phase one
        controller = controller()
        gvm = self.bind_node(mission, context, controller)
        write_graph(gvm)

        # phase two
        def should_stop(model=model, controller=controller):
            return controller.checked_all()

        while not should_stop():
            controller.expand()
            curr_plan = controller.last_plan()
            print(evaluation(curr_plan))

        plan = controller.last_plan()

    def bind_node(self, node, context, controller):
        if is_leaf(node):
            if self.is_macro(node):
                macro = self.resolve_macro(node)
                return self.bind_node(macro, context, macro_lib, skill_lib)
            elif is_skill(node):
                # TODO build alternative if multiple skills
                return self.bind_skills(node)
        else:
            refinement = self.get_refinement(node)
            operator = self.get_operator(refinement)
            children = self.get_children(refinement)
            bound_self.bind_children(operator, children,
                                                  controller):
                

            
    def bind_children(self, operator, children, context, controller):
        def has_next():
            return True
        
        first_child = operator.get_first(children)
        queue = (first_child, context)

        for bind in queue:
            child_node, context = bind

            # sequential context
            bound_child_node = self.bind_node(child_node, context)
            result = bound_child_node.check(context)
            if not result.is_achievable:
                print('State not Handled - not achievable task. TODO')
                continue
            
            possible_outcomes = result.possible_outcomes
                
            for po in possible_outcomes:
                next_node = operator.next_node(child_node, po)
                next_context = context.extend(po)
                
                if is_end(next_node):


                new_binding = (next_node, next_context)
                queue.append(new_bindings)
        
        return next_context


    def is_leaf(node):
        return False


    def bind_child(self, child):
        return None

    def resolve(self, refinements):
        return None

    def parseName(self, nodeName):
        return None

    def resolve_macro(self, node):
        pass

    def is_skill(self, node):
        pass

    def bind_skills(self, node):
        pass

    def init_context_from_scenario(scenario):
        pass

    def write_graph(self):
        if self.is_write_graph_enable:
            print('writting graph')
