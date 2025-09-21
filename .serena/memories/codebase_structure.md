# Codebase Structure

## Directory Layout
```
streamlit-ad-app/
├── app/
│   ├── main.py                    # Main Streamlit application
│   └── utils/
│       ├── code_generator.py      # AI code generation module
│       ├── code_executor.py       # Code execution & object detection
│       ├── template_prompt.py     # Prompt templates for AI
│       ├── apple_strawberry.png   # Default sample image
│       └── __init__.py
├── .github/workflows/
│   └── deploy.yml                 # CI/CD for EC2 deployment
├── .devcontainer/                 # Dev container configuration
├── requirements.txt               # Dependencies (pip format)
├── pyproject.toml                 # Project config (uv format)
├── Dockerfile                     # Container configuration
└── README.md                      # Project documentation
```

## Key Components

### Main Application (app/main.py)
- Streamlit UI with step-by-step workflow
- API key management (environment variable or UI input)
- Image upload and condition input handling
- Integration with code generation and execution modules

### Core Modules
- **code_generator.py**: Interfaces with Anthropic Claude API to generate anomaly detection code
- **code_executor.py**: Contains ImagePatch class and object detection logic using Grounding DINO
- **template_prompt.py**: Contains the detailed prompt template for AI code generation

### ImagePatch Class
Core class for representing image regions with object detection results:
- Properties: coordinates (x1,y1,x2,y2), dimensions, centers
- Methods: find(), overlaps(), expand_patch_with_surrounding()
- Used in generated anomaly detection programs