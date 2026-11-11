from pathlib import Path
from tempfile import TemporaryDirectory
import pytest
from fastapi.testclient import TestClient
from repomedic.api import app, service
from repomedic.staged import StagedRuns

client = TestClient(app)

def test_dashboard_served_and_assets():
    page = client.get('/')
    assert page.status_code == 200
    assert 'Mission control' in page.text
    for asset in ('app.js', 'style.css'):
        assert client.get('/assets/' + asset).status_code == 200

def test_real_stepwise_run_and_approval():
    runner = StagedRuns(service)
    run = runner.create('shipping bug')
    assert run['decision'] == 'NOT_STARTED'
    assert len(run['trace']) == 0
    with TemporaryDirectory() as output:
        with pytest.raises(ValueError):
            service.approve(run['run_id'], True, Path(output))
        for n in range(1,5):
            run = runner.advance(run['run_id'])
            assert run['step'] == n
            assert len(run['trace']) == n
        assert run['decision'] == 'AWAITING_HUMAN_APPROVAL'
        assert run['baseline']['passed'] is False
        assert run['verification']['passed'] is True
        assert '+    return total >= threshold' in run['diff']
        with pytest.raises(ValueError):
            runner.advance(run['run_id'])
        run=service.approve(run['run_id'], True, Path(output))
        assert run['artifact_released']
        assert Path(run['patch_file']).exists()
        assert (Path(output) / f"{run['run_id']}.json").exists()

def test_dashboard_http_steps_and_rejection():
    res=client.post('/dashboard/runs',json={})
    assert res.status_code == 200
    run_id=res.json()['run_id']
    assert client.post(f'/runs/{run_id}/review',json={'approved': True}).status_code == 409
    for i in range(4):
        res=client.post(f'/dashboard/runs/{run_id}/next')
        assert res.status_code == 200
        assert res.json()['step']==i+1
    assert client.post(f'/dashboard/runs/{run_id}/next').status_code == 409
    res=client.post(f'/runs/{run_id}/review',json={'approved':False})
    assert res.status_code == 200 and res.json()['decision']=='HUMAN_REJECTED'
    assert client.post(f'/runs/{run_id}/review',json={'approved':True}).status_code == 409

def test_staged_input_validation():
    runner=StagedRuns(service)
    with pytest.raises(ValueError):runner.create('')
    with pytest.raises(ValueError):runner.create('x'*501)
    with pytest.raises(KeyError):runner.advance('not-a-run')
