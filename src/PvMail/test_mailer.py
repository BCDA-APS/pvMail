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


import unittest

import mailer


class Test(unittest.TestCase):

    def setUp(self):
        pass

#     def tearDown(self):
#         pass

    def test_short(self):
        recipients = ["jemian@anl.gov"]
        subject = "pvMail test using sendmail"
        #message = "\n".join(["%s\t%s" % (k, v) for k, v in sorted(os.environ.items())])
        
        message = "This is a short test"
        
        mailer.sendMail_sendmail(subject, message, recipients)

    def test_smtp(self):
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
