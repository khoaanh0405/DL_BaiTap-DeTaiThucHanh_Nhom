"""Create report-quality figures from generated data and experiment logs."""
from __future__ import annotations
import json, sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.mlp_core import gaussian_pdf, MLPRegressor, InputStandardizer, predict
import torch

FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(FIG / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main():
    train = pd.read_csv(ROOT / "data/train.csv")
    valid = pd.read_csv(ROOT / "data/validation.csv")
    test = pd.read_csv(ROOT / "data/test.csv")
    for name, df in [("train",train),("validation",valid),("test",test)]:
        print(name, df.describe().round(5).to_string())

    fig = plt.figure(figsize=(15,5))
    ax1 = fig.add_subplot(1,3,1, projection="3d")
    for ax, df, title in [(ax1,train,"Train (n=2000)"),
                          (fig.add_subplot(1,3,2,projection="3d"),valid,"Validation (n=500)"),
                          (fig.add_subplot(1,3,3,projection="3d"),test,"Test (n=100)")]:
        ax.scatter(df.x1, df.x2, df.y, s=5, alpha=.65)
        ax.set_title(title); ax.set_xlabel("x1"); ax.set_ylabel("x2"); ax.set_zlabel("Gaussian y")
    save(fig,"01_data_splits_3d.png")

    x1 = np.linspace(-2,2,100); x2 = np.linspace(-4,4,120)
    X1,X2 = np.meshgrid(x1,x2); grid = np.column_stack([X1.ravel(),X2.ravel()]); Z=gaussian_pdf(grid).reshape(X1.shape)
    fig=plt.figure(figsize=(8,6)); ax=fig.add_subplot(111,projection="3d")
    surf=ax.plot_surface(X1,X2,Z,cmap="viridis",linewidth=0,antialiased=True,alpha=.9)
    ax.set_xlabel("x1"); ax.set_ylabel("x2"); ax.set_zlabel("f(x1,x2)"); ax.set_title("True bivariate Gaussian surface")
    fig.colorbar(surf, ax=ax, shrink=.65, label="Density")
    save(fig,"02_true_gaussian_surface.png")

    fig,axs=plt.subplots(1,3,figsize=(14,4))
    for ax,col in zip(axs,["x1","x2","y"]):
        ax.hist(train[col],bins=35,edgecolor="white"); ax.set_title(f"Train distribution: {col}"); ax.set_xlabel(col); ax.set_ylabel("Frequency")
    save(fig,"03_data_distributions.png")

    fig,axs=plt.subplots(1,2,figsize=(12,4))
    axs[0].scatter(train.x1,train.x2,c=train.y,s=7,cmap="viridis"); axs[0].set_xlabel("x1"); axs[0].set_ylabel("x2"); axs[0].set_title("Input domain colored by target")
    axs[1].scatter(test.x1,test.y,c=test.y,s=15,cmap="viridis"); axs[1].set_xlabel("x1"); axs[1].set_ylabel("x2"); axs[1].set_title("Held-out test locations")
    save(fig,"04_domain_and_target.png")

    runs=pd.read_csv(ROOT/"logs/experiment_runs.csv")
    summaries={g:pd.read_csv(ROOT/f"results/experiment_{g}_summary.csv") for g in "ABC"}
    def exp_plot(g, xcol, xlabel, title, filename):
        d=summaries[g]
        fig,ax=plt.subplots(figsize=(8,5))
        ax.errorbar(d.factor_value,d.val_mse_mean,yerr=d.val_mse_std,marker="o",capsize=4,label="Validation MSE (mean ± SD)")
        ax.set_xlabel(xlabel); ax.set_ylabel("Validation MSE"); ax.set_title(title); ax.grid(True,alpha=.3); ax.legend()
        save(fig,filename)
    exp_plot("A","factor_value","Number of training samples A","Experiment A - Training set size","05_experiment_A.png")
    exp_plot("B","factor_value","Hidden neurons B (one hidden layer)","Experiment B - Hidden width","06_experiment_B.png")
    exp_plot("C","factor_value","Number of hidden layers C (10 neurons/layer)","Experiment C - Hidden depth","07_experiment_C.png")

    d=summaries["C"]
    fig,ax=plt.subplots(figsize=(8,5)); ax.errorbar(d.factor_value,d.train_seconds_mean,marker="o",capsize=4)
    ax.set_xlabel("Hidden depth C"); ax.set_ylabel("Training time (seconds)"); ax.set_title("Experiment C - Mean training time"); ax.grid(True,alpha=.3)
    save(fig,"08_depth_training_time.png")

    final=json.loads((ROOT/"results/final_model_summary.json").read_text())
    ckpt=torch.load(ROOT/"models/best_model.pt",map_location="cpu",weights_only=False)
    model=MLPRegressor(2,ckpt["hidden_dims"]); model.load_state_dict(ckpt["model_state_dict"]); model.eval()
    sc=InputStandardizer(); sc.mean_=np.array(ckpt["input_standardizer"]["mean"]).reshape(1,-1); sc.std_=np.array(ckpt["input_standardizer"]["std"]).reshape(1,-1)
    pred=predict(model,sc,grid)
    Zhat=pred.reshape(X1.shape)
    fig=plt.figure(figsize=(14,5))
    a=fig.add_subplot(1,2,1,projection="3d"); a.plot_surface(X1,X2,Z,cmap="viridis",alpha=.75); a.set_title("True Gaussian"); a.set_xlabel("x1"); a.set_ylabel("x2"); a.set_zlabel("y")
    b=fig.add_subplot(1,2,2,projection="3d"); b.plot_surface(X1,X2,Zhat,cmap="plasma",alpha=.75); b.set_title(f"MLP approximation: {final['hidden_dims']}"); b.set_xlabel("x1"); b.set_ylabel("x2"); b.set_zlabel("ŷ")
    save(fig,"09_true_vs_approx_surface.png")

    pred_df=pd.read_csv(ROOT/"results/final_test_predictions.csv")
    fig,axs=plt.subplots(1,2,figsize=(12,5))
    axs[0].scatter(pred_df.y_true,pred_df.y_pred,alpha=.8); lo=min(pred_df.y_true.min(),pred_df.y_pred.min()); hi=max(pred_df.y_true.max(),pred_df.y_pred.max()); axs[0].plot([lo,hi],[lo,hi],"r--",label="Ideal y = ŷ"); axs[0].set_xlabel("True y"); axs[0].set_ylabel("Predicted ŷ"); axs[0].set_title("Test: true vs predicted"); axs[0].legend(); axs[0].grid(True,alpha=.3)
    axs[1].scatter(pred_df.y_true,pred_df.absolute_error,alpha=.8); axs[1].set_xlabel("True y"); axs[1].set_ylabel("Absolute error"); axs[1].set_title("Test absolute error"); axs[1].grid(True,alpha=.3)
    save(fig,"10_test_prediction_diagnostics.png")

    final_hist=pd.read_csv(ROOT/"logs/final_model_epoch_history.csv")
    fig,ax=plt.subplots(figsize=(8,5)); ax.plot(final_hist.epoch,final_hist.train_mse,label="Train MSE"); ax.plot(final_hist.epoch,final_hist.val_mse,label="Validation MSE"); ax.axvline(final["final_best_epoch"],color="gray",linestyle="--",label="Best checkpoint")
    ax.set_xlabel("Epoch"); ax.set_ylabel("MSE"); ax.set_title("Selected model learning curve"); ax.grid(True,alpha=.3); ax.legend()
    save(fig,"11_final_learning_curve.png")

    # Per-run spread visual: train and validation metrics across experiment configurations.
    fig,axs=plt.subplots(1,3,figsize=(15,4))
    for ax,g in zip(axs,"ABC"):
        part=runs[runs.group==g]
        ax.scatter(part.train_mse,part.val_mse,c=part.factor_value,s=22,alpha=.8)
        ax.set_xlabel("Train MSE"); ax.set_ylabel("Validation MSE"); ax.set_title(f"Generalization: group {g}"); ax.grid(True,alpha=.3)
    save(fig,"12_train_validation_tradeoff.png")

if __name__ == "__main__": main()
