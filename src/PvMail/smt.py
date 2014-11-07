#!/usr/bin/env python

'''
Test the pvMail.sendMail_sendmail() method while it is being "improved".
'''

import pvMail
import os
import logging

recipients = ["jemian@anl.gov"]
subject = "pvMail test using sendmail"
message = "\n".join(["%s\t%s" % (k, v) for k, v in sorted(os.environ.items())])

#message = "This is a short test"

logging.basicConfig(level=logging.INFO)
pvMail.logger("startup")
pvMail.sendMail_sendmail(subject, message, recipients)
pvMail.logger("finished")
