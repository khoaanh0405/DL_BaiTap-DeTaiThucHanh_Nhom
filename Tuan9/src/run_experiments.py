"""Run reproducible A/B/C experiments in separate groups to keep logs resumable."""
from __future__ import annotations
import argparse, json, sys, time
from pathlib import Path
import numpy as np
import pandas as pd
import torch
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.mlp_core import generate_dataset, train_model, predict, MU, COV


def save_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def run_group(group: str, cfg: dict, x_train, y_train, x_valid, y_valid, nested_x, nested_y) -> None:
    ROOT.joinpath("logs").mkdir(exist_ok=True)
    model_dir = ROOT / "models/experiment_checkpoints"
    model_dir.mkdir(parents=True, exist_ok=True)
    if group == "A": specs = [(n, [10], nested_x[:n], nested_y[:n]) for n in cfg["experiment_A_train_sizes"]]
    elif group == "B": specs = [(w, [w], x_train, y_train) for w in cfg["experiment_B_hidden_widths"]]
    elif group == "C": specs = [(d, [10] * d, x_train, y_train) for d in cfg["experiment_C_hidden_depths"]]
    else: raise ValueError(group)
    rows, epochs_rows = [], []
    for value, hidden_dims, xtr, ytr in specs:
        for seed in cfg["experiment_seeds"]:
            run_id = f"{group}_{value:04d}_seed{seed}"
            ckpt = model_dir / f"{run_id}.pt"
            out = train_model(
                xtr, ytr, x_valid, y_valid, hidden_dims, seed,
                epochs=cfg["epochs"], batch_size=cfg["batch_size"], learning_rate=cfg["learning_rate"],
                weight_decay=cfg["weight_decay"], patience=cfg["early_stopping_patience"], device=None,
                checkpoint_path=ckpt,
            )
            for rec in out["history"]:
                epochs_rows.append({"run_id": run_id, "group": group, "factor_value": value, "seed": seed, **rec})
            rows.append({"run_id": run_id, "group": group, "factor_value": value,
                         "hidden_dims": "x".join(map(str, hidden_dims)), "depth": len(hidden_dims),
                         "width": hidden_dims[0], "train_samples": len(xtr), "seed": seed,
                         "best_epoch": out["best_epoch"], "epochs_run": out["epochs_run"],
                         "train_mse": out["train_mse"], "train_mae": out["train_mae"], "train_rmse": out["train_rmse"],
                         "val_mse": out["val_mse"], "val_mae": out["val_mae"], "val_rmse": out["val_rmse"],
                         "train_seconds": out["train_seconds"], "device": out["device"],
                         "checkpoint": str(ckpt.relative_to(ROOT))})
            print(f"{run_id}: val_MSE={out['val_mse']:.7g}, epoch={out['best_epoch']}, seconds={out['train_seconds']:.2f}", flush=True)
    runs = pd.DataFrame(rows); epochs_df = pd.DataFrame(epochs_rows)
    save_csv(runs, ROOT / f"logs/experiment_{group}_runs.csv")
    save_csv(epochs_df, ROOT / f"logs/experiment_{group}_epochs.csv")
    agg = runs.groupby("factor_value").agg(
        train_mse_mean=("train_mse","mean"), train_mse_std=("train_mse","std"),
        val_mse_mean=("val_mse","mean"), val_mse_std=("val_mse","std"),
        val_mae_mean=("val_mae","mean"), val_mae_std=("val_mae","std"),
        val_rmse_mean=("val_rmse","mean"), val_rmse_std=("val_rmse","std"),
        train_seconds_mean=("train_seconds","mean"), best_epoch_mean=("best_epoch","mean")
    ).reset_index()
    agg["group"] = group
    save_csv(agg, ROOT / f"results/experiment_{group}_summary.csv")


