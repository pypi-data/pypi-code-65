

class TaskContext:
    def extend(self, change):
        new_context = self.clone()
        # apply change
        return new_context

    def clone(self):
        pass
