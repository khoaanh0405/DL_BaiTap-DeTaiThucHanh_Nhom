"""Load the selected checkpoint and predict Gaussian density for custom x1,x2 pairs.

Usage:
    python src/predict_example.py --points "0,0;1,1;-1,2"
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import torch

from mlp_core import InputStandardizer, MLPRegressor, predict

ROOT = Path(__file__).resolve().parents[1]


def parse_points(value: str) -> np.ndarray:
    rows = []
    for item in value.split(";"):
        parts = [part.strip() for part in item.split(",")]
        if len(parts) != 2:
            raise argparse.ArgumentTypeError(
                f"Invalid point {item!r}; each point must be x1,x2"
            )
        try:
            rows.append([float(parts[0]), float(parts[1])])
        except ValueError as exc:
            raise argparse.ArgumentTypeError(f"Invalid numeric point: {item!r}") from exc
    return np.asarray(rows, dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--points", type=parse_points, default=parse_points("0,0;1,1;-1,2"),
        help='Semicolon-separated x1,x2 pairs, e.g. "0,0;1,1"',
    )
    parser.add_argument("--checkpoint", type=Path, default=ROOT / "models" / "best_model.pt")
    args = parser.parse_args()

    if not args.checkpoint.exists():
        raise FileNotFoundError(f"Checkpoint not found: {args.checkpoint}")

    checkpoint = torch.load(args.checkpoint, map_location="cpu", weights_only=False)
    model = MLPRegressor(input_dim=2, hidden_dims=checkpoint["hidden_dims"])
    model.load_state_dict(checkpoint["model_state_dict"])
    scaler = InputStandardizer()
    scaler.mean_ = np.asarray(checkpoint["input_standardizer"]["mean"], dtype=np.float32).reshape(1, -1)
    scaler.std_ = np.asarray(checkpoint["input_standardizer"]["std"], dtype=np.float32).reshape(1, -1)

    values = predict(model, scaler, args.points, device="cpu")
    print("x1\tx2\ty_hat")
    for (x1, x2), pred in zip(args.points, values):
        print(f"{x1:.6f}\t{x2:.6f}\t{pred:.10f}")


if __name__ == "__main__":
    main()
