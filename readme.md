# when-poop-bot

# Install/Local dev
```
uv sync

or 

python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

# Test
```
uv run python -m pytest

or 

python -m pytest
```

# Deploying
- Github Action for main code base
- Dependencies are added as lambda layers (see below) manually

## Lambda Layers / Runtime Dependencies
- matplotlib ([Layer](https://api.klayers.cloud/api/v2/p3.11/layers/latest/ap-southeast-1/html))
- numpy ([Layer](https://api.klayers.cloud/api/v2/p3.11/layers/latest/ap-southeast-1/html))
- [july](git+https://github.com/thoellrich/july.git@35833e4c3d84b07faedeb128d670520b2d779932) - without deps (use forked repo due to unresolved errors on main package)

# New features
1) rate limiting feature
2) cloudwatch metrics for monitoring