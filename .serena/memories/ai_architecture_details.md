# AI Architecture and Technical Details

## AI Code Generation Process
1. **Input Processing**: User text conditions in Japanese
2. **Prompt Engineering**: Combines user input with detailed template prompt (587 lines)
3. **API Call**: Sends to Anthropic Claude API (claude-3-7-sonnet-20250219)
4. **Code Generation**: Produces Python code with ImagePatch-based anomaly detection
5. **Code Formatting**: Cleans and structures the generated code

## Object Detection Pipeline
1. **Model**: Grounding DINO (IDEA-Research/grounding-dino-base via Hugging Face)
2. **Caching**: Model and processor cached globally for performance
3. **Detection Process**: 
   - Image preprocessing and text query processing
   - Object detection with confidence scoring
   - Post-processing (NMS, overlap removal, large box filtering)

## ImagePatch Class Architecture
- **Purpose**: Represents detected objects as image regions
- **Core Properties**: coordinates (x1,y1,x2,y2), dimensions, centers, detection scores
- **Key Methods**:
  - `find()`: Detect objects in the patch
  - `overlaps()`: Check intersection with other patches
  - `expand_patch_with_surrounding()`: Expand detection area
- **Usage**: Generated code uses ImagePatch instances for anomaly logic

## Execution Flow
1. **Code Generation**: AI generates ImagePatch-based detection code
2. **Dynamic Execution**: Code executed in isolated namespace
3. **Object Detection**: Grounding DINO finds objects based on generated queries
4. **Anomaly Scoring**: Returns 0 (normal) or 1 (anomaly) based on conditions
5. **Result Display**: Shows detection results and anomaly score in UI

## Performance Optimizations
- Global model caching to avoid repeated loading
- Image preprocessing optimizations
- Non-maximum suppression for duplicate removal
- Memory-efficient patch processing