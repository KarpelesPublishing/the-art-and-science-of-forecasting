"""Batch contracts: causal cutoff, durable reuse, isolated failures, actual scale."""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from forecasting_companion.batch import run_batch


def panel(count=3, n=48):
    rng = np.random.default_rng(20260918)
    dates = pd.date_range('2020-01-01', periods=n, freq='MS')
    return pd.concat([pd.DataFrame({'series_id': f'{i:05d}', 'timestamp': dates,
                       'target': 40+.2*np.arange(n)+5*np.sin(2*np.pi*np.arange(n)/12)+rng.normal(0, 1, n)})
                      for i in range(count)], ignore_index=True)


def test_resume_input_config_and_code_invalidation(tmp_path, monkeypatch):
    import forecasting_companion.batch as batch
    source, dest = tmp_path/'input.csv', tmp_path/'out'
    data = panel()
    data.to_csv(source, index=False)
    first = run_batch(source, dest, workers=2)
    assert first['successful'] == 3 and first['resumed'] == 0
    forecast = (dest/'forecast.csv').read_bytes()
    assert run_batch(source, dest, resume=True)['resumed'] == 3
    assert (dest/'forecast.csv').read_bytes() == forecast
    data.loc[0, 'target'] += 10
    data.to_csv(source, index=False)
    assert run_batch(source, dest, resume=True)['resumed'] == 2
    assert run_batch(source, dest, horizon=6, resume=True)['resumed'] == 0
    fake_code = tmp_path/'changed-code.py'
    fake_code.write_text('changed implementation')
    monkeypatch.setattr(batch, '__file__', str(fake_code))
    assert run_batch(source, dest, resume=True)['resumed'] == 0


def test_failures_are_isolated_and_cutoff_excludes_future(tmp_path):
    data = panel(5)
    data.loc[data.series_id == '00001', 'target'] = np.inf
    duplicate = data[data.series_id == '00002'].iloc[[0]]
    data = pd.concat([data, duplicate], ignore_index=True)
    data = data.drop(data[(data.series_id == '00003') & (data.timestamp == '2021-01-01')].index)
    data = data.drop(data[(data.series_id == '00004')].index[7:])
    source, dest = tmp_path/'input.csv', tmp_path/'out'
    data.to_csv(source, index=False)
    summary = run_batch(source, dest)
    assert summary['successful'] == 1 and summary['failed'] == 4
    forecast = pd.read_csv(dest/'forecast.csv', dtype={'series_id': str})
    assert set(forecast.series_id) == {'00000'}
    assert len(json.loads((dest/'failures.json').read_text())['failures']) == 4
    clean = panel(1)
    clean.to_csv(source, index=False)
    run_batch(source, dest, as_of='2022-12-01')
    before = (dest/'forecast.csv').read_bytes()
    clean.loc[clean.timestamp > '2022-12-01', 'target'] = 999999
    clean.to_csv(source, index=False)
    after = run_batch(source, dest, as_of='2022-12-01', resume=True)
    assert after['resumed'] == 1
    assert before == (dest/'forecast.csv').read_bytes()
    assert pd.read_csv(dest/'forecast.csv').origin.str.startswith('2022-12-01').all()


@pytest.mark.parametrize('horizon', [0, -1, 1.5, True, 10001])
def test_bad_horizon(tmp_path, horizon):
    with pytest.raises(ValueError, match='horizon'):
        run_batch(tmp_path/'unused.csv', tmp_path/'out', horizon=horizon)


def test_thousand_series_and_quantile_contract(tmp_path):
    source, dest = tmp_path/'thousand.csv', tmp_path/'out'
    panel(1000).to_csv(source, index=False)
    result = run_batch(source, dest, horizon=12, workers=4)
    assert result['successful'] == 1000 and result['failed'] == 0
    forecast = pd.read_csv(dest/'forecast.csv', dtype={'series_id': str})
    assert len(forecast) == 1000*12*3
    assert forecast.series_id.nunique() == 1000
    assert set(forecast.horizon_step) == set(range(1, 13))
    values = forecast.pivot(index=['series_id', 'horizon_step'], columns='quantile', values='value')
    assert (values[.1] <= values[.5]).all() and (values[.5] <= values[.9]).all()
    assert np.isfinite(forecast[['point', 'value']]).all().all()
    assert run_batch(source, dest, resume=True)['resumed'] == 1000


def test_short_history_extrapolation_and_corrupt_checkpoint(tmp_path):
    source, dest = tmp_path/'short.csv', tmp_path/'out'
    panel(1, 8).to_csv(source, index=False)
    run_batch(source, dest, horizon=12)
    forecast = pd.read_csv(dest/'forecast.csv')
    assert 'empirical_signed_residual_sqrt_extrapolation' in set(forecast.band_method)
    next((dest/'checkpoints').glob('*.json')).write_text('{broken')
    assert run_batch(source, dest, horizon=12, resume=True)['computed'] == 1


def test_bad_dates_and_targets_preserve_literal_ids(tmp_path):
    data = panel(3)
    data['series_id'] = data.series_id.replace({'00000': 'NA', '00001': 'null', '00002': '007'})
    data['timestamp'] = data.timestamp.astype(str)
    data['target'] = data.target.astype(str)
    data.loc[data.series_id == 'null', 'timestamp'] = 'not-a-date'
    data.loc[data.series_id == '007', 'target'] = 'not-a-number'
    source, dest = tmp_path/'bad.csv', tmp_path/'out'
    data.to_csv(source, index=False)
    result = run_batch(source, dest, as_of='2023-12-01')
    assert result['successful'] == 1 and result['failed'] == 2
    forecast = pd.read_csv(dest/'forecast.csv', dtype=str, keep_default_na=False)
    assert set(forecast.series_id) == {'NA'}


def test_checkpoint_integrity_and_invalid_frequency(tmp_path):
    source, dest = tmp_path/'data.csv', tmp_path/'out'
    panel(1).to_csv(source, index=False)
    run_batch(source, dest)
    checkpoint = next((dest/'checkpoints').glob('*.json'))
    altered = json.loads(checkpoint.read_text())
    altered['result']['forecasts'][0]['point'] = 999999
    checkpoint.write_text(json.dumps(altered))
    assert run_batch(source, dest, resume=True)['computed'] == 1
    with pytest.raises(ValueError):
        run_batch(source, dest, frequency='0D')
    with pytest.raises(ValueError):
        run_batch(source, dest, workers=0)
