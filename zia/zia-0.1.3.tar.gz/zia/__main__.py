import fire
from zia import *

class ZscalerInternetAccess(object):
    def __init__(self, profile='default'):
        self._session = Session(profile=profile)
        # self.activation = Activation(self.session)
        # self.admin_audit_logs = AdminAuditLogs(self.session)
        # self.location = Locations(self.session)
        # self.security = Security(self.session)
        # self.datacenters = Datacenters(self.session)
        # self.sandbox = Sandbox(self.session)
        # self.ssl = Ssl(self.session)
        # self.user = User(self.session)
        # self.gre = Gre(self.session)
        # self.vpn_credentials = VpnCredentials(self.session)
        self.policies = UrlFilteringPolicies(self._session, 'str')
        self.categories = UrlCategories(self._session, 'str')
    def authenticate(self):
        self._session.authenticate()

def main():
    z = ZscalerInternetAccess()
    z.authenticate()
    fire.Fire(z)
    return 0

if __name__ == "__main__":
    main()
