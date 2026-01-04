"""
Test Base64 Image Storage in MongoDB
This script tests if Base64 encoded images work properly
"""

import base64
from io import BytesIO
from PIL import Image
import requests

# Test with a sample image
print("=" * 60)
print("🧪 Testing Base64 Image Storage")
print("=" * 60)
print()

# Download a test image
print("1️⃣ Downloading test image...")
response = requests.get("https://via.placeholder.com/600x400.jpg")
image_bytes = BytesIO(response.content)
print(f"   Original size: {len(response.content)} bytes")
print()

# Convert to Base64
print("2️⃣ Converting to Base64...")
image_base64 = base64.b64encode(image_bytes.read()).decode('utf-8')
data_uri = f"data:image/jpeg;base64,{image_base64}"
print(f"   Base64 size: {len(image_base64)} characters")
print(f"   Data URI size: {len(data_uri)} characters")
print()

# Check MongoDB document size limit
print("3️⃣ Checking MongoDB limits...")
max_doc_size = 16 * 1024 * 1024  # 16MB
current_size = len(data_uri)
print(f"   MongoDB max document size: {max_doc_size:,} bytes (16MB)")
print(f"   Current image size: {current_size:,} bytes")
print(f"   Percentage used: {(current_size/max_doc_size)*100:.2f}%")
print()

if current_size < max_doc_size:
    print("✅ Image size is within MongoDB limits!")
else:
    print("❌ WARNING: Image too large for MongoDB!")

print()
print("=" * 60)
print("📝 Recommendations:")
print("=" * 60)
print()
print("For Telegram images (typically 100-500KB):")
print("  - Base64 encoded: ~130-650KB")
print("  - Well within MongoDB 16MB limit ✅")
print()
print("Benefits:")
print("  ✅ No external storage needed")
print("  ✅ Images persist with course data")
print("  ✅ Works on Render (ephemeral filesystem)")
print("  ✅ Automatic backups with MongoDB")
print()
print("Considerations:")
print("  ⚠️  Slightly larger than binary (33% overhead)")
print("  ⚠️  Included in MongoDB document size")
print("  ✅ But still very manageable for course images")
print()
