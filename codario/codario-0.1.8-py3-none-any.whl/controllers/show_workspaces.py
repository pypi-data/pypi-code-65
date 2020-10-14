from cement import Controller, ex, shell
import urllib3, json, getpass, os

class ShowWorkspaces(Controller):
    class Meta:
        label = 'show-workspaces'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='Display all workspaces.',
        arguments=[
            ([ '--key' ], { 'help' : 'The API Key.', 'action' : 'store', 'dest' : 'key' }),
            ([ '--mode' ], { 'help' : 'Choose "table" (by default) or "json".', 'action' : 'store', 'dest' : 'mode' })
        ]
    )
    def show_workspaces(self):
        if self.app.pargs.key is None:
            if os.getenv('CODARIO_API_KEY', None) is not None:
                self.app.pargs.key = os.getenv('CODARIO_API_KEY')
            else:
                self.app.log.error('The argument "--key" is required.')
                return

        http = urllib3.PoolManager()

        r = http.request(
            'GET',
            self.app.base_url + '/workspaces',
            headers={'Content-Type': 'application/json', 'X-API-KEY': self.app.pargs.key}
        )

        data = r.data.decode('utf-8')
        response = json.loads(data)

        if response.get('workspaces'):
            if 'json' == self.app.pargs.mode:
                print(json.dumps(response['workspaces']))
            else:
                headers = ['ID', 'NAME']
                content = []

                for workspace in response['workspaces']:
                    content.append([
                        workspace['id'],
                        workspace['name'],
                    ])

                self.app.render(content, headers=headers)
        else:
            self.app.log.error(response.get('message'))
