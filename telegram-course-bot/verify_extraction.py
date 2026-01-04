from parser import resolve_coursevania_link
import sys

# Test URL provided by user
url = "https://coursevania.com/courses/mastering-adobe-illustrator-projects-build-your-portfolio/"

print(f"Testing resolution for: {url}")
resolved = resolve_coursevania_link(url)

print(f"Result: {resolved}")

if "udemy.com" in resolved:
    print("✅ SUCCESS: Resolved to Udemy link")
    sys.exit(0)
else:
    print("❌ FAILURE: Did not resolve to Udemy link")
    sys.exit(1)
