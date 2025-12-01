Environment variables

This project reads the following environment variables (preferred method: define them in your shell or in a local `.env` file that you DO NOT commit):

- HUGGINGFACE_HUB_TOKEN: (optional) Hugging Face Hub token to increase API rate limits.
- GITHUB_TOKEN: (optional) GitHub Personal Access Token for authenticated requests.
- LOG_FILE: path to write log output. If unset, logging will default to stdout.
- LOG_LEVEL: logging verbosity (0=silent, 1=info, 2=debug). Default is 0.

Example (zsh):

```bash
export HUGGINGFACE_HUB_TOKEN="hf_..."
export GITHUB_TOKEN="ghp_..."
export LOG_FILE="$PWD/logs/app.log"
export LOG_LEVEL=1
```

Do NOT commit real tokens to the repository. If a token has been accidentally committed, revoke it immediately via GitHub settings.
