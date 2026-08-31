# DE Team Coding Standards

You are assisting a Data Engineering team with Python pipeline development and Perl-to-Python modernisation.

## Python Standards
All function arguments must have type hints. All return types must be declared.
Every pipeline function must log on entry and exit using the project logger.
Use pathlib.Path for all file operations. Never use os.path.
Handle None explicitly on all critical fields (instrument_id, exchange_code, price, volume, record_id).
Use collections.Counter for counting and frequency analysis.

## Perl-to-Python Conversion
Do not produce a line-by-line translation. Produce idiomatic Python.
Map LWP::UserAgent to requests.Session. Map JSON::from_json to json module.
Map Time::HiRes to time.time(). Map Data::Dumper to pprint.
Do not call exit() inside library code. Raise exceptions instead.
