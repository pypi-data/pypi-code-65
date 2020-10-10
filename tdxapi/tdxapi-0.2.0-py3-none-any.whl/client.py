import webbrowser

from tdxapi.dispatcher import Dispatcher, RequestsBackend
from tdxapi.managers.account import AccountManager
from tdxapi.managers.application import ApplicationManager
from tdxapi.managers.asset_app import AssetApplication
from tdxapi.managers.attachment import AttachmentManager
from tdxapi.managers.custom_attribute import CustomAttributeManager
from tdxapi.managers.custom_attribute_choice import CustomAttributeChoiceManager
from tdxapi.managers.functional_role import FunctionalRoleManager
from tdxapi.managers.report import ReportManager
from tdxapi.managers.resource_pool import ResourcePoolManager
from tdxapi.managers.security_role import SecurityRoleManager
from tdxapi.models.bases import TdxModelEncoder


class TdxClient(object):
    def __init__(self, organization, beid=None, wskey=None, use_sandbox=False):
        if beid is None or wskey is None:
            raise AttributeError("beid and wskey are required")

        self.dispatcher = Dispatcher(
            RequestsBackend(organization, beid, wskey, use_sandbox, TdxModelEncoder)
        )

        self.applications = ApplicationManager(self.dispatcher)
        self.accounts = AccountManager(self.dispatcher)
        self.attachments = AttachmentManager(self.dispatcher)
        self.attributes = CustomAttributeManager(self.dispatcher)
        self.attribute_choices = CustomAttributeChoiceManager(self.dispatcher)
        self.functional_roles = FunctionalRoleManager(self.dispatcher)
        self.resource_pools = ResourcePoolManager(self.dispatcher)
        self.reports = ReportManager(self.dispatcher)
        self.security_roles = SecurityRoleManager(self.dispatcher)

        self._org_apps = {}

        for a in self.applications.get_all():
            if a.app_class == "TDAssets":
                self._org_apps[a.id] = AssetApplication(self.dispatcher, a.id)

    def asset_app(self, app_id: int) -> AssetApplication:
        return self._org_apps[app_id]

    @staticmethod
    def docs():
        webbrowser.open_new_tab("https://app.teamdynamix.com/TDWebApi/")
