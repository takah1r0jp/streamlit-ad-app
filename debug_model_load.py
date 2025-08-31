#!/usr/bin/env python3
"""
Grounding DINOモデルのロード検証スクリプト
EC2コンテナ内でのメモリ使用量とモデルロード成功/失敗を確認
"""

import psutil
import torch
import time
import gc
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection

def print_memory_usage(stage):
    """メモリ使用量を表示"""
    memory = psutil.virtual_memory()
    print(f"[{stage}] Available RAM: {memory.available / (1024**3):.2f} GB")
    print(f"[{stage}] Used RAM: {(memory.total - memory.available) / (1024**3):.2f} GB")
    print(f"[{stage}] Memory usage: {memory.percent}%")
    print("-" * 50)

def main():
    print("=== Grounding DINO Model Load Test ===")
    print_memory_usage("Initial")
    
    print(f'PyTorch version: {torch.__version__}')
    print(f'CUDA available: {torch.cuda.is_available()}')
    print(f'CUDA device count: {torch.cuda.device_count() if torch.cuda.is_available() else 0}')
    
    if torch.cuda.is_available():
        print(f'CUDA device name: {torch.cuda.get_device_name(0)}')
    
    print("-" * 50)
    
    try:
        model_id = 'IDEA-Research/grounding-dino-base'
        print(f'Model ID: {model_id}')
        print('Starting model load test...')
        
        # Step 1: プロセッサロード
        print('\n1. Loading processor...')
        start_time = time.time()
        processor = AutoProcessor.from_pretrained(model_id)
        processor_time = time.time() - start_time
        print(f'Processor loaded successfully! ({processor_time:.2f}s)')
        print_memory_usage("After Processor Load")
        
        # Step 2: モデルロード
        print('\n2. Loading model...')
        start_time = time.time()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f'Using device: {device}')
        
        model = AutoModelForZeroShotObjectDetection.from_pretrained(model_id)
        model = model.to(device)
        model_time = time.time() - start_time
        
        print(f'Model loaded successfully! ({model_time:.2f}s)')
        print_memory_usage("After Model Load")
        
        # Step 3: 簡単な推論テスト
        print('\n3. Testing inference...')
        from PIL import Image
        import numpy as np
        
        # ダミー画像作成
        dummy_image = Image.fromarray(np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8))
        
        start_time = time.time()
        inputs = processor(images=dummy_image, text="apple.", return_tensors="pt").to(device)
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        inference_time = time.time() - start_time
        print(f'Inference test completed! ({inference_time:.2f}s)')
        print_memory_usage("After Inference")
        
        # Step 4: メモリクリーンアップテスト
        print('\n4. Testing memory cleanup...')
        del model
        del processor
        del inputs
        del outputs
        gc.collect()
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        print_memory_usage("After Cleanup")
        
        print("\n✅ ALL TESTS PASSED!")
        
    except Exception as e:
        print(f'\n❌ Model loading failed: {e}')
        print("\nDetailed error:")
        import traceback
        traceback.print_exc()
        
        print_memory_usage("After Error")
        
        # メモリ不足の場合の対策提案
        if "out of memory" in str(e).lower() or "memory" in str(e).lower():
            print("\n🔧 MEMORY ISSUE DETECTED!")
            print("Suggested solutions:")
            print("1. Increase EC2 instance to t3.medium (4GB RAM)")
            print("2. Add swap memory: sudo swapon /swapfile") 
            print("3. Use smaller model: grounding-dino-tiny")

if __name__ == "__main__":
    main()