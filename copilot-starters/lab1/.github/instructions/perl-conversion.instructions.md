---
applyTo: "**/*.pl,**/*.py"
---
When converting Perl to Python:
- Translate LWP::UserAgent to requests.Session
- Translate JSON qw(from_json to_json) to import json
- Use collections.Counter for hash counting patterns
- Use pathlib.Path for all file I/O
- Add type hints to every function
- Do not translate Perl regex syntax literally -- use the re module
