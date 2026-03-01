# Factory.ai

For connections workflows to GitHub, ChatGPT, AllBots.com, etc.

## GitHub Repository Connector

`github_connector.py` connects to **all** GitHub repositories the authenticated
user has access to — including the most recently created ones — by paginating
through the GitHub REST API.

### Quick start

```bash
pip install -r requirements.txt
export GITHUB_TOKEN=ghp_your_personal_access_token
python github_connector.py
```

The token needs at least the `repo` scope (or `public_repo` for public repos only).

### Usage as a library

```python
from github_connector import GitHubConnector

connector = GitHubConnector(token="ghp_your_token")  # or rely on GITHUB_TOKEN env var

# Returns all repos sorted newest-first, with full pagination
repos = connector.connect()
for repo in repos:
    print(repo["full_name"], repo["created_at"])
```

### Tests

```bash
pip install pytest
pytest test_github_connector.py -v
```

