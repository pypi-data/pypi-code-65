import pytest
from aoa.api.project_api import ProjectApi


def test_project(setup):
    project_api = ProjectApi(pytest.aoa_client)
    before_count = len(project_api)

    project = dict()
    project['name'] = 'new_project'
    project['gitRepositoryUrl'] = "https://github.com/ThinkBigAnalytics/TestAoaDemoModels.git"
    project['groupId'] = 'DEMO'
    project['description'] = 'new_project'
    project_rtn = project_api.save(project)
    project_id = project_rtn['id']

    after_count = len(project_api)

    assert (before_count + 1 == after_count), "save project...failed"

    project_rtn_by_id = project_api.find_by_id(project_id=project_id)
    key_to_remove = ('id', 'createdAt', '_links')
    for k in key_to_remove:
        project_rtn_by_id.pop(k, None)

    assert (project_rtn_by_id == project), "validate new project...failed"

    project_name = 'project_updated'
    pytest.aoa_client.set_project_id(project_id)
    project_upd = dict()
    project_upd['name'] = project_name
    project_upd['gitRepositoryUrl'] = "https://github.com/ThinkBigAnalytics/AoaDemoModelsUpdated.git"
    project_upd['groupId'] = 'DEMO'
    project_upd['description'] = project_name
    project_api.update(project_upd)

    project_rtn_upd_by_id = project_api.find_by_id(project_id=project_id)
    key_to_remove = ('id', 'createdAt', '_links')
    for k in key_to_remove:
        project_rtn_upd_by_id.pop(k, None)

    assert (project_upd == project_rtn_upd_by_id), 'validate updated project...failed'

