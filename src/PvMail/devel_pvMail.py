#!/usr/bin/env python

'''developer testing of pvMail'''


import sys
import pvMail

# python pvMail.py pvMail:trigger pvMail:message developer@email.tld -l mylog.log -g &
sys.argv.append('pvMail:trigger')
sys.argv.append('pvMail:message')
sys.argv.append('developer@email.tld')
sys.argv.append('-l mylog.log')
sys.argv.append('-g')
pvMail.main()


########### SVN repository information ###################
# $Date: 2014-07-10 13:38:52 -0500 (Thu, 10 Jul 2014) $
# $Author: jemian $
# $Revision: 1578 $
# $URL: https://subversion.xray.aps.anl.gov/bcdaext/pvMail/trunk/src/PvMail/devel_pvMail.py $
# $Id: devel_pvMail.py 1578 2014-07-10 18:38:52Z jemian $
########### SVN repository information ###################
