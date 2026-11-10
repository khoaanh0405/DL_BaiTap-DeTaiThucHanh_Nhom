"""PyTorch MLP utilities for 2-D Gaussian function approximation."""
from __future__ import annotations

import copy
import json
import random
import time
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

MU = np.array([0.0, 0.0], dtype=np.float64)
COV = np.array([[0.3, -0.5], [-0.5, 2.0]], dtype=np.float64)
X1_RANGE = (-2.0, 2.0)
X2_RANGE = (-4.0, 4.0)


def set_seed(seed: int) -> None:
    """Set Python, NumPy and PyTorch seeds for repeatable experiments."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    # Reproducibility is preferred over speed for this small MLP exercise.
    torch.use_deterministic_algorithms(True, warn_only=True)


def gaussian_pdf(x: np.ndarray, mean: np.ndarray = MU, cov: np.ndarray = COV) -> np.ndarray:
    """Evaluate the bivariate Gaussian density row-wise."""
    x = np.asarray(x, dtype=np.float64)
    mean = np.asarray(mean, dtype=np.float64)
    cov = np.asarray(cov, dtype=np.float64)
    delta = x - mean
    inv_cov = np.linalg.inv(cov)
    exponent = -0.5 * np.einsum("ni,ij,nj->n", delta, inv_cov, delta)
    normalizer = 1.0 / (2.0 * np.pi * np.sqrt(np.linalg.det(cov)))
    return normalizer * np.exp(exponent)


def generate_dataset(n: int, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Sample inputs uniformly inside the assignment domain and label by the PDF."""
    rng = np.random.default_rng(seed)
    x = np.column_stack([
        rng.uniform(*X1_RANGE, size=n),
        rng.uniform(*X2_RANGE, size=n),
    ]).astype(np.float32)
    y = gaussian_pdf(x).astype(np.float32)
    return x, y


class InputStandardizer:
    """Standardize x using train-only statistics; never fits on validation/test."""
    def __init__(self) -> None:
        self.mean_: np.ndarray | None = None
        self.std_: np.ndarray | None = None

    def fit(self, x: np.ndarray) -> "InputStandardizer":
        self.mean_ = np.mean(x, axis=0, keepdims=True)
        self.std_ = np.std(x, axis=0, keepdims=True)
        self.std_ = np.where(self.std_ < 1e-8, 1.0, self.std_)
        return self

    def transform(self, x: np.ndarray) -> np.ndarray:
        if self.mean_ is None or self.std_ is None:
            raise RuntimeError("InputStandardizer must be fitted before transform().")
        return ((np.asarray(x, dtype=np.float32) - self.mean_) / self.std_).astype(np.float32)

    def state_dict(self) -> dict:
        return {"mean": self.mean_.reshape(-1).tolist(), "std": self.std_.reshape(-1).tolist()}


class MLPRegressor(nn.Module):
    """Configurable MLP with tanh hidden activations and a linear regression head."""
    def __init__(self, input_dim: int = 2, hidden_dims: Sequence[int] = (10,)) -> None:
        super().__init__()
        if not hidden_dims or any(int(h) < 1 for h in hidden_dims):
            raise ValueError("hidden_dims must contain one or more positive integers")
        layers: list[nn.Module] = []
        prev = input_dim
        for idx, width in enumerate(hidden_dims, start=1):
            layers.append(nn.Linear(prev, int(width)))
            layers.append(nn.Tanh())
            prev = int(width)
        layers.append(nn.Linear(prev, 1))  # Linear output is suitable for regression.
        self.network = nn.Sequential(*layers)
        self.hidden_dims = tuple(int(x) for x in hidden_dims)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.network(x)


def _evaluate(model: nn.Module, loader: DataLoader, criterion: nn.Module, device: torch.device) -> tuple[float, float, float]:
    model.eval()
    total_sq = 0.0
    total_abs = 0.0
    total_n = 0
    with torch.no_grad():
        for xb, yb in loader:
            xb, yb = xb.to(device), yb.to(device)
            pred = model(xb)
            total_sq += torch.sum((pred - yb) ** 2).item()
            total_abs += torch.sum(torch.abs(pred - yb)).item()
            total_n += len(xb)
    mse = total_sq / max(total_n, 1)
    mae = total_abs / max(total_n, 1)
    return mse, mae, float(np.sqrt(mse))


