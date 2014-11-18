#!/usr/bin/env python

# from: https://subversion.xray.aps.anl.gov/bcdaext/bcdaqwidgets

'''
PySide-based EPICS-aware widgets for Python

Copyright (c) 2009 - 2014, UChicago Argonne, LLC.
See LICENSE file for details.

The bcdaqwidgets [#]_ module from BCDA [#]_
provides a set of PySide (also PyQt4) QtGui-based
widgets that are EPICS-aware.  These include:

=============================  ================================================================
widget                         description
=============================  ================================================================
:func:`BcdaQLabel`             EPICS-aware QtGui.QLabel widget
:func:`BcdaQLineEdit`          EPICS-aware QtGui.QLineEdit widget
:func:`BcdaQPushButton`        EPICS-aware QtGui.QPushButton widget
:func:`BcdaQMomentaryButton`   sends a value when pressed or released, label does not change
:func:`BcdaQToggleButton`      toggles boolean PV when pressed
=============================  ================================================================

.. [#] https://subversion.xray.aps.anl.gov/bcdaext/bcdaqwidgets
.. [#] BCDA: Beam line Controls and Data Acquisition group 
       of the Advanced Photon Source, Argonne National Laboratory,
       http://www.aps.anl.gov/bcda

'''


import epics
try:
    from PyQt4 import QtCore, QtGui
    pyqtSignal = QtCore.pyqtSignal
except:
    from PySide import QtCore, QtGui
    pyqtSignal = QtCore.Signal


def typesafe_enum(*sequential, **named):
    '''
    typesafe  enum
    
    EXAMPLE::

        >>> Numbers = typesafe_enum('ZERO', 'ONE', 'TWO', four='IV')
        >>> Numbers.ZERO
        0
        >>> Numbers.ONE
        1
        >>> Numbers.four
        IV
    
    :see: http://stackoverflow.com/questions/36932/whats-the-best-way-to-implement-an-typesafe_enum-in-python
    '''
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('TypesafeEnum', (), enums)

AllowedStates = typesafe_enum('DISCONNECTED', 'CONNECTED',)
CLUT = {   # clut: Color LookUp Table
    AllowedStates.DISCONNECTED: "#ffffff",      # white
    AllowedStates.CONNECTED:    "#e0e0e0",      # a bit darker than default #f0f0f0
    
}

SeverityColor = typesafe_enum('NO_ALARM', 'MINOR', 'MAJOR', 'CALC_INVALID')
SeverityColor.NO_ALARM =     "green"        # green
SeverityColor.MINOR =        "#ff0000"      # dark orange since yellow looks bad against gray
SeverityColor.MAJOR =        "red"          # red
SeverityColor.CALC_INVALID = "pink"         # pink


class StyleSheet(object):
    '''
    manage style sheet settings for a Qt widget
    
    Example::

        widget = QtGui.QLabel('example label')
        sty = bcdaqwidgets.StyleSheet(widget)
        sty.updateStyleSheet({
            'font': 'bold',
            'color': 'white',
            'background-color': 'dodgerblue',
            'qproperty-alignment': 'AlignCenter',
        })
    
    '''

    def __init__(self, widget, sty={}):
        '''
        :param obj widget: the Qt widget on which to apply the style sheet
        :param dict sty: starting dictionary of style sheet settings
        '''
        self.widget = widget
        widgetclass = str(type(widget)).strip('>').split('.')[-1].strip("'")
        self.widgetclass = widgetclass
        self.style_cache = dict(sty)

    def clearCache(self):
        '''clear the internal cache'''
        self.style_cache = {}

    def updateStyleSheet(self, sty={}):
        '''change specified styles and apply all to widget'''
        self._updateCache(sty)
        self.widget.setStyleSheet(str(self))

    def _updateCache(self, sty={}):
        '''update internal cache with specified styles'''
        for key, value in sty.items():
            self.style_cache[key] = value

    def __str__(self):
        '''returns a CSS text with the cache settings'''
        s = self.widgetclass + ' {\n'
        for key, value in sorted(self.style_cache.items()):
            s += '    %s: %s;\n' % (key, value)
        s += '}'
        return s


