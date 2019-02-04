#!/home/pi/miniconda3/bin/python3

import sys
import os
import time
import cgi
import cgitb
cgitb.enable()

sys.path.insert(1, os.path.join(sys.path[0], '..')) # look in parent folder for modules too
import sht31


print("Content-Type: text/html\n")

print(
"""
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<head>
<meta charset="utf-8"/>
<title>FOOBAR</title>
</head>
<body>
""")

print("<h1> Hello there world </h1>")

print("<pre>")
sht31.run_test()
print("</pre>")

print("""
</body>
</html>
""")
