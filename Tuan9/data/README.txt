Dataset: two-dimensional Gaussian function approximation

Target density:
  f(x) = 1 / (2*pi*sqrt(det(C))) * exp(-0.5*(x-mu)^T*C^(-1)*(x-mu))
  mu = [0, 0]
  C  = [[0.3, -0.5], [-0.5, 2.0]]
Input domain:
  -2 <= x1 <= 2
  -4 <= x2 <= 4

Files:
  train.csv       2,000 samples, seed 2026
  validation.csv    500 samples, seed 2027
  test.csv          100 samples, seed 2028

Columns: x1, x2, y
All splits are generated independently. The test set is held out and is not used for model selection.
To regenerate, run `python src/run_experiments.py A` (the script regenerates the same deterministic datasets before each group).
