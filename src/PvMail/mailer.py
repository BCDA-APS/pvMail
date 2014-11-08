
'''
send a message by email to one or more recipients (by SMTP or sendmail)
'''


import datetime
import os
import sys

import PvMail


def sendMail_sendmail(subject, message, recipients, logger = None):
    '''
    send an email message using sendmail (linux only)
    
    :param str subject: short text for email subject
    :param str message: full text of email body
    :param [str] recipients: list of email addresses to receive the message
    :param obj logger: optional message logging method
    :returns str: status message or None (if exception)
    '''
    
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

    try:
        if logger is not None:
            logger( "email command:\n" + cmd )
        if os.path.exists(email_program):
            os.popen(cmd)    # send the message
        else:
            if logger is not None:
                logger( 'email program (%s) does not exist' % email_program )
    except Exception, err_msg:
        # TODO: consider passing exception to caller
        #err_msg = traceback.format_exc()
        final_msg = "cmd = %s\ntraceback: %s" % (cmd, err_msg)
        logger(final_msg)
        msg = None
        
    return msg


def sendMail_SMTP(recipient_list, message_text,
                  subject = '[pvMail]',
                  recipient_name = None,
                  sender_email = None,
                  simulation = False,
                  smtp_server = None,
                  ):
    '''
    send an email message using an SMTP server. 
    
    Uses the APS outgoing email server (apsmail.aps.anl.gov) to send the message via SMTP. 
    (Note, this requires the sender_email to be accepted by the SMTP server.)
    Simulation mode disables sending of e-mail messages, to avoid spam.
    
    # TODO: verify that recipient_list is either string, list, or tuple
    :param str recipient_list: A string containing a single e-mail address or a list or tuple (etc.)
       containing a list of strings with e-mail addresses.
    :param str message_text: The text message to be sent.
    :param str subject: a subject to be included in the e-mail message (default: ``[pvMail]``)
    # TODO: verify the autoassignment of @aps.anl.gov
    :param str recipient_name: Recipient(s) of the message. If not specified,
       no "To:" header shows up in the e-mail. 
       This should be an e-mail address or *@aps.anl.gov* is appended.
    :param str sender_email: E-mail address identified as the sender of the e-mail
       (defaults: ``SENDER_EMAIL = "1ID@aps.anl.gov"``). 
       This should be an e-mail address or *@aps.anl.gov* is appended.
    :param bool simulation: set to *True* to use simulation mode (default: *False*)
    :param str smtp_server: SMTP server to be used (default: ``SMTP_SERVER = 'apsmail.aps.anl.gov'``)
       
    Examples:
      >>> msg = 'This is a very short e-mail'
      >>> macros.sendMail_SMTP(['toby@sigmaxi.net','brian.h.toby@gmail.com'],msg, subject='test')

    or with a single address:
      >>> msg = """Dear Brian,
      ...   How about a longer message?
      ... Thanks, Brian
      ... """
      >>> to = "toby@anl.gov"
      >>> macros.sendMail_SMTP(to,msg,recipient_name='monty@python.good',sender_email='spammer@anl.gov')

    A good way to use this routine is within a try/except block:
      >>> userlist = ['user@univ.edu','contact@anl.gov']
      >>> try:
      >>>     for iLoop in range(nLoop):
      >>>         for xLoop in range(nX): 
      >>>             # do something
      >>> except Exception:
      >>>     import traceback
      >>>     msg = "(%s, %s):\n" % (datestamp, __file__)
      >>>     msg += str(traceback.format_exc())
      >>>     subject = '[' + sys.argv[0] + ']'
      >>>     macros.sendMail_SMTP(userlist, msg, subject=subject)
    
    '''
    
    # Postpone imports until needed (lazy import)
    # This routine is not often called
    # The import has a slight delay on first use (which is OK)
    from email.Message import Message
    import smtplib
    
    # assign defaults, as needed
    if sender_email is None:
        sender_email = PvMail.sender_email
    if smtp_server is None:
        smtp_server = PvMail.smtp_server
    
    if not simulation:
        print("e-mail message simulation:")
        #for who in recipient_list:
        #    print("\tTo:\t"+str(who))
        print("\tTo:\t" + ', '.join(recipient_list))
        print("\tFrom:\t"+str(sender_email))
        print("\tSubject:\t"+str(subject))
        print("\tContents: ")
        print(70*"=")
        print(message_text)
        print(70*"=")
        return
    msg = Message()
    # show recipient name string if specified
    if recipient_name is not None:
        msg['To'] = recipient_name
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.set_payload(message_text)
    #if debug: print "sending e-mail message"
    server = smtplib.SMTP(smtp_server)   # TODO: password?
    #server.set_debuglevel(1)
    server.sendmail(sender_email, recipient_list, str(msg))
    #server.quit()
