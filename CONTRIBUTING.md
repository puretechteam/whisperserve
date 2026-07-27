# Contributing to WhisperServe

Thank you for your interest in contributing to WhisperServe. This document provides guidelines and instructions to help you get started.

## Getting Started

### Prerequisites

- Python 3.11 or later
- pip
- Docker (optional, for running the service in a container)

### Setup

1. Fork the repository on GitHub.
2. Clone your fork locally:

```bash
git clone https://github.com/YOUR_USERNAME/whisperserve.git
cd whisperserve
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

4. Copy the example environment file and configure your settings:

```bash
cp .env.example .env
```

## Development Workflow

### Running the Service

Start the development server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Code Style

- Follow PEP 8 conventions.
- Use type hints where applicable.
- Keep functions and modules focused and small.
- Run syntax checks before committing:

```bash
find . -name "*.py" -not -path "./.github/*" -not -path "./.venv/*" | while read f; do
  python -m py_compile "$f"
done
```

### Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org/) format. Commit messages must use one of the following prefixes:

- `feat:` — a new feature (triggers a MINOR version bump)
- `fix:` — a bug fix (triggers a PATCH version bump)
- `BREAKING CHANGE:` — a breaking change (triggers a MAJOR version bump)
- `chore:` — maintenance tasks (no version bump)
- `docs:` — documentation changes (no version bump)
- `refactor:` — code restructuring (no version bump)
- `test:` — test additions or changes (no version bump)

### Pull Requests

1. Create a new branch for your feature or bug fix:

```bash
git checkout -b describe-your-change
```

2. Make your changes and commit them with clear, descriptive messages.
3. Push your branch to your fork and open a Pull Request against the `main` branch.
4. Ensure all CI checks pass before requesting review.

## Issue Reports

- Use the **Bug Report** template for reporting bugs.
- Use the **Feature Request** template for suggesting new features.
- Search existing issues before opening a new one to avoid duplicates.

## Testing

If a test suite exists, run it with:

```bash
pytest
```

## Questions?

Open a discussion or reach out to the maintainers if you have any questions.