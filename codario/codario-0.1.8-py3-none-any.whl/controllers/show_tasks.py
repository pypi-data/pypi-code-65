from cement import Controller, ex, shell
import urllib3, json, getpass, os

class ShowTasks(Controller):
    class Meta:
        label = 'show-tasks'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='Display all tasks or tasks for a certain project.',
        arguments=[
            ([ '--key' ], { 'help' : 'The API Key.', 'action' : 'store', 'dest' : 'key' }),
            ([ '--workspace' ], { 'help' : 'Specify Workspace ID', 'action' : 'store', 'dest' : 'workspace' }),
            ([ '--project' ], { 'help' : 'Specify Project ID to get tasks from a certain project.', 'action' : 'store', 'dest' : 'project' }),
            ([ '--statuses' ], { 'help' : 'Specify the statuses of the tasks to be obtained. Available statuses:  "new_updates_available", "ready_to_test", "test_passed", "test_failed", "failed", "closed". By default will display all statuses except "closed".', 'action' : 'store', 'dest' : 'statuses' }),
            ([ '--mode' ], { 'help' : 'Choose "table" (by default) or "json".', 'action' : 'store', 'dest' : 'mode' })
        ]
    )
    def show_tasks(self):
        if self.app.pargs.key is None:
            if os.getenv('CODARIO_API_KEY', None) is not None:
                self.app.pargs.key = os.getenv('CODARIO_API_KEY')
            else:
                self.app.log.error('The argument "--key" is required.')
                return

        if self.app.pargs.workspace is None:
            self.app.log.error('The argument "--workspace" is required.')
            return

        fields = {
            'statuses': 'new_updates_available,ready_to_test,test_passed,test_failed,failed',
            'max_results': 20
        }

        if self.app.pargs.statuses is not None:
            fields['statuses'] = self.app.pargs.statuses

        if self.app.pargs.project is not None:
            fields['project'] = self.app.pargs.project

        http = urllib3.PoolManager()

        tasks = []

        while (True):
            r = http.request(
                'GET',
                self.app.base_url + '/workspaces/' + self.app.pargs.workspace + '/tasks',
                headers={'Content-Type': 'application/json', 'X-API-KEY': self.app.pargs.key},
                fields=fields
            )

            data = r.data.decode('utf-8')
            response = json.loads(data)

            if not response.get('tasks'):
                self.app.log.error(response.get('message'))
                return

            tasks = tasks + response['tasks']

            if response['next_boundary_id'] is None:
                break
            else:
                fields['boundary_id'] = response['next_boundary_id']

        if 'json' == self.app.pargs.mode:
            print(json.dumps(tasks))
        else:
            headers = ['ID', 'PROJECT', 'STATUS', 'UPDATES FOR VULNERABLE PACKAGES', 'CREATED']
            content = []

            for task in tasks:
                content.append([
                    task['id'],
                    task['project']['name'][:50],
                    task['status'],
                    'yes' if task['update_from_vulnerable_version'] else 'no',
                    task['created_at']
                ])

            self.app.render(content, headers=headers)