class BcdaQSignalDef(QtCore.QObject):
    '''
    Define the signals used to communicate between the PyEpics
    thread and the PySide (main Qt4 GUI) thread.
    '''
    # see: http://www.pyside.org/docs/pyside/PySide/QtCore/Signal.html
    # see: http://zetcode.com/gui/pysidetutorial/eventsandsignals/

    newFgColor = pyqtSignal()
    newBgColor = pyqtSignal()
    newText    = pyqtSignal()


class BcdaQWidget(object):
    '''superclass for EPICS-aware widgets'''

    def __init__(self, pvname=None, useAlarmState=False):
        self.style_dict = {}
        self.text_cache = ' ' * 4
        self.pv = None                           # PyEpics PV object
        self.ca_callback = None
        self.ca_connect_callback = None
        self.state = AllowedStates.DISCONNECTED
        self.labelSignal = BcdaQSignalDef()
        self.clut = dict(CLUT)

        self.useAlarmState = useAlarmState
        self.severity_color_list = [SeverityColor.NO_ALARM, SeverityColor.MINOR, SeverityColor.MAJOR, SeverityColor.CALC_INVALID]

        # for internal use persisting the various styleSheet settings
        self._style_sheet = StyleSheet(self)

    def ca_connect(self, pvname, ca_callback=None, ca_connect_callback=None):
        '''
        Connect this widget with the EPICS pvname
        
        :param str pvname: EPICS Process Variable name
        :param obj ca_callback: EPICS CA callback handler method
        :param obj ca_connect_callback: EPICS CA connection state callback handler method
        '''
        if self.pv is not None:
            self.ca_disconnect()
        if len(pvname) > 0:
            self.ca_callback = ca_callback
            self.ca_connect_callback = ca_connect_callback
            self.pv = epics.PV(pvname, 
                               callback=self.onPVChange,
                               connection_callback=self.onPVConnect)
            self.state = AllowedStates.CONNECTED
            self.setToolTip(pvname)

    def ca_disconnect(self):
        '''disconnect from this EPICS PV, if connected'''
        if self.pv is not None:
            self.pv.remove_callback()
            pvname = self.pv.pvname
            self.pv.disconnect()
            self.pv = None
            self.ca_callback = None
            self.ca_connect_callback = None
            self.state = AllowedStates.DISCONNECTED
            self.text_cache = ' ' * 4
            self.SetText()
            self.SetBackgroundColor()
            self.setToolTip(pvname + ' not connected')

    def onPVConnect(self, pvname='', **kw):
        '''respond to a PyEpics CA connection event'''
        conn = kw['conn']
        self.text_cache = {      # adjust the text
                          False: '',    #'disconnected',
                          True:  'connected',
                      }[conn]
        self.labelSignal.newText.emit()      # threadsafe update of the widget
        self.state = {      # adjust the state
                          False: AllowedStates.DISCONNECTED,
                          True:  AllowedStates.CONNECTED,
                      }[conn]
        self.labelSignal.newBgColor.emit()   # threadsafe update of the widget
        if self.ca_connect_callback is not None:
            # caller wants to be notified of this camonitor event
            self.ca_connect_callback(**kw)

    def onPVChange(self, pvname=None, char_value=None, **kw):
        '''respond to a PyEpics camonitor() event'''
        self.text_cache = char_value         # cache the new text locally
        self.labelSignal.newText.emit()      # threadsafe update of the widget
        if self.ca_callback is not None:
            # caller wants to be notified of this camonitor event
            self.ca_callback(pvname=pvname, char_value=char_value, **kw)

    def SetText(self, *args, **kw):
        '''set the text of the widget (threadsafe update)'''
        # pull the new text from the cache (set by onPVChange() method)
        self.setText(self.text_cache)

        # if desired, color the text based on the alarm severity
        if self.useAlarmState and self.pv is not None:
            self.pv.get_ctrlvars()
            if self.pv.severity is not None:
                if self.pv.severity < 0 or self.pv.severity >= len(self.severity_color_list):
                    print self.pv.severity
                    print self.severity_color_list
                    pass
                color = self.severity_color_list[self.pv.severity]
                self.updateStyleSheet({'color': color})

    def updateStyleSheet(self, changes_dict):
        '''update the widget's stylesheet'''
        self._style_sheet.updateStyleSheet(changes_dict)


class BcdaQLabel(QtGui.QLabel, BcdaQWidget):
    '''
    Provide the value of an EPICS PV on a PySide.QtGui.QLabel
    
    USAGE::
    
        from moxy.qtlib import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect("example:m1.RBV")
        
    :param str pvname: epics process variable name for this widget
    :param bool useAlarmState: change the text color based on pv severity
    :param str bgColorPv: update widget's background color based on this pv's value
    
    '''

    def __init__(self, pvname=None, useAlarmState=False, bgColorPv=None):
        ''':param str text: initial Label text (really, we can ignore this)'''
        BcdaQWidget.__init__(self, useAlarmState=useAlarmState)
        QtGui.QLabel.__init__(self, self.text_cache)

        # define the signals we'll use in the camonitor handler to update the GUI
        self.labelSignal = BcdaQSignalDef()
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.updateStyleSheet({
                               'background-color': 'bisque', 
                               'border': '1px solid gray', 
                               'font': 'bold', 
                               })

        self.clut = dict(CLUT)
        self.pv = None
        self.ca_callback = None
        self.ca_connect_callback = None
        self.state = AllowedStates.DISCONNECTED
        self.SetBackgroundColor()
        self.setAlignment(QtCore.Qt.AlignHCenter)

        if pvname is not None and isinstance(pvname, str):
            self.ca_connect(pvname)

        if bgColorPv is not None:
            self.bgColorObj = epics.PV(pvname=bgColorPv, callback=self.onBgColorObjChanged)

        self.bgColor_clut = {'not connected': 'white', '0': '#88ff88', '1': 'transparent'}
        self.bgColor = None

        self.bgColorSignal = BcdaQSignalDef()
        self.bgColorSignal.newBgColor.connect(self.SetBackgroundColorExtra)

    def onBgColorObjChanged(self, *args, **kw):
        '''epics pv callback when bgColor PV changes'''          
        if not self.bgColorObj.connected:     # white and displayed text is ' '
            self.bgColor = self.bgColor_clut['not connected']
        else:
            value = str(self.bgColorObj.get())
            if value in self.bgColor_clut:
                self.bgColor = self.bgColor_clut[value]
        # trigger the background color to change
        self.bgColorSignal.newBgColor.emit()

    def SetBackgroundColorExtra(self, *args, **kw):
        '''changes the background color of the widget'''
        if self.bgColor is not None:
            self.updateStyleSheet({'background-color': self.bgColor})
            self.bgColor = None

    def SetBackgroundColor(self, *args, **kw):
        '''set the background color of the widget via its stylesheet'''
        color = self.clut[self.state]
        self.updateStyleSheet({'background-color': color})


class BcdaQLineEdit(QtGui.QLineEdit, BcdaQWidget):
    '''
    Provide the value of an EPICS PV on a PySide.QtGui.QLineEdit
    
    USAGE::
    
        from moxy.qtlib import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQLineEdit()
        widget.ca_connect("example:m1.VAL")

    '''

    def __init__(self, pvname=None, useAlarmState=False):
        ''':param str text: initial Label text (really, we can ignore this)'''
        BcdaQWidget.__init__(self)
        QtGui.QLineEdit.__init__(self, self.text_cache)

        # define the signals we'll use in the camonitor handler to update the GUI
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.clut = dict(CLUT)
        self.clut[AllowedStates.CONNECTED] = "bisque"
        self.updateStyleSheet({
                               'background-color': 'bisque', 
                               'border': '3px inset gray', 
                               })

        self.SetBackgroundColor()
        self.setAlignment(QtCore.Qt.AlignHCenter)
        self.returnPressed.connect(self.onReturnPressed)

        if pvname is not None and isinstance(pvname, str):
            self.ca_connect(pvname)

    def onReturnPressed(self):
        '''send the widget's text to the EPICS PV'''
        if self.pv is not None and len(self.text()) > 0:
            self.pv.put(str(self.text()))

    def SetBackgroundColor(self, *args, **kw):
        '''set the background color of the QLineEdit() via its QPalette'''
        color = self.clut[self.state]
        self.updateStyleSheet({'background-color': color})


class BcdaQPushButton(QtGui.QPushButton, BcdaQWidget):
    '''
    Provide a QtGui.QPushButton connected to an EPICS PV
    
    It is necessary to also call the SetPressedValue() and/or
    SetReleasedValue() method to define the value to be sent 
    to the EPICS PV with the corresponding push button event.
    If left unconfigured, no action will be taken.
    
    USAGE::
    
        from moxy.qtlib import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQPushButton()
        widget.ca_connect("example:bo0")
        widget.SetReleasedValue(1)
    
    '''

    def __init__(self, label='', pvname=None):
        ''':param str text: initial Label text (really, we can ignore this)'''
        BcdaQWidget.__init__(self)
        QtGui.QPushButton.__init__(self, self.text_cache)
        self.setText(label)

        self.labelSignal = BcdaQSignalDef()
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.clut = dict(CLUT)
        self.updateStyleSheet({'font': 'bold',})

        self.pv = None
        self.ca_callback = None
        self.ca_connect_callback = None
        self.state = AllowedStates.DISCONNECTED
        self.setCheckable(True)
        self.SetBackgroundColor()
        self.clicked[bool].connect(self.onPressed)
        self.released.connect(self.onReleased)

        self.pressed_value = None
        self.released_value = None

        if pvname is not None and isinstance(pvname, str):
            self.ca_connect(pvname)

    def onPressed(self, **kw):
        '''button was pressed, send preset value to EPICS'''
        if self.pv is not None and self.pressed_value is not None:
            self.pv.put(self.pressed_value, wait=True)

    def onReleased(self, **kw):
        '''button was released, send preset value to EPICS'''
        if self.pv is not None and self.released_value is not None:
            self.pv.put(self.released_value, wait=True)

    def SetPressedValue(self, value):
        '''specify the value to be sent to the EPICS PV when the button is pressed'''
        self.pressed_value = value

    def SetReleasedValue(self, value):
        '''specify the value to be sent to the EPICS PV when the button is released'''
        self.released_value = value

    def SetBackgroundColor(self, *args, **kw):
        '''set the background color of the QPushButton() via its stylesheet'''
        color = self.clut[self.state]
        self.updateStyleSheet({'background-color': color})


class BcdaQMomentaryButton(BcdaQPushButton):
    '''
    Send a value when pressed or released, label does not change if PV changes.
    
    This is a special case of a BcdaQPushButton where the text on the button
    does not respond to changes of the value of the attached EPICS PV.
    
    It is a good choice to use, for example, for a motor STOP button.
    
    USAGE::
    
        from moxy.qtlib import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQMomentaryButton('Stop')
        widget.ca_connect("example:m1.STOP")
        widget.SetReleasedValue(1)

    '''

    def SetText(self, *args, **kw):
        '''do not change the label from the EPICS PV'''
        pass


class BcdaQToggleButton(BcdaQPushButton):
    '''
    Toggles boolean PV when pressed
    
    This is a special case of a BcdaQPushButton where the text on the button
    changes with the value of the attached EPICS PV.  In this case, the 
    displayed value is the name of the next state of the EPICS PV when 
    the button is pressed.
    
    It is a good choice to use, for example, for an ON/OFF button.
    
    USAGE::
    
        from moxy.qtlib import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQToggleButton()
        widget.ca_connect("example:room_light")
        widget.SetReleasedValue(1)

    '''

    def __init__(self, pvname=None):
        BcdaQPushButton.__init__(self)
        self.value_names = {1: 'change to 0', 0: 'change to 1'}
        self.setToolTip('tell EPICS PV to do this')

        if pvname is not None and isinstance(pvname, str):
            self.ca_connect(pvname)

    def ca_connect(self, pvname, ca_callback=None, ca_connect_callback=None):
        BcdaQPushButton.ca_connect(self, pvname, ca_callback=None, ca_connect_callback=None)
        labels = self.pv.enum_strs
        if labels is not None and len(labels)>1:
            # describe what happens when the button is pressed
            self.value_names[0] = labels[1]
            self.value_names[1] = labels[0]

    def onPressed(self):
        '''button was pressed, toggle the EPICS value as a boolean'''
        if self.pv is not None:
            self.pv.put(not self.pv.get(), wait=True)

    # disable these methods
    def onReleased(self, **kw): pass
    def SetPressedValue(self, value): pass
    def SetReleasedValue(self, value): pass

    def SetText(self, *args, **kw):
        '''set the text of the widget (threadsafe update) from the EPICS PV'''
        # pull the new text from the cache (set by onPVChange() method)
        self.setText(self.value_names[self.pv.get()])


#------------------------------------------------------------------


class DemoView(QtGui.QWidget):
    '''
    Show the BcdaQWidgets using an EPICS PV connection.

    Allow it to connect and ca_disconnect.
    This is a variation of EPICS PV Probe.
    '''

    def __init__(self, parent=None, pvname=None, bgColorPv=None):
        QtGui.QWidget.__init__(self, parent)

        layout = QtGui.QGridLayout()
        layout.addWidget(QtGui.QLabel('BcdaQLabel'), 0, 0)
        self.value = BcdaQLabel()
        layout.addWidget(self.value, 0, 1)
        self.setLayout(layout)

        self.sig = BcdaQSignalDef()
        self.sig.newBgColor.connect(self.SetBackgroundColor)
        self.toggle = False

        self.setWindowTitle("Demo bcdaqwidgets module")
        if pvname is not None:
            self.ca_connect(pvname)

            layout.addWidget(QtGui.QLabel('BcdaQLabel with alarm colors'), 1, 0)
            layout.addWidget(BcdaQLabel(pvname=pvname, useAlarmState=True), 1, 1)

            pvnameBg = pvname.split('.')[0] + '.DMOV'
            lblWidget = BcdaQLabel(pvname=pvname, bgColorPv=pvnameBg)
            layout.addWidget(QtGui.QLabel('BcdaQLabel with BG color change due to moving motor'), 2, 0)
            layout.addWidget(lblWidget, 2, 1)

            layout.addWidget(QtGui.QLabel('BcdaQLineEdit'), 3, 0)
            layout.addWidget(BcdaQLineEdit(pvname=pvname), 3, 1)

            pvname = pvname.split('.')[0] + '.PROC'
            widget = BcdaQMomentaryButton(label=pvname, pvname=pvname)
            layout.addWidget(QtGui.QLabel('BcdaQMomentaryButton'), 4, 0)
            layout.addWidget(widget, 4, 1)

    def ca_connect(self, pvname):
        self.value.ca_connect(pvname, ca_callback=self.callback)

    def callback(self, *args, **kw):
        self.sig.newBgColor.emit()   # threadsafe update of the widget

    def SetBackgroundColor(self, *args, **kw):
        '''toggle the background color of self.value via its stylesheet'''
        self.toggle = not self.toggle
        color = {False: "#ccc333", True: "#cccccc",}[self.toggle]
        self.value.updateStyleSheet({'background-color': color})


#------------------------------------------------------------------


def main():
    '''command-line interface to test this GUI widget'''
    import argparse
    import sys
    parser = argparse.ArgumentParser(description='Test the bcdaqwidgets module')

    # positional arguments
    # not required if GUI option is selected
    parser.add_argument('test_PV', 
                        action='store', 
                        nargs='?',
                        help="EPICS PV name", 
                        default="prj:m1.RBV", 
                        )
    results = parser.parse_args()

    app = QtGui.QApplication(sys.argv)
    view = DemoView(pvname=results.test_PV)
    view.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
