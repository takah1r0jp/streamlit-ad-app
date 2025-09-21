# Task Completion Checklist

## Code Quality Checks
Since this project doesn't have explicit linting/testing commands configured, perform these manual checks:

1. **Syntax Validation**
   ```bash
   python -m py_compile app/main.py
   python -m py_compile app/utils/*.py
   ```

2. **Import Verification**
   ```bash
   python -c "from app.utils import code_generator, code_executor, template_prompt"
   ```

3. **Streamlit App Validation**
   ```bash
   # Test that the app starts without errors
   uv run python -m streamlit run app/main.py --server.headless true
   ```

## Functionality Testing
1. **Manual Testing Steps**:
   - Verify API key input works
   - Test image upload functionality
   - Check condition input and validation
   - Test code generation (requires valid API key)
   - Test code execution with sample image

2. **Dependencies Check**:
   ```bash
   uv sync  # Ensure all dependencies are properly installed
   ```

## Git Operations
```bash
git status                    # Check working directory status
git add .                     # Stage changes
git commit -m "description"   # Commit with descriptive message
git push origin main          # Push to main branch
```

## Deployment Verification
- Check that Docker build succeeds
- Verify environment variables are properly set
- Test that the application runs in container environment

## Notes
- No automated testing framework detected
- No linting tools (black, flake8, etc.) configured
- Manual verification is primary quality assurance method
- Focus on functional testing over unit testing