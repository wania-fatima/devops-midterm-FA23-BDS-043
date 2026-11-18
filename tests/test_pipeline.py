import json
from pathlib import Path
import pandas as pd
from fastapi.testclient import TestClient
from app import app

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / 'config.json').read_text())
client = TestClient(app)

def test_dataset():
    df = pd.read_csv(ROOT / 'dataset/train.csv')
    assert len(df) >= 100
    assert set(CFG['features'] + ['label']).issubset(df.columns)
    assert df['label'].nunique() == 2

def test_metrics_file():
    m = json.loads((ROOT / 'artifacts/metrics.json').read_text())
    for k in ['student_id', 'accuracy', 'training_rows', 'model_version', 'git_sha']:
        assert k in m
    assert m['student_id'] == CFG['student_id']
    assert 0.0 <= m['accuracy'] <= 1.0

def test_api_metrics():
    r = client.get('/metrics')
    assert r.status_code == 200
    assert r.json()['training_rows'] == len(pd.read_csv(ROOT / 'dataset/train.csv'))

def test_api_predict():
    rec = {f: 0.1 for f in CFG['features']}
    r = client.post('/predict', json={'records': [rec]})
    assert r.status_code == 200
    assert len(r.json()['predictions']) == 1
