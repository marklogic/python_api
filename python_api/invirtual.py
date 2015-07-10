import sys

if hasattr(sys, 'real_prefix'):
    exit(0)
else:
    print("**************************************")
    print("Not in virtual environment.")
    print("**************************************")
    exit(1)


