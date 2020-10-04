class base_operators:
    def __init__(self, engine):
        self.engine = engine

    def expand(self, node):
        pass

    def end_state(self):
        pass

    def has_next(self, tasks):
        print(tasks)

    def err_suc_result_handler(self, expansion, err_handle, suc_handle):
        print(expansion)

    def merge(self, pathA, pathB):
        pass

    def SEQ(self, tasks, context, prev_path):
        def suc_handle(suc_out, prev_path=prev_path):
            # call for next
            if self.has_next(tasks):
                # x
                self.SEQ(tasks, self.merge(context, prev_path, suc_out))
            else:
                # last task was a success
                self.end_state(suc_out)

        def err_handle(err_out, prev_path=prev_path):
            self.end_state(err_out)

        return self.err_suc_result_handler(
            self.expand(tasks.pop(), context),
            err_handle=err_handle,
            suc_handle=suc_handle)
