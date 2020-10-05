from django.apps import AppConfig

MODULE_NAME = "payment"

DEFAULT_CFG = {
    "gql_query_payments_perms": ["101401"],
}


class PaymentConfig(AppConfig):
    name = MODULE_NAME

    gql_query_payments_perms = []

    def _configure_permissions(self, cfg):
        ContributionConfig.gql_query_payments_perms = cfg[
            "gql_query_payments_perms"]

    def ready(self):
        from core.models import ModuleConfiguration
        cfg = ModuleConfiguration.get_or_default(MODULE_NAME, DEFAULT_CFG)
        self._configure_permissions(cfg)