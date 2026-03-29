import re

with open("frontend/app/dashboard/page.tsx", "r") as f:
    content = f.read()

# Remove the Open-Meteo block
content = re.sub(r'<div className="rounded-full border border-emerald-500/30 bg-emerald-950/30 px-3 py-1\.5">.*?</div>', '', content, flags=re.DOTALL)

# Remove the Back to Landing block
content = re.sub(r'<Link\s+href="/"[^>]*>\s*Back to Landing\s*</Link>', '', content, flags=re.DOTALL)

with open("frontend/app/dashboard/page.tsx", "w") as f:
    f.write(content)

