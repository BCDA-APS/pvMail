#!/usr/bin/env python

'''
unit tests for the spec module
'''

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


import logging
import time
import unittest

import cli


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def test_sendmail(self):
        logging.basicConfig(filename=cli.LOG_FILE,level=logging.INFO)
        cli.logger("startup")
        pvm = cli.PvMail()
        pvm.recipients = ['prjemian@gmail.com']
        pvm.triggerPV = "pvMail:trigger"
        pvm.messagePV = "pvMail:message"
        retry_interval_s = 0.05
        end_time = time.time() + 60
        report_time = time.time() + 5.0
        pvm.do_start()
        while time.time() < end_time:
            if time.time() > report_time:
                report_time = time.time() + 5.0
                cli.logger("time remaining: %.1f seconds ..." % (end_time - time.time()))
            time.sleep(retry_interval_s)
        pvm.do_stop()


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    #unittest.main()

    suite = unittest.TestLoader().loadTestsFromTestCase(Test)
    unittest.TextTestRunner(verbosity=2).run(suite)
