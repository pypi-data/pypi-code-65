from cement import Controller, ex, shell
import urllib3, json, getpass, os

class ShowProjects(Controller):
    class Meta:
        label = 'show-projects'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='Display all projects.',
        arguments=[
            ([ '--key' ], { 'help' : 'The API Key.', 'action' : 'store', 'dest' : 'key' }),
            ([ '--workspace' ], { 'help' : 'Specify Workspace ID', 'action' : 'store', 'dest' : 'workspace' }),
            ([ '--mode' ], { 'help' : 'Choose "table" (by default) or "json".', 'action' : 'store', 'dest' : 'mode' })
        ]
    )
    def show_projects(self):
        if self.app.pargs.key is None:
            if os.getenv('CODARIO_API_KEY', None) is not None:
                self.app.pargs.key = os.getenv('CODARIO_API_KEY')
            else:
                self.app.log.error('The argument "--key" is required.')
                return

        if self.app.pargs.workspace is None:
            self.app.log.error('The argument "--workspace" is required.')
            return

        http = urllib3.PoolManager()

        r = http.request(
            'GET',
            self.app.base_url + '/workspaces/' + self.app.pargs.workspace + '/projects',
            headers={'Content-Type': 'application/json', 'X-API-KEY': self.app.pargs.key}
        )

        data = r.data.decode('utf-8')
        response = json.loads(data)

        if response.get('projects'):
            if 'json' == self.app.pargs.mode:
                print(json.dumps(response['projects']))
            else:
                headers = ['ID', 'NAME', 'MANAGER', 'TASKS']
                content = []

                for project in response['projects']:
                    content.append([
                        project['id'],
                        project['name'],
                        project['manager'],
                        'for inspection: ' + str(project['tasks_for_inspection']) + ' / ' + ('has vulnerabilities' if (project['has_tasks_with_vulnerabilities'] or project['has_vulnerable_packages_without_tasks']) else 'secure'),
                    ])

                self.app.render(content, headers=headers)

        else:
            self.app.log.error(response.get('message'))
