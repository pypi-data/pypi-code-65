from datetime import date as Date
from todoist_to_markdown.task import Task
from typing import Dict
from todoist.api import TodoistAPI
from todoist_to_markdown.enviroment import get_environment
from todoist_to_markdown.argument import get_argument


token = get_environment('TODOIST_API_TOKEN')
if token is None:
    token = get_argument('token')
if token is None:
    raise Exception(
        'Todoistのトークンを設定してください。コマンドのオプションまたは環境変数TODOIST_API_TOKENで設定可能です')
api = TodoistAPI(token)
api.sync()
today = Date.today()


def get_today_tasks() -> Dict[str, Task]:
    today_items: Dict[str, Task] = {}
    sub_item_list = []
    for item in api.state['items']:
        # 完了していれば省く
        if _is_complete(item):
            continue
        # サブタスクはあとで処理する
        if is_sub_task(item):
            sub_item_list.append(item)
            continue
        # 今日じゃなければ省く
        if not _is_today(item):
            continue
        task: Task = _convert_model(item)
        today_items[item['id']] = task

    # 「今日」に指定されてないサブタスクがあるので、それらを検索する
    parent_id_list = today_items.keys()
    for item in sub_item_list:
        parent_id = item['parent_id']
        if parent_id in parent_id_list:
            task = _convert_model(item)
            today_items[parent_id].add_sub_task(task=task)

    return today_items


def _convert_model(item) -> Task:
    return Task(title=item['content'])


def is_sub_task(item):
    return item['parent_id'] is not None


def _is_today(item):
    if 'due' not in item:
        return False
    if item['due'] is None:
        return False
    # "today"で判定
    if 'string' in item['due'] and item['due']['string'] == 'today':
        return True
    # 日付で判定
    if 'date' not in item['due']:
        return False
    date = Date.fromisoformat(item['due']['date'][0:10])
    return date == today


def _is_complete(item):
    return item['checked']
