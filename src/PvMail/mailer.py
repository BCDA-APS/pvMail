
'''
send a message by email to one or more recipients (by SMTP or sendmail)


========  ================================================================
agent     description
========  ================================================================
sendmail  (linux-only) uses either */usr/lib/sendmail* or */usr/bin/mail*
SMTP      uses smtplib [#]_
========  ================================================================

.. [#] *smtplib*: https://docs.python.org/2/library/smtplib.html
'''


import datetime
import os
import sys

# import PvMail


SMTP_TIMEOUT = 10


class MailerError(Exception): pass


def sendMail_sendmail(subject, message, recipients, logger = None):
    '''
    send an email message using sendmail (linux only)
    
    :param str subject: short text for email subject
    :param str message: full text of email body
    :param [str] recipients: list of email addresses to receive the message
    :param obj logger: optional message logging method
    :returns str: status message or None (if exception)
    '''
    
    if sys.platform not in ('linux2'):
        raise MailerError('Cannot use this method on sys.platform='+sys.platform)
    
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


def sendMail_SMTP(recipients, subject, message, smtp_cfg, sender = None):
    '''
    send email message through SMTP server
    
    :param [str] recipients: string list of email addresses which should receive message by email
    :param str subject: email message subject
    :param str message: email message content
    :param dict smtp_cfg: such as returned from :mod:`PvMail.ini_config.Config.get`
    
        :server:               required - (*str*) SMTP server
        :user:                 required - (*str*) username to login to SMTP server
        :port:                 optional - (*str*) SMTP port
        :password:             optional - (*str*) password for username
        :connection_security:  optional - (*str*) **STARTTLS** (the only choice, if specified)

    :param str sender: "From" address, if *None* use *smtp_cfg['user']* value
    
    EXAMPLE::
    
        >>> import PvMail.ini_config
        >>> smtp_cfg = PvMail.ini_config.Config().get()
        >>> recipients = ['joe@gmail.com', 'sally@example.org']
        >>> subject = 'SMTP test message'
        >>> message = '\\n'.join(['%s: %s' % (k, v) for k, v in os.environ.items()])
        >>> sendMail_SMTP(recipients, subject, message, smtp_cfg)
    
    '''
    import smtplib
    import email
    
    host = smtp_cfg.get('server', None)
    if host is None:
        raise MailerError('must define an SMTP host to be used')
    port = smtp_cfg.get('port', None)
    username = smtp_cfg.get('user', None)
    if username is None:
        raise MailerError('must define a username for the SMTP server')
    if sender is None:
        sender = username
    password = smtp_cfg.get('password', None)
    connection_security = smtp_cfg.get('connection_security', None)
    if connection_security not in (None, 'STARTTLS'):
        msg = 'connection_security must be: STARTTLS or not defined, found: '
        raise MailerError(msg + connection_security)
    
    msg = email.Message.Message()
    if isinstance(recipients, str):
        msg['To'] = recipients
    else:
        for who in recipients:
            msg['To'] = who
    msg['From'] = sender
    msg['Subject'] = subject
    msg.set_payload(message)

    smtpserver = smtplib.SMTP(timeout=SMTP_TIMEOUT)
    # smtpserver.set_debuglevel(1)
    if port is None:
        _r = smtpserver.connect(host)
    if port is not None:
        _r = smtpserver.connect(host, int(port))
    
    _r = smtpserver.ehlo()
    if smtp_cfg.get('connection_security', None) == 'STARTTLS':
        _r = smtpserver.starttls()
        _r = smtpserver.ehlo()
    
    if password is not None:
        _r = smtpserver.login(username, password)
    
    smtpserver.sendmail(username, recipients, str(msg))
    smtpserver.close()


if __name__ == '__main__':
    import ini_config
    smtp_cfg = ini_config.Config().get()
    recipients = ['prjemian@gmail.com', 'Pete@jemian.org']
    subject = sys.argv[0] + ' test message'
    message = '\n'.join(['%s: %s' % (k, v) for k, v in os.environ.items()])
    sendMail_SMTP(recipients, subject, message, smtp_cfg)
