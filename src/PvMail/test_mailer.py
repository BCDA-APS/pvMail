'''
unit tests for the spec module
'''

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


import datetime
import socket
import sys
import unittest

import mailer


class Test(unittest.TestCase):

    def setUp(self):
        pass

#     def tearDown(self):
#         pass

    def test_sendmail(self):
        # this should fail on windows
        recipients = ["jemian@anl.gov"]
        subject = "pvMail test using sendmail"
        #message = "\n".join(["%s\t%s" % (k, v) for k, v in sorted(os.environ.items())])
        message = "pvMail mailer test_sendmail"
        mailer.sendMail_sendmail(subject, message, recipients)
    
    def test_sendmail_2(self):
        # this should fail on windows
        recipients = ["jemian", "prjemian"]
        message = ''
        message += 'host: %s\n' % socket.gethostname()
        message += 'date: %s (UNIX, not PV)\n' % datetime.datetime.now()
        message += 'program: %s\n' % sys.argv[0]
        message += 'recipients: %s\n' % ", ".join(recipients)
        subject = "pvMail mailer test_sendmail_2"
        mailer.sendMail_sendmail(subject, message, recipients)

    def test_smtp(self):
        subject = "pvMail mailer test_smtp"
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