def finalize(cfg: dict, x_train, y_train, x_valid, y_valid, x_test, y_test) -> None:
    run_frames, epoch_frames = [], []
    for g in "ABC":
        rp, ep = ROOT / f"logs/experiment_{g}_runs.csv", ROOT / f"logs/experiment_{g}_epochs.csv"
        if not rp.exists() or not ep.exists(): raise FileNotFoundError(f"Run group {g} first: {rp}")
        run_frames.append(pd.read_csv(rp)); epoch_frames.append(pd.read_csv(ep))
    runs = pd.concat(run_frames, ignore_index=True); epoch_logs = pd.concat(epoch_frames, ignore_index=True)
    save_csv(runs, ROOT / "logs/experiment_runs.csv")
    save_csv(epoch_logs, ROOT / "logs/epoch_history_all_runs.csv")
    summaries = {g:pd.read_csv(ROOT/f"results/experiment_{g}_summary.csv") for g in "ABC"}
    save_csv(pd.concat([summaries[g] for g in "ABC"],ignore_index=True), ROOT / "results/all_experiments_summary.csv")

    candidates=[]
    for g in "BC":
        for value, part in runs[runs.group==g].groupby("factor_value"):
            hd=[int(v) for v in str(part.iloc[0].hidden_dims).split("x")]
            params=0; prev=2
            for h in hd: params += prev*h+h; prev=h
            params += prev+1
            candidates.append({"group":g,"factor_value":int(value),"hidden_dims":hd,"mean_val_mse":part.val_mse.mean(),"std_val_mse":part.val_mse.std(),"params":params})
    candidates=sorted(candidates,key=lambda d:(d["mean_val_mse"],d["params"]))
    chosen=candidates[0]
    final=train_model(x_train,y_train,x_valid,y_valid,chosen["hidden_dims"],999,
                      epochs=cfg.get("final_refit_epochs", cfg["epochs"]),batch_size=cfg["batch_size"],learning_rate=cfg["learning_rate"],
                      weight_decay=cfg["weight_decay"],patience=cfg.get("final_refit_patience", cfg["early_stopping_patience"]),device=None,
                      checkpoint_path=ROOT/"models/best_model.pt")
    y_pred=predict(final["model"],final["scaler"],x_test,device=final["device"])
    mse=float(np.mean((y_pred-y_test)**2)); mae=float(np.mean(np.abs(y_pred-y_test))); rmse=float(np.sqrt(mse))
    save_csv(pd.DataFrame({"x1":x_test[:,0],"x2":x_test[:,1],"y_true":y_test,"y_pred":y_pred,"absolute_error":np.abs(y_pred-y_test)}),ROOT/"results/final_test_predictions.csv")
    save_csv(pd.DataFrame(final["history"]),ROOT/"logs/final_model_epoch_history.csv")
    summary={
      "selection_rule":"Minimum mean validation MSE among B and C trials; tie-break by fewer parameters.",
      "selected_group":chosen["group"],"selected_factor_value":chosen["factor_value"],"hidden_dims":chosen["hidden_dims"],
      "parameter_count":chosen["params"],"selection_mean_validation_mse":chosen["mean_val_mse"],"selection_std_validation_mse":chosen["std_val_mse"],
      "final_refit_seed":999,"final_best_epoch":final["best_epoch"],"final_train_mse":final["train_mse"],
      "final_validation_mse":final["val_mse"],"test_mse":mse,"test_mae":mae,"test_rmse":rmse,
      "final_train_seconds":final["train_seconds"],"device":final["device"],"n_train":len(x_train),"n_validation":len(x_valid),"n_test":len(x_test),
      "experiment_seeds":cfg["experiment_seeds"],"covariance":COV.tolist(),"mean":MU.tolist(),
      "optimizer":cfg["optimizer"],"learning_rate":cfg["learning_rate"],"batch_size":cfg["batch_size"],"epochs_max":cfg.get("final_refit_epochs", cfg["epochs"]),
      "activation":cfg["activation"],"search_early_stopping_patience":cfg["early_stopping_patience"],"final_refit_patience":cfg.get("final_refit_patience", cfg["early_stopping_patience"])}
    (ROOT/"results/final_model_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    import torch as _torch
    ckpt=_torch.load(ROOT/"models/best_model.pt",map_location="cpu",weights_only=False)
    (ROOT/"models/best_model_metadata.json").write_text(json.dumps({**summary,"input_standardizer":ckpt["input_standardizer"]},indent=2),encoding="utf-8")
    print("FINAL SUMMARY\n"+json.dumps(summary,indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(); parser.add_argument("group",choices=["A","B","C","all","finalize"],default="all",nargs="?"); args=parser.parse_args()
    torch.set_num_threads(1)
    cfg=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
    data_dir=ROOT/"data"; data_dir.mkdir(exist_ok=True)
    x_train,y_train=generate_dataset(cfg["n_train"],cfg["data_seeds"]["train"])
    x_valid,y_valid=generate_dataset(cfg["n_validation"],cfg["data_seeds"]["validation"])
    x_test,y_test=generate_dataset(cfg["n_test"],cfg["data_seeds"]["test"])
    for name,x,y in [("train",x_train,y_train),("validation",x_valid,y_valid),("test",x_test,y_test)]:
        pd.DataFrame({"x1":x[:,0],"x2":x[:,1],"y":y}).to_csv(data_dir/f"{name}.csv",index=False)
    idx=np.random.default_rng(314159).permutation(len(x_train)); nested_x,nested_y=x_train[idx],y_train[idx]
    if args.group in "ABC" and len(args.group)==1: run_group(args.group,cfg,x_train,y_train,x_valid,y_valid,nested_x,nested_y)
    elif args.group=="all":
        for g in "ABC": run_group(g,cfg,x_train,y_train,x_valid,y_valid,nested_x,nested_y)
        finalize(cfg,x_train,y_train,x_valid,y_valid,x_test,y_test)
    else: finalize(cfg,x_train,y_train,x_valid,y_valid,x_test,y_test)

if __name__=="__main__": main()
