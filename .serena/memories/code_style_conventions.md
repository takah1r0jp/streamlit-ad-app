# Code Style and Conventions

## Language and Comments
- **Primary Language**: Japanese (comments, UI text, documentation)
- **Variable/Function Names**: English (following Python conventions)
- **Documentation**: Mixed Japanese/English

## Python Style
- **Import Organization**: Standard library, third-party, local imports
- **Naming Conventions**: 
  - snake_case for functions and variables
  - PascalCase for classes (e.g., ImagePatch)
  - ALL_CAPS for constants
- **Type Hints**: Not extensively used in current codebase
- **Docstrings**: Minimal usage, mostly inline comments

## Streamlit Patterns
- Page configuration at top of main.py
- CSS styling embedded as markdown
- Step-by-step UI workflow with status indicators
- Session state management for user inputs
- Column layouts for responsive design

## File Organization
- Utils modules in `app/utils/` directory
- Each utility has focused responsibility:
  - code_generator: AI interaction
  - code_executor: Object detection and execution
  - template_prompt: Prompt engineering
- No separate test directory observed

## Dependencies Management
- Uses both requirements.txt and pyproject.toml
- Prefers uv package manager over pip
- Specific version pinning for all dependencies