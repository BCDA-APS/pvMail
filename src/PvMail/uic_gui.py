"""
===================================
pvMail: just the GUI
===================================

Run the Graphical User Interface for PvMail using
PyQt from a .ui file with the uic subpackage.
"""

# Copyright (c) 2009-2024, UChicago Argonne, LLC.  See LICENSE file.

import datetime
import os
import pathlib
import sys

from pydm.widgets.label import PyDMLabel
from pydm.widgets.line_edit import PyDMLineEdit
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import uic

from . import AUTHORS
from . import COPYRIGHT
from . import DESCRIPTION
from . import DOCS_URL
from . import __version__ as VERSION
from . import cli
from . import ini_config
from . import utils
from .email_model import EmailListModel

pyqtSignal = QtCore.pyqtSignal

WINDOW_TITLE = "pvMail"
COLOR_ON = "lightgreen"
COLOR_OFF = "lightred"
COLOR_DEFAULT = "#eee"
LOG_REDISPLAY_DELAY_MS = 1000
PATH_RESOURCES = pathlib.Path(__file__).parent / "resources"
PATH_GUI_UI = utils.get_pkg_file_path(PATH_RESOURCES / "gui.ui")
PATH_ABOUT_UI = utils.get_pkg_file_path(PATH_RESOURCES / "about.ui")

PYDM_TOOLTIP_TEXT = "\n".join(
    [
        "$(pv_value.address)",
        "$(pv_value.TIME)",
        "connected=$(pv_value.connection)",
    ]
)


class PvMailSignalDef(QtCore.QObject):
    """Define the signals used to communicate between the threads."""

    EPICS_monitor = pyqtSignal(object)


class PvMail_GUI(object):
    """GUI used for pvMail, based on Qt (PyQt5 & PyDM)."""

    def __init__(
        self, ui_file=None, logger=None, logfile=None, config=None, *args, **kw
    ):
        """make this class callable from pvMail application"""
        self.ui = uic.loadUi(utils.get_pkg_file_path(ui_file or PATH_GUI_UI))

        self.ui.history.clear()
        self.logger = logger
        self.logfile = logfile
        self.config = config or ini_config.Config()

        self.setStatus("starting")

        self.email_address_model = EmailListModel([], self.ui)
        self.pvmail = None
        self.watching = False

        # menu item handlers
        self.ui.actionSend_test_email.triggered.connect(self.doSendTestMessage)
        self.ui.actionE_xit.triggered.connect(self.doClose)
        self.ui.actionAbout_pvMail.triggered.connect(self.doAbout)

        # button handlers
        self.ui.w_btn_run.clicked.connect(self.doRun)
        self.ui.w_btn_stop.clicked.connect(self.doStop)

        # the list of email recipients
        self.ui.emails.setModel(self.email_address_model)

        # adjust dynamic labels
        self.ui.config_file_name.setText(config.ini_file)
        self.ui.log_file_name.setText(str(logfile))
        self.ui.w_running_stopped.setText("stopped")

        self.ui.l_pv_trigger = QtWidgets.QLabel("trigger")
        self.ui.pv_trigger = PyDMLabel()
        self.ui.pv_trigger.setToolTip(PYDM_TOOLTIP_TEXT)

        self.ui.messagePV.returnPressed.connect(self.setMessageChannel)
        self.ui.triggerPV.returnPressed.connect(self.setTriggerChannel)

        self.ui.formLayout.addRow(self.ui.l_pv_trigger, self.ui.pv_trigger)
        self.triggerSignal = PvMailSignalDef()
        self.triggerSignal.EPICS_monitor.connect(self.onTrigger_gui_thread)

        self.ui.l_pv_message = QtWidgets.QLabel("message")
        self.ui.pv_message = PyDMLineEdit()
        self.ui.pv_message.setToolTip(PYDM_TOOLTIP_TEXT)
        self.ui.pv_message.setReadOnly(True)
        self.ui.formLayout.addRow(self.ui.l_pv_message, self.ui.pv_message)
        self.messageSignal = PvMailSignalDef()
        self.messageSignal.EPICS_monitor.connect(self.onMessage_gui_thread)

        self.setStatus("ready")

    def show(self):
        self.ui.show()

    def doAbout(self, *args, **kw):
        # TODO:  add a check for a new version #5
        # based on a comparison with the PyPI version:
        # https://pypi.python.org/pypi/PvMail
        #
        # Comparing with the VERSION file will show the development trunk
        # which is not always the production release version.
        # https://raw.githubusercontent.com/prjemian/pvMail/master/src/PvMail/VERSION
        #
        about = uic.loadUi(utils.get_pkg_file_path(PATH_ABOUT_UI))
        about.title.setText(f"PvMail  {VERSION}")
        about.description.setText(DESCRIPTION)
        about.authors.setText(", ".join(AUTHORS))
        about.copyright.setText(COPYRIGHT)

        pb = QtWidgets.QPushButton(DOCS_URL, clicked=self.doUrl)
        about.verticalLayout_main.addWidget(pb)

        # TODO: provide control to show the license

        # feed the status message
        msg = f"About: PvMail, v{VERSION}, PID={os.getpid()}"
        self.setStatus(msg)
        about.show()
        about.exec_()

    def doUrl(self):
        self.setStatus("opening documentation URL in default browser")
        service = QtGui.QDesktopServices()
        url = QtCore.QUrl(DOCS_URL)
        service.openUrl(url)

    def doClose(self, *args, **kw):
        self.setStatus("application exit requested")
        self.ui.close()

    def doRun(self, *args, **kw):
        self.setStatus("<Run> button pressed")
        if self.watching:
            self.setStatus("already watching")
        else:
            self.pvmail = cli.PvMail(self.config)

            # acquire information, validate it first
            msg_pv = str(self.getMessagePV())
            if len(msg_pv) == 0:
                self.setStatus("must give a message PV name")
                return
            trig_pv = str(self.getTriggerPV())
            if len(trig_pv) == 0:
                self.setStatus("must give a trigger PV name")
                return
            if len(self.email_list) == 0:
                self.setStatus("need at least one email address for list of recipients")
                return

            # report connection failure and abort
            for key, pv in dict(message=msg_pv, trigger=trig_pv).items():
                tc = self.pvmail.testConnect(pv, timeout=cli.CONNECTION_TEST_TIMEOUT)
                if tc is False:
                    msg = "could not connect to %s PV: %s" % (key, pv)
                    self.setStatus(msg)
                    self.pvmail = None
                    return

            self.pvmail.triggerPV = trig_pv
            self.pvmail.messagePV = msg_pv

            for obj in (self.ui.messagePV, self.ui.triggerPV):
                obj.setReadOnly(True)
                obj.setStyleSheet(f"background-color: {COLOR_DEFAULT}")
            self.ui.w_running_stopped.setStyleSheet(f"background-color: {COLOR_ON}")
            self.ui.pv_message.setReadOnly(True)

            self.pvmail.recipients = self.email_list
            self.setStatus("trigger PV: " + self.pvmail.triggerPV)
            self.setStatus("message PV: " + self.pvmail.messagePV)
            self.setStatus("recipients: " + "  ".join(self.email_list))
            try:
                self.pvmail.do_start()
            except Exception as reason:
                self.setStatus(str(reason))
                return
            self.ui.w_running_stopped.setText("running")
            self.ui.w_running_stopped.setStyleSheet(
                (f"background-color: {COLOR_ON}" "; qproperty-alignment: AlignCenter")
            )
            self.watching = True
            self.setStatus("Watching for email triggers.")

    def doStop(self, *args, **kw):
        if not self.watching:
            self.setStatus("not watching now")
        else:
            self.setStatus("<Stop> button pressed")
            self.pvmail.do_stop()
            self.ui.w_running_stopped.setText("stopped")
            for obj in (self.ui.messagePV, self.ui.triggerPV):
                obj.setStyleSheet("background-color: white")
                obj.setReadOnly(False)
            self.ui.w_running_stopped.setStyleSheet(
                f"background-color: {COLOR_DEFAULT}"
            )
            self.ui.pv_message.setReadOnly(False)

            self.setStatus("Not watching, no emails will be sent.")
            self.pvmail = None
            self.watching = False

    def doSendTestMessage(self):
        from . import mailer

        self.setStatus("requested a test email")
        subject = "PvMail mailer test message: " + self.config.mail_transfer_agent
        message = f"This is a test of the PvMail mailer, v{VERSION}"
        msg_pv = str(self.getMessagePV())
        if self.watching:
            message += "\n\n" + self.pvmail.message
        message += "\n\n triggerPV = " + str(self.getTriggerPV())
        message += "\n messagePV = " + msg_pv
        message += f"\n\n For more help, see: {DOCS_URL}"
        mailer.send_message(subject, message, self.email_list, self.config)
        self.setStatus("sent a test email")

    def appendEmailList(self, email_addr):
        self.email_address_model.listdata.append(email_addr)
        self.setStatus("added email: " + email_addr)

    @property
    def email_list(self):
        """the list of email addresses with empty items removed"""
        recipients = [v for v in self.email_address_model.listdata if len(v) > 0]
        return recipients

    @email_list.setter
    def email_list(self, recipients):
        self.email_address_model.reset()
        # remove blanks from the list, append blank at end for user to append
        recipients = (" ".join(recipients)).strip().split() + [""]
        for v in recipients:
            self.appendEmailList(v)

    def getMessagePV(self):
        return self.ui.messagePV.text()

    def onMessage_pv_thread(self, value=None, *args, **kw):
        self.messageSignal.EPICS_monitor.emit(value)  # threadsafe update of the widget

    def onMessage_gui_thread(self, value):
        self.setStatus("message: %s" % str(value))
        if self.ui.pv_message.text() != value:
            self.ui.pv_message.text_cache = value
            self.ui.pv_message.SetText()

    def setMessagePV(self, messagePV):
        self.ui.messagePV.setText(str(messagePV))
        self.setMessageChannel()
        self.setStatus("set message PV: " + messagePV)

    def setMessageChannel(self):
        self.setWidgetChannel(self.ui.pv_message, self.getMessagePV())

    def getTriggerPV(self):
        return self.ui.triggerPV.text()

    def onTrigger_pv_thread(self, value=None, char_value=None, *args, **kw):
        self.triggerSignal.EPICS_monitor.emit(value)  # threadsafe update of the widget

    def onTrigger_gui_thread(self, value):
        self.setStatus("trigger: %s" % str(value))
        color = {0: COLOR_DEFAULT, 1: COLOR_ON}[value]
        self.ui.pv_trigger.SetBackgroundColor(color)
        if self.ui.pv_trigger.text() != str(value):
            self.ui.pv_trigger.text_cache = str(value)
            self.ui.pv_trigger.SetText()
        if value == 1:
            # delayed update, wait for sending the email to be logged
            QtCore.QTimer.singleShot(LOG_REDISPLAY_DELAY_MS, self.logfile_to_history)

    def setTriggerPV(self, triggerPV):
        self.ui.triggerPV.setText(str(triggerPV))
        self.setTriggerChannel()
        self.setStatus("set trigger PV: " + triggerPV)

    def setWidgetChannel(self, widget, pv):
        pv = pv.strip()
        if len(pv) == 0:
            pv = "-none-"
        widget.set_channel(f"ca://{pv}")
        widget.check_enable_state()

    def setTriggerChannel(self):
        self.setWidgetChannel(self.ui.pv_trigger, self.getTriggerPV())

    def setStatus(self, message):
        ts = str(datetime.datetime.now())
        self.ui.statusbar.showMessage(str(message))
        if hasattr(self.ui, "history"):
            if self.logger is None or self.logfile is None:
                self.ui.history.append(ts + "  " + message)
            else:
                self.logger(message)
                # update with log file contents
                self.logfile_to_history()
            self.ui.history.ensureCursorVisible()

    def logfile_to_history(self):
        # update history with logfile contents
        self.ui.history.clear()
        self.ui.history.append(open(self.logfile, "r").read())


def main(triggerPV, messagePV, recipients, logger=None, logfile=None, config=None):
    app = QtWidgets.QApplication(sys.argv)
    config = config or ini_config.Config()
    gui = PvMail_GUI(logger=logger, logfile=logfile, config=config)

    gui.setStatus("PID: " + str(os.getpid()))
    if logfile is not None:
        logfile = pathlib.Path(logfile)
    if logfile is not None and logfile.exists():
        gui.ui.history.append(open(logfile, "r").read())
        gui.setStatus(f"log file: {logfile}")
    gui.setStatus("email configuration file: " + config.ini_file)
    gui.setStatus("email agent: " + config.mail_transfer_agent)
    gui.setMessagePV(messagePV)
    gui.setTriggerPV(triggerPV)
    gui.email_list = recipients

    gui.show()
    sys.exit(app.exec_())