def train_model(
    x_train: np.ndarray,
    y_train: np.ndarray,
    x_valid: np.ndarray,
    y_valid: np.ndarray,
    hidden_dims: Sequence[int],
    seed: int,
    epochs: int = 180,
    batch_size: int = 128,
    learning_rate: float = 0.004,
    weight_decay: float = 1e-5,
    patience: int = 30,
    device: str | None = None,
    checkpoint_path: str | Path | None = None,
) -> dict:
    """Train with explicit train/validation loops and best-validation checkpointing."""
    set_seed(seed)
    chosen_device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
    scaler = InputStandardizer().fit(x_train)
    xtr = scaler.transform(x_train)
    xva = scaler.transform(x_valid)

    train_ds = TensorDataset(torch.from_numpy(xtr), torch.from_numpy(y_train.reshape(-1, 1).astype(np.float32)))
    valid_ds = TensorDataset(torch.from_numpy(xva), torch.from_numpy(y_valid.reshape(-1, 1).astype(np.float32)))
    generator = torch.Generator().manual_seed(seed)
    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, generator=generator)
    valid_loader = DataLoader(valid_ds, batch_size=max(batch_size, 256), shuffle=False)

    model = MLPRegressor(2, hidden_dims).to(chosen_device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate, weight_decay=weight_decay)

    history: list[dict] = []
    best_val = float("inf")
    best_epoch = 0
    best_state = None
    wait = 0
    start = time.perf_counter()

    for epoch in range(1, epochs + 1):
        model.train()
        train_sq = 0.0
        train_n = 0
        for xb, yb in train_loader:
            xb, yb = xb.to(chosen_device), yb.to(chosen_device)
            optimizer.zero_grad(set_to_none=True)
            pred = model(xb)
            loss = criterion(pred, yb)
            loss.backward()
            optimizer.step()
            train_sq += torch.sum((pred.detach() - yb) ** 2).item()
            train_n += len(xb)

        train_mse = train_sq / max(train_n, 1)
        val_mse, val_mae, val_rmse = _evaluate(model, valid_loader, criterion, chosen_device)
        history.append({"epoch": epoch, "train_mse": train_mse, "val_mse": val_mse, "val_mae": val_mae, "val_rmse": val_rmse})

        if val_mse < best_val - 1e-12:
            best_val = val_mse
            best_epoch = epoch
            best_state = copy.deepcopy({k: v.detach().cpu() for k, v in model.state_dict().items()})
            wait = 0
        else:
            wait += 1
        if wait >= patience:
            break

    elapsed = time.perf_counter() - start
    if best_state is None:
        raise RuntimeError("Training did not produce a valid checkpoint")
    model.load_state_dict(best_state)
    train_mse, train_mae, train_rmse = _evaluate(model, DataLoader(train_ds, batch_size=512), criterion, chosen_device)
    val_mse, val_mae, val_rmse = _evaluate(model, valid_loader, criterion, chosen_device)

    if checkpoint_path is not None:
        path = Path(checkpoint_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            "model_state_dict": best_state,
            "input_standardizer": scaler.state_dict(),
            "hidden_dims": list(hidden_dims),
            "seed": seed,
            "best_epoch": best_epoch,
            "best_val_mse": val_mse,
        }, path)

    return {
        "model": model,
        "scaler": scaler,
        "history": history,
        "best_epoch": best_epoch,
        "epochs_run": len(history),
        "train_mse": train_mse,
        "train_mae": train_mae,
        "train_rmse": train_rmse,
        "val_mse": val_mse,
        "val_mae": val_mae,
        "val_rmse": val_rmse,
        "train_seconds": elapsed,
        "device": str(chosen_device),
    }


def predict(model: nn.Module, scaler: InputStandardizer, x: np.ndarray, device: str | None = None) -> np.ndarray:
    chosen_device = torch.device(device or next(model.parameters()).device)
    model.eval()
    xt = torch.from_numpy(scaler.transform(x)).to(chosen_device)
    with torch.no_grad():
        return model(xt).cpu().numpy().reshape(-1)
