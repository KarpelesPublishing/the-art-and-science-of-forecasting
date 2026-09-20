import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
import pytest
from forecasting_companion.common import brier, mae, mase

def test_scores_by_hand():
    assert brier([0,1],[0,1]) == 0
    assert brier([.5,.5],[0,1]) == .25
    assert mae([2,4], np.array([1,6])) == 1.5
    assert mase([2,4], np.array([1,6]), [1,2,3]) == 1.5
    assert np.isnan(mase([2], np.array([1]), [1,1,1]))

def test_invalid_probability():
    with pytest.raises(ValueError): brier([1.2], [1])

def test_scores_reject_broadcast_and_missing_values():
    for score in [mae,brier]:
        with pytest.raises(ValueError): score([0,1],[[0],[1]])
        with pytest.raises(ValueError): score([],[])
        with pytest.raises(ValueError): score([float('nan')],[1])
    with pytest.raises(ValueError): mase([1],[2],[1,2],season=2)
    with pytest.raises(ValueError): mase([1],[2],[1,2],season=0)
