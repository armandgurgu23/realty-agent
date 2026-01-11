
# This code has only been tested on my personal Mac laptop. It may not work for Windows.
curl -LsSf https://astral.sh/uv/install.sh | sh
uv install
uv run python -m src.chat_with_realty
