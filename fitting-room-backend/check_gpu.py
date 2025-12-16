import torch
import onnxruntime as ort

print(f"🔥 PyTorch Version: {torch.__version__}")
print(f"🔥 CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"   👉 Device Name: {torch.cuda.get_device_name(0)}")
else:
    print("   ❌ GPU를 찾을 수 없습니다. (CPU 모드로 동작 중)")

print(f"\n🚀 ONNX Runtime Device: {ort.get_device()}")
print(f"   👉 Providers: {ort.get_available_providers()}")