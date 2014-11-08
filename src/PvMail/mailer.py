
'''
send a message by email to one or more recipients (by SMTP or sendmail)
'''


import datetime
import os
import sys


def sendMail_sendmail(subject, message, recipients, logger = None):
    '''
    send an email message using sendmail (linux only)
    
    :param str subject: short text for email subject
    :param str message: full text of email body
    :param [str] recipients: list of email addresses to receive the message
    :param obj logger: optional message logging method
    '''
    global gui_object
    
    from_addr = sys.argv[0]
    to_addr = str(" ".join(recipients))

    # TODO: replace with email package?
    cmd = 'the mail configuration has not been set yet'
    if 'el' in str(os.uname()):         # RHEL uses postfix
        email_program = '/usr/lib/sendmail'
        mail_command = "%s -F %s -t %s" % (email_program, from_addr, to_addr)
        mail_message = [mail_command, "Subject: "+subject, message]
        cmd = '''cat << +++ | %s\n+++''' % "\n".join(mail_message)
    
    if 'Ubuntu' in str(os.uname()):     # some Ubuntu (11) uses exim, some (10) postfix
        email_program = '/usr/bin/mail'
        mail_command = "%s %s" % (email_program, to_addr)
        content = '%s\n%s' % (subject, message)
        # TODO: needs to do THIS
        '''
        cat /tmp/message.txt | mail jemian@anl.gov
        '''
        cmd = '''echo %s | %s''' % (content, mail_command)

    iso8601 = str(datetime.datetime.now())
    msg = "(%s) sending email to: %s" % (iso8601, to_addr)
    if logger is not None:
        logger(msg)
    if gui_object is not None:
        gui_object.SetStatus(msg)   # FIXME: get the GUI status line to update

    try:
        if logger is not None:
            logger( "email command:\n" + cmd )
        if os.path.exists(email_program):
            os.popen(cmd)    # send the message
        else:
            if logger is not None:
                logger( 'email program (%s) does not exist' % email_program )
    except Exception, err_msg:
        #err_msg = traceback.format_exc()
        final_msg = "cmd = %s\ntraceback: %s" % (cmd, err_msg)
        logger(final_msg)
