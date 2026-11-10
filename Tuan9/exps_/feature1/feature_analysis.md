# Feature analysis / preprocessing decision

This function approximation problem has exactly two physical input variables, `x1` and `x2`. Neither variable is a redundant ID or a categorical feature. Both are required to evaluate the bivariate Gaussian exponent, so no feature is removed.

The model standardizes each input using the training split's mean and standard deviation only. The same fitted transformation is then applied unchanged to validation and test. Target `y` is left in its natural density scale. See `config.json`, `src/mlp_core.py`, and the `pre-processing.ipynb` notebook.
