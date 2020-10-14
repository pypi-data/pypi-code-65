from cement import Controller, ex, shell
import urllib3, json, getpass, os

class ProcessTask(Controller):
    class Meta:
        label = 'process-task'
        stacked_type = 'embedded'
        stacked_on = 'base'

    @ex(
        help='Process a task.',
        arguments=[
            ([ '--key' ], { 'help' : 'The API Key.', 'action' : 'store', 'dest' : 'key' }),
            ([ '--task' ], { 'help' : 'The Task ID.', 'action' : 'store', 'dest' : 'task' }),
            ([ '--status' ], { 'help' : 'The destination status to a task.', 'action' : 'store', 'dest' : 'status' })
        ]
    )
    def process_task(self):
        if self.app.pargs.key is None:
            if os.getenv('CODARIO_API_KEY', None) is not None:
                self.app.pargs.key = os.getenv('CODARIO_API_KEY')
            else:
                self.app.log.error('The argument "--key" is required.')
                return

        if self.app.pargs.status is None:
            self.app.log.error('The argument "--status" is required.')
            return

        if self.app.pargs.task is None:
            self.app.log.error('The argument "--task" is required.')
            return

        body = {
            'status': self.app.pargs.status
        }

        http = urllib3.PoolManager()

        r = http.request(
            'PATCH',
            self.app.base_url + '/workspaces/WID/projects/PID/tasks/' + self.app.pargs.task,
            headers={'Content-Type': 'application/json', 'X-API-KEY': self.app.pargs.key},
            body=json.dumps(body).encode('utf-8')
        )

        data = r.data.decode('utf-8')
        response = json.loads(data)

        if response.get('success') and response['success'] is True:
            self.app.log.info(response['message'])
        else:
            self.app.log.error(response['message'])
