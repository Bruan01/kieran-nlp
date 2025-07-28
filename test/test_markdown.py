#!/usr/bin/env python3

import markdown

test_md = """
| 列1 | 列2 | 列3 |
| --- | --- | --- |
| A   | B   | C   |
| D   | E   | F   |
"""

html = markdown.markdown(test_md, extensions=['tables', 'fenced_code', 'codehilite'])
print(html)