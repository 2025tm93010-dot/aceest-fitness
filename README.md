# ACEest Fitness & Gym — CI/CD Pipeline

A Flask service for managing gym members and workout logs, delivered through an automated
pipeline: **Git/GitHub → Pytest → Docker → GitHub Actions → Jenkins**.

## Project structure
```
app.py                  Flask application (app factory + routes)
tests/test_app.py       Pytest suite
requirements.txt        Runtime dependencies (Flask, gunicorn)
requirements-dev.txt    Adds pytest + flake8
Dockerfile              Multi-stage: base -> test -> runtime
Jenkinsfile             Jenkins declarative pipeline
.github/workflows/main.yml   GitHub Actions workflow
```

## API
| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Liveness check |
| GET | `/plans` | Membership plans and prices |
| POST | `/members` | Create member `{"name": "...", "plan": "basic|premium|elite"}` |
| GET | `/members`, `/members/<id>` | List / fetch members |
| DELETE | `/members/<id>` | Remove a member |
| POST | `/members/<id>/workouts` | Log workout `{"exercise": "...", "minutes": 30}` |
| GET | `/members/<id>/summary` | Session count and total minutes |

Data is held in memory (resets on restart) to keep the focus on the DevOps workflow.

## Local setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
python app.py                  # http://localhost:5000
curl localhost:5000/health
```

## Run tests manually
```bash
pytest -v                      # locally
flake8 .                       # lint

# inside Docker (same as CI)
docker build --target test -t aceest-fitness-test .
docker run --rm aceest-fitness-test
```

## Docker
```bash
docker build --target runtime -t aceest-fitness .
docker run -p 5000:5000 aceest-fitness
```
The runtime image uses `python:3.12-slim`, installs only runtime dependencies, excludes tests,
runs as a non-root user, serves via gunicorn and defines a `HEALTHCHECK`.

## GitHub Actions (`.github/workflows/main.yml`)
Triggered on every `push` and `pull_request`:
1. **Build & Lint** – install deps, `flake8`, `compileall` syntax check.
2. **Docker image assembly** – build the `runtime` target.
3. **Automated testing** – build the `test` target and run Pytest inside the container.

## Jenkins (`Jenkinsfile`)
Jenkins acts as the secondary, controlled build gate:
1. Pull latest code from GitHub (`checkout scm`).
2. Clean build: fresh virtualenv, install deps, lint.
3. Run Pytest.
4. `docker build --no-cache` and run the containerised tests.

**Setup:** install Jenkins with Python 3 and Docker available to the `jenkins` user →
*New Item → Pipeline* → "Pipeline script from SCM" → Git → your repo URL → script path
`Jenkinsfile`. Optionally enable "GitHub hook trigger" or "Poll SCM".

## Suggested Git workflow
```bash
git init && git branch -M main
git add app.py requirements.txt && git commit -m "feat: add Flask app with member and workout endpoints"
git add tests requirements-dev.txt .flake8 && git commit -m "test: add pytest suite"
git add Dockerfile .dockerignore && git commit -m "build: add multi-stage Dockerfile"
git add .github && git commit -m "ci: add GitHub Actions workflow"
git add Jenkinsfile && git commit -m "ci: add Jenkins pipeline"
git add README.md .gitignore && git commit -m "docs: add README"
git remote add origin https://github.com/2025tm93010-dot/aceest-fitness.git && git push -u origin main
```
