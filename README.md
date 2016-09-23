# L4-7_Automation
This tool will download configurations from APIC controller and alter them based on tests defined by users. It then post back to APIC to achieve config add or removal. Ixia traffic is verified.

File structure:
- tests/* (define tests in YAML)
- lib/* (library files)
- qual.py

prerequisite:
- pip install -U pytest

To start:
- python qual.py -t [test_definitions.yaml] --ixia/--no-ixia
