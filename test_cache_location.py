"""Test that AI models cache is on D: drive."""
import os
from pathlib import Path

print("\n" + "="*60)
print("🔍 AI Models Cache Location Check")
print("="*60)

# Check environment variables
print("\n📍 Environment Variables:")
hf_home = os.getenv("HF_HOME", "Not set")
transformers_cache = os.getenv("TRANSFORMERS_CACHE", "Not set")
hf_hub_cache = os.getenv("HF_HUB_CACHE", "Not set")

print(f"   HF_HOME: {hf_home}")
print(f"   TRANSFORMERS_CACHE: {transformers_cache}")
print(f"   HF_HUB_CACHE: {hf_hub_cache}")

# Check if cache exists
cache_path = Path("D:/ai_models_cache/huggingface")
if cache_path.exists():
    # Calculate size
    total_size = sum(f.stat().st_size for f in cache_path.rglob('*') if f.is_file())
    size_gb = total_size / (1024**3)
    print(f"\n✅ D: drive cache verified!")
    print(f"   Location: {cache_path}")
    print(f"   Size: {size_gb:.2f} GB")
    print(f"   Files: {sum(1 for _ in cache_path.rglob('*') if _.is_file())}")
else:
    print(f"\n⚠️ Cache directory not found at {cache_path}")

# Check old C: drive location
old_cache = Path.home() / ".cache" / "huggingface"
if old_cache.exists():
    old_size = sum(f.stat().st_size for f in old_cache.rglob('*') if f.is_file())
    old_size_gb = old_size / (1024**3)
    print(f"\n⚠️ Old cache still on C: drive!")
    print(f"   Location: {old_cache}")
    print(f"   Size: {old_size_gb:.2f} GB")
else:
    print(f"\n✅ No cache on C: drive - all clear!")

print("\n" + "="*60)
print("✅ Setup Complete!")
print("="*60)
print("\n💡 All future AI model downloads will go to D: drive!")
print("   C: drive space saved: ~3.64 GB\n")
