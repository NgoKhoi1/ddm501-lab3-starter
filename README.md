# Lab 3: Testing & CI/CD for ML Systems

[![CI Pipeline](https://github.com/NgoKhoi1/ddm501-lab3-starter/actions/workflows/ci.yml/badge.svg)](https://github.com/NgoKhoi1/ddm501-lab3-starter/actions/workflows/ci.yml)
[![CD Pipeline](https://github.com/NgoKhoi1/ddm501-lab3-starter/actions/workflows/cd.yml/badge.svg)](https://github.com/NgoKhoi1/ddm501-lab3-starter/actions/workflows/cd.yml)
![Coverage](https://img.shields.io/badge/coverage-86%25-brightgreen)
![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11-blue)

## Overview

Implement comprehensive testing strategies and CI/CD pipelines for the movie rating prediction system to ensure quality and automate deployment.

| | |
|---|---|
| **Course** | DDM501 - AI in Production: From Models to Systems |
| **Weight** | 15% of total grade |
| **Duration** | 3 hours (in-class) + 1 week to complete |
| **Prerequisites** | Lab 1 and Lab 2 completed |

### Team Members

| Name | Student ID | Role | Contribution |
|---|---|---|---|
| Phạm Minh Hoàng | _TODO_ | Unit & Data Testing | Unit tests for the model and schemas (`tests/unit/`), data quality tests (`tests/data/`), shared fixtures (`tests/conftest.py`) |
| Nguyễn Công Trọng | _TODO_ | Integration & Model Testing | API integration tests (`tests/integration/`), model behavioral tests (`tests/model/`), testing strategy document (`docs/TESTING_STRATEGY.md`) |
| Ngô Minh Khôi | _TODO_ | CI/CD & Code Quality | CI/CD pipelines (`.github/workflows/`), pre-commit hooks and tool config (`.pre-commit-config.yaml`, `pyproject.toml`), Dockerfile, README |

Each member contributed roughly one third (~33%) of the total work.

## Learning Objectives

- Write comprehensive unit tests for ML components
- Implement integration tests for API endpoints
- Create data validation tests
- Design model behavioral tests (invariance, directional, minimum functionality)
- Set up CI/CD pipelines with GitHub Actions
- Implement automated code quality checks

## Project Structure

```
ddm501-lab3-starter/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application
│   ├── model.py            # ML model class
│   ├── schemas.py          # Pydantic schemas
│   └── config.py           # Configuration
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Shared fixtures
│   ├── unit/
│   │   ├── test_model.py   # Model unit tests
│   │   └── test_schemas.py # Schema tests
│   ├── integration/
│   │   └── test_api.py     # API tests
│   ├── data/
│   │   └── test_data_quality.py  # Data tests
│   └── model/
│       └── test_model_behavior.py  # Behavioral tests
├── docs/
│   └── TESTING_STRATEGY.md # Testing strategy document
├── .github/
│   └── workflows/
│       ├── ci.yml          # CI pipeline
│       └── cd.yml          # CD pipeline
├── scripts/
│   └── train_model.py      # Model training script
├── models/                 # Saved models (generated, not committed)
├── .pre-commit-config.yaml # Pre-commit hooks
├── pyproject.toml          # Tool configuration (black, isort, mypy, pytest, coverage)
├── requirements.txt
├── requirements-dev.txt    # Development dependencies
├── Dockerfile
└── README.md
```

## Quick Start

### 1. Clone and Set Up

```bash
git clone https://github.com/NgoKhoi1/ddm501-lab3-starter.git
cd ddm501-lab3-starter

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/macOS
.\venv\Scripts\Activate.ps1     # Windows PowerShell
```

### 2. Install Dependencies

`scikit-surprise==1.1.3` is only published as source code, so it has to be
compiled against the pinned numpy. Install it first, then install the rest:

```bash
pip install setuptools wheel "cython<3" numpy==1.26.2
pip install scikit-surprise==1.1.3 --no-build-isolation
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

Compiling needs a C compiler:

- **Windows:** Visual Studio Build Tools, with the "Desktop development with C++" workload.
- **macOS:** Xcode Command Line Tools (`xcode-select --install`).
- **Linux:** `build-essential`.

### 3. Train the Model

```bash
python scripts/train_model.py
```

The script downloads MovieLens 100K on the first run and saves
`models/svd_model.pkl`. Training uses a fixed seed (`random_state=42`), so every
machine produces the same model.

> **SSL error on Windows** (`CERTIFICATE_VERIFY_FAILED`) when downloading the dataset?
> Download it with curl, which uses the Windows certificate store, then run the script again:
>
> ```powershell
> curl.exe -L -o ml-100k.zip https://files.grouplens.org/datasets/movielens/ml-100k.zip
> Expand-Archive ml-100k.zip "$HOME\.surprise_data\ml-100k"
> ```

### 4. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=term --cov-report=html

# Run a specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/data/ -v
pytest tests/model/ -v
```

### 5. Code Quality Checks

```bash
# Install pre-commit hooks (once)
pre-commit install

# Run all checks manually
pre-commit run --all-files

# Individual tools
black app/ tests/ scripts/
isort app/ tests/ scripts/
flake8 app/ tests/ scripts/
mypy app/
```

### 6. Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs are at http://localhost:8000/docs.

### 7. Run with Docker

```bash
python scripts/train_model.py          # the image includes models/svd_model.pkl
docker build -t movie-rating-api .
docker run -p 8000:8000 movie-rating-api
```

## Completed Tasks

### Test Files
- [x] `tests/unit/test_model.py` - Unit tests for model class (13 tests)
- [x] `tests/unit/test_schemas.py` - Schema validation tests (18 tests)
- [x] `tests/integration/test_api.py` - API endpoint tests (26 tests)
- [x] `tests/data/test_data_quality.py` - Data quality tests (17 tests)
- [x] `tests/model/test_model_behavior.py` - Behavioral tests (16 tests)

### CI/CD Files
- [x] `.github/workflows/ci.yml` - CI pipeline
- [x] `.github/workflows/cd.yml` - CD pipeline (BONUS)
- [x] `.pre-commit-config.yaml` - Pre-commit hooks

### Documentation
- [x] [`docs/TESTING_STRATEGY.md`](docs/TESTING_STRATEGY.md) - Testing strategy document
- [x] README updated

## Test Types

The full rationale for each layer is in the [Testing Strategy](docs/TESTING_STRATEGY.md).

### Unit Tests
Test individual functions and classes in isolation.

```python
def test_model_loads_successfully(trained_model):
    assert trained_model.is_loaded()
```

### Integration Tests
Test component interactions and API endpoints.

```python
def test_predict_valid_request(test_client):
    response = test_client.post("/predict", json={"user_id": "196", "movie_id": "242"})
    assert response.status_code == 200
```

### Data Tests
Validate data quality and schema.

```python
def test_ratings_in_valid_range(sample_ratings):
    for r in sample_ratings:
        assert 1.0 <= r["rating"] <= 5.0
```

### Behavioral Tests
Test model behavior patterns.

```python
def test_same_input_same_output(trained_model):
    result1 = trained_model.predict("196", "242")
    result2 = trained_model.predict("196", "242")
    assert result1 == result2
```

## Test Coverage

**90 tests, 86% coverage** (minimum required: 80%).

| File | Statements | Missed | Coverage |
|---|---|---|---|
| `app/__init__.py` | 1 | 0 | 100% |
| `app/config.py` | 13 | 0 | 100% |
| `app/main.py` | 51 | 10 | 80% |
| `app/model.py` | 42 | 9 | 79% |
| `app/schemas.py` | 32 | 0 | 100% |
| **Total** | **139** | **19** | **86%** |

The uncovered lines are error-handling paths (model not loaded, unexpected
prediction errors). Every CI run uploads the full HTML report as the
`coverage-report` artifact. Open a run in the **Actions** tab to download it.

## CI/CD Pipeline

### Continuous Integration (`ci.yml`)

Runs on every push to `main`/`develop` and every pull request to `main`.

```
lint ──────────► test ──────────┐
                                ├──► build (Docker)
type-check ─────────────────────┘
```

| Job | What it does |
|---|---|
| **Lint** | flake8, black and isort checks |
| **Type Check** | mypy, with type hints required on every function |
| **Run Tests** | Trains the model, runs all tests with coverage, uploads the coverage report |
| **Build Docker Image** | Builds the image and checks that `/health` and `/predict` respond inside the container |

### Continuous Deployment (`cd.yml`)

Triggered by pushing a version tag:

```bash
git tag v1.0.0
git push origin v1.0.0
```

1. Trains the model, then builds the Docker image and pushes it to Docker Hub
   (`<user>/movie-rating-api:latest` and `:v1.0.0`).
2. Creates a GitHub Release.
3. Deploys to staging, then production (placeholder steps).

Required repository secrets (**Settings → Secrets and variables → Actions**):

| Secret | Used for |
|---|---|
| `DOCKER_USERNAME` | Docker Hub username |
| `DOCKER_PASSWORD` | Docker Hub access token |
| `CODECOV_TOKEN` | Optional: uploads coverage to Codecov |

## Grading Rubric

| Criteria | Weight |
|----------|--------|
| Test Coverage (unit, integration, data, model) | 30% |
| CI/CD Pipeline | 30% |
| Code Quality | 20% |
| Documentation | 20% |

**Minimum Requirements:**
- [x] 80% code coverage (86%)
- [x] All CI checks passing
- [x] Pre-commit hooks configured

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [pre-commit](https://pre-commit.com/)
- [Black](https://black.readthedocs.io/)
- [Flake8](https://flake8.pycqa.org/)
- [mypy](https://mypy.readthedocs.io/)

## Submission

1. Complete all TODO items
2. Ensure all tests pass
3. Achieve minimum 80% coverage
4. Push to GitHub with CI badge
5. Submit repository link via LMS

## License

MIT License - For educational purposes only.
