from python:3.12-bookworm
arg INSTALL_PREFIX=/usr/local
env PYTHONUNBUFFERED=1
env VIRTUAL_ENV=/venv
env POETRY_NO_INTERACTION=1
env POETRY_VIRTUALENVS_CREATE=false
env PATH="$VIRTUAL_ENV/bin:$PATH"
run pip install poetry
run python -m venv $VIRTUAL_ENV
workdir /app
copy pyproject.toml poetry.lock ./
run poetry install --no-root
copy ./ .
run poetry install --only-root
