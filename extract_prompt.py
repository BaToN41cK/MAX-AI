import re
with open(r'max_ai\core\agent.py', 'r', encoding='utf-8') as f:
    content = f.read()
pattern = re.compile(r'mistral_prompt = f\"\"\"[\s\S]*?\"\"\"')
match = pattern.search(content)
if match:
    print(repr(match.group(0)))
else:
    print('Not found')
