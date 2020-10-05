
def test_agents(client, benchmark_yaml):
    agents = client.agents()
    assert agents
    assert agents[0] == list(benchmark_yaml['agents'].keys())[0]


def test_log(client):
    logs = client.log()
    assert logs
    assert len(logs) > 0


def test_agent_logs(client):
    agents = client.agents()
    logs = client.agent_logs(agents[0])
    assert logs == ''


def test_version(client):
    version = client.version()
    assert version
    assert version['version']
