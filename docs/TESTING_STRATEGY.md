# Testing Strategy — Movie Rating Prediction API

This document describes how the Movie Rating Prediction API is tested, why each
layer of tests exists, and how the tests are enforced by the CI/CD pipeline.

## 1. Goals

Before the system goes to production we need confidence that:

1. The code is correct: the model wrapper, the schemas and the API each behave as specified.
2. The input data is valid: ratings are in range, complete and consistently typed.
3. The model behaves sensibly: it is deterministic, reasonably accurate and robust to unusual input.
4. The API handles valid and invalid requests correctly.
5. Every change is checked automatically before it is merged or deployed.

## 2. Test Pyramid

We follow the ML testing pyramid: many fast, isolated tests at the bottom and
fewer, broader tests at the top.

| Layer | Location | Tests | What it covers |
|---|---|---|---|
| Unit — model | `tests/unit/test_model.py` | 13 | `MovieRatingModel` loading, `predict`, `predict_batch`, `is_loaded`, bad IDs, missing file |
| Unit — schemas | `tests/unit/test_schemas.py` | 18 | Pydantic request/response validation rules |
| Integration | `tests/integration/test_api.py` | 26 | All API endpoints through FastAPI's `TestClient` |
| Data | `tests/data/test_data_quality.py` | 17 | Range, completeness, type, distribution and uniqueness checks on rating data |
| Model behaviour | `tests/model/test_model_behavior.py` | 16 | Invariance, directional, minimum functionality, performance and robustness |
| System | CI `build` job | — | Docker image builds, container starts, `/health` and `/predict` respond |
| **Total** | | **90** | |

## 3. Test Layers in Detail

### 3.1 Unit tests — model wrapper

Checks the `MovieRatingModel` class in `app/model.py` on its own:

- The model loads and exposes a non-null `model` attribute.
- `predict()` returns a `float` between 1.0 and 5.0, for a single pair and for every known pair.
- `predict_batch()` returns a list with one in-range rating per input pair.
- `is_loaded()` returns a real `bool`, and it is `True` after loading.
- **Unknown inputs:** `None` or empty IDs do not raise an error. Surprise falls back to a
  default estimate, and for `("", "")` that is the global mean rating. The tests check this
  actual behaviour.
- A missing model file raises `FileNotFoundError`.

### 3.2 Unit tests — schemas

Checks the validation rules in `app/schemas.py` without starting the API:

- Missing `user_id`, `movie_id` or both raise `ValidationError`. The "both" case reports 2 errors.
- Empty, whitespace-only and `None` IDs are rejected.
- An integer ID is rejected, because Pydantic v2 does not convert `int` to `str`.
- `predicted_rating` must be between 1.0 and 5.0: 0.5 and 5.5 are rejected, while 1.0 and 5.0 are accepted.
- A batch request needs 1 to 100 items: 0 and 101 are rejected, while 100 is accepted.

### 3.3 Integration tests — API

Checks every endpoint end to end through FastAPI's `TestClient`, with the real trained model:

| Endpoint | Checked |
|---|---|
| `GET /` | 200, contains `name`, `version`, `docs` |
| `GET /health` | 200, `status` present, `model_loaded` is a boolean |
| `POST /predict` | 200, response echoes `user_id`/`movie_id`, rating in 1–5; all known pairs succeed |
| `POST /predict/batch` | 200, `total_count` and list length match the request, all ratings in 1–5 |
| `GET /model/info` | 200, `model_version` present, `is_loaded` is a boolean |
| Validation errors | Missing fields, an empty body, malformed JSON and a 10,000-character ID all return 422 |
| Routing errors | An unknown path returns 404; `GET /predict` and `POST /health` return 405 |

The `test_client` fixture uses `with TestClient(app) as client:` so FastAPI's
startup event runs and the model is loaded, exactly as it is under uvicorn.

### 3.4 Data quality tests

Checks rating records (the `sample_ratings` fixture) against the rules training data must meet:

- **Range:** every rating is between 1.0 and 5.0, with nothing negative and nothing above the maximum.
- **Completeness:** no missing user IDs, movie IDs or ratings (`None`/`NaN`), and all required fields are present.
- **Types:** IDs are strings and ratings are numeric (booleans are rejected explicitly).
- **Distribution:** the mean rating is between 2.0 and 4.5, and the standard deviation is between 0 and 2.0.
- **Uniqueness:** each (user, movie) pair appears once, and there are several users and movies.

### 3.5 Model behavioural tests (CheckList approach)

| Category | Tests |
|---|---|
| **Invariance** | The same input always gives the same output (repeated 5 times). Batch order doesn't change any pair's prediction. Batch results equal one-by-one predictions. |
| **Directional** | Predictions for known pairs are within 1.5 of the actual rating. Different movies (same user) and different users (same movie) get different predictions. |
| **Minimum functionality** | Known users get valid predictions. Predictions aren't all identical. Unknown users and movies are handled without crashing. |
| **Performance** | Mean absolute error on known pairs is below 1.0. No single error is above 3.0. |
| **Robustness** | Numeric string IDs are recognised. IDs are matched as exact strings: `"001"` is not user `"1"`, but still gets a valid default prediction. |

## 4. Making the Model Tests Reproducible

`SVD` starts training from random values. Without a fixed seed, every retrain
produces a slightly different model, so accuracy tests could pass on one
machine and fail on another. Two settings in `scripts/train_model.py` fix this:

- `random_state=42`: every machine (Windows, macOS, Linux CI) trains the same model. The sample
  prediction for user 196 and movie 242 is 3.37 both locally and in the Linux CI container.
- `n_epochs=30` (up from 20): with 20 epochs, no seed met the lab's accuracy thresholds. One
  known pair was off by about 1.8–2.2, and the average error was 1.03–1.24.

| Setting | Largest error on known pairs | Average error | Cross-validation RMSE |
|---|---|---|---|
| 20 epochs, seed 42 | 1.83 | 1.03 | 0.936 |
| **30 epochs, seed 42 (used)** | **1.08** | **0.61** | **0.942** |

**Trade-off:** extra epochs fit the training data more closely, so error on unseen data rises
slightly (RMSE +0.006, under 1%). The behavioural accuracy tests use pairs from the training
data, so they measure how well the model fits those pairs, not how well it generalises.
Cross-validation RMSE, printed on every training run, is the measure of generalisation.

## 5. Fixtures

All shared fixtures live in `tests/conftest.py`:

| Fixture | Scope | Purpose |
|---|---|---|
| `test_client` | session | `TestClient` with startup events run (model loaded) |
| `trained_model` | session | Loads `models/svd_model.pkl` once; skips model tests if it is missing |
| `sample_prediction_request` / `sample_batch_request` | function | Valid API payloads |
| `sample_ratings` | function | Rating records for data quality tests |
| `known_user_movie_pairs` | function | Real MovieLens ratings used in accuracy tests |
| `unknown_users` / `unknown_movies` | function | IDs absent from the dataset |

## 6. Coverage

Run with `pytest tests/ --cov=app --cov-report=term --cov-report=html`.

| File | Statements | Missed | Coverage |
|---|---|---|---|
| `app/__init__.py` | 1 | 0 | 100% |
| `app/config.py` | 13 | 0 | 100% |
| `app/main.py` | 51 | 10 | 80% |
| `app/model.py` | 42 | 9 | 79% |
| `app/schemas.py` | 32 | 0 | 100% |
| **Total** | **139** | **19** | **86%** |

This exceeds the required minimum of 80%. The uncovered lines are failure paths
that don't occur with a healthy model:

- The 503 "Model not loaded" responses and the 500 handlers for unexpected prediction errors (`app/main.py`).
- The generic model-loading error branch, `RuntimeError` when predicting without a model, and
  the unused `get_model()`/`reset_model()` helpers (`app/model.py`).

Covering these would need mocking (for example, patching the global `model` to `None`).
That's the natural next step if coverage needs to go higher.

In CI, the coverage report is uploaded as the `coverage-report` artifact
(`coverage.xml` and `htmlcov/`) on every run, and sent to Codecov when a
`CODECOV_TOKEN` secret is set.

## 7. Automation (CI/CD)

### Pre-commit (local, before every commit)

`.pre-commit-config.yaml` runs these checks:

- Whitespace, end-of-file, YAML/JSON, large-file, merge-conflict and private-key checks
- `black`, `isort` and `flake8` (line length 100)
- `mypy` on `app/`
- `pytest tests/unit/`

### CI — `.github/workflows/ci.yml`

Runs on pushes to `main`/`develop` and on pull requests to `main`:

```
lint ──────────► test ──────────┐
                                ├──► build (Docker)
type-check ─────────────────────┘
```

| Job | Steps |
|---|---|
| `lint` | flake8, `black --check`, `isort --check-only` |
| `type-check` | `mypy app/`, with every function required to have type hints (`disallow_untyped_defs`) |
| `test` | Install dependencies, train the model, run all tests with coverage, upload the coverage and model artifacts |
| `build` | Build the Docker image with the trained model, start it, and check that `/health` reports `model_loaded: true` and `/predict` responds |

Pip packages and the MovieLens dataset are cached between runs.

### CD — `.github/workflows/cd.yml`

Runs when a version tag (`v*`) is pushed:

1. Train the model, then build the Docker image and push it to Docker Hub as `:latest` and `:<tag>`.
2. Create a GitHub Release.
3. Deploy to `staging`, then `production` (placeholder steps; add required reviewers to the
   `production` environment to require manual approval).

Because every release is a versioned image tag, rolling back means redeploying the previous tag.

## 8. Known Limitations

- **Data tests use a fixture, not the full dataset.** The same checks could be pointed at the
  real MovieLens data to validate it before training.
- **Accuracy tests use training data.** They catch a broken model, not overfitting. Cross-validation RMSE covers generalisation.
- **No load or performance testing** of the API (for example, with Locust).
- **Failure paths are not covered** (see Coverage) and need mocking to test.
