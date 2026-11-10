from pathlib import Path
import sys
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.mlp_core import gaussian_pdf, COV, MLPRegressor

def test_gaussian_peak_and_covariance():
    assert np.isclose(np.linalg.det(COV),0.35)
    peak=gaussian_pdf(np.array([[0.0,0.0]]))[0]
    assert np.isclose(peak,1/(2*np.pi*np.sqrt(0.35)))

def test_mlp_output_shape():
    import torch
    model=MLPRegressor(2,[10,10])
    out=model(torch.zeros(4,2))
    assert tuple(out.shape)==(4,1)

if __name__=='__main__':
    test_gaussian_peak_and_covariance(); test_mlp_output_shape(); print('core tests passed')
