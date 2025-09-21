# Suggested Commands for Development

## Package Management
```bash
# Install dependencies (preferred)
uv sync

# Alternative with pip
pip install -r requirements.txt
```

## Running the Application
```bash
# Run with uv (preferred)
uv run python -m streamlit run app/main.py

# Alternative with pip environment
streamlit run app/main.py
```

## Environment Setup
```bash
# Set API key (required for AI functionality)
export ANTHROPIC_API_KEY="your_api_key_here"
```

## Development Utilities
```bash
# List directory contents
ls -la

# Search for patterns in code
grep -r "pattern" app/

# View file contents
cat filename

# Git operations
git status
git add .
git commit -m "message"
git push origin main
```

## Docker Operations
```bash
# Build Docker image
docker build -t streamlit-ad-app .

# Run container
docker run -d -p 8501:8501 -e ANTHROPIC_API_KEY="your_key" --name streamlit-ad-app-container streamlit-ad-app

# Stop container
docker stop streamlit-ad-app-container
docker rm streamlit-ad-app-container
```

## System Information
- Platform: Darwin (macOS)
- Git repository: Yes
- Default branch: main