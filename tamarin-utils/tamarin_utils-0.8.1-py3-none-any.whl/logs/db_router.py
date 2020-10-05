class LogRouter:
    route_app_labels = ['logs']

    def db_for_read(self, model, **hints):
        """ reading Log from log """
        if model._meta.app_label in self.route_app_labels:
            return 'log'
        return None

    def db_for_write(self, model, **hints):
        """ writing Log to log """
        if model._meta.app_label in self.route_app_labels:
            return 'log'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the log apps is
        involved.
        """
        if (
                obj1._meta.app_label in self.route_app_labels or
                obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the log apps only appear in the
        'log' database.
        """
        if app_label in self.route_app_labels:
            return db == 'log'
        return None


