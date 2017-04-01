#!/usr/bin/env python

'''developer testing of pvMail'''


import sys
import cli

# python pvMail.py pvMail:trigger pvMail:message developer@email.tld -l mylog.log -g &
sys.argv.append('pvMail:trigger')
sys.argv.append('pvMail:message')
sys.argv.append('developer@email.tld')
sys.argv.append('-l mylog.log')
sys.argv.append('-g')
cli.main()
