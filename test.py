"""
ccextractor-web | test.py

Author   : Saurabh Shrivastava
Email    : saurabh.shrivastava54@gmail.com
Link     : https://github.com/saurabhshr

"""

from mod_dashboard.models import Platforms

for p in Platforms:
    print(p.value)
    print(Platforms(p.value).name)
