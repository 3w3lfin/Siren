'''
 * system Siren 1.1.1
 * https://github.com/3w3lfin
 *
 * Copyright 2016, Ewelina Kośmider
 * 
 * Licensed under the MIT license:
 * http://www.opensource.org/licenses/MIT
 '''
 
#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
