from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

from .metrics import clip_prob, logit


class IdentityCalibrator:
    def fit(self, p, y):
        return self
    def predict(self, p):
        return clip_prob(p)


class PlattCalibrator:
    def fit(self, p, y):
        self.model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        self.model.fit(logit(p).reshape(-1, 1), np.asarray(y, dtype=int))
        return self
    def predict(self, p):
        return self.model.predict_proba(logit(p).reshape(-1, 1))[:, 1]


class IsotonicCalibrator:
    def fit(self, p, y):
        self.model = IsotonicRegression(out_of_bounds="clip")
        self.model.fit(clip_prob(p), np.asarray(y, dtype=int))
        return self
    def predict(self, p):
        return clip_prob(self.model.predict(clip_prob(p)))


class BetaStyleCalibrator:
    """Beta-style calibration using log(p) and -log(1-p) features."""
    def fit(self, p, y):
        p = clip_prob(p)
        X = np.column_stack([np.log(p), -np.log(1 - p)])
        self.model = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        self.model.fit(X, np.asarray(y, dtype=int))
        return self
    def predict(self, p):
        p = clip_prob(p)
        X = np.column_stack([np.log(p), -np.log(1 - p)])
        return self.model.predict_proba(X)[:, 1]


def make_calibrator(name: str):
    name = name.lower()
    if name == "none":
        return IdentityCalibrator()
    if name == "platt":
        return PlattCalibrator()
    if name == "isotonic":
        return IsotonicCalibrator()
    if name in {"beta", "beta_style"}:
        return BetaStyleCalibrator()
    raise ValueError(f"Unknown calibration method: {name}")
