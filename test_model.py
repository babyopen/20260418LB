#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'python'))

try:
    from zodiac_ml_predictor import load_model
    model_path = os.path.join(os.path.dirname(__file__), 'python', 'zodiac_model.pkl')
    print(f"尝试加载模型: {model_path}")
    model = load_model(model_path)
    print("✅ 模型加载成功!")
    print(f"模型类型: {type(model)}")
except Exception as e:
    print(f"❌ 模型加载失败: {e}")
    import traceback
    traceback.print_exc()
