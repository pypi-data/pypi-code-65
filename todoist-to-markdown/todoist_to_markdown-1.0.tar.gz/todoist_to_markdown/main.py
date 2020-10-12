from todoist_to_markdown.task import Task
from typing import Dict
from todoist_to_markdown.todoist import get_today_tasks
from todoist_to_markdown.argument import get_argument


def cli():
    subcommand = get_argument('subcommand')
    if subcommand == 'today':
        today_items: Dict[str, Task] = get_today_tasks()
        for today_item in today_items.values():
            print(f'- [ ] {today_item.title}')
            for sub_task in today_item.sub_tasks:
                print(f'  - [ ] {sub_task.title}')


if __name__ == '__main__':
    cli()
