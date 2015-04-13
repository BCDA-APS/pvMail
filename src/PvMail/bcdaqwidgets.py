#!/usr/bin/env python

'''
BcdaQWidgets: PyEpics-aware PyQt widgets for the APS

Copyright (c) 2009 - 2015, UChicago Argonne, LLC.
See LICENSE file for details.

The bcdaqwidgets [#]_ module provides a set of PyQt4
widgets that are EPICS-aware.  These include:

=============================  ================================================================
widget                         description
=============================  ================================================================
:class:`BcdaQLabel`            EPICS-aware QLabel widget
:class:`BcdaQLineEdit`         EPICS-aware QLineEdit widget
:class:`BcdaQPushButton`       EPICS-aware QPushButton widget
:class:`BcdaQMomentaryButton`  sends a value when pressed or released, label does not change
:class:`BcdaQToggleButton`     toggles boolean PV when pressed
:class:`BcdaQLabel_RBV`        makes motor RBV field background green when motor is moving
=============================  ================================================================

.. [#] BCDA: Beam line Controls and Data Acquisition group 
       of the Advanced Photon Source, Argonne National Laboratory,
       http://www.aps.anl.gov/bcda

.. note:: bcdaqwidgets must be imported AFTER importing either PyQt4
'''


import sys
from PyQt4 import QtCore, QtGui
pyqtSignal = QtCore.pyqtSignal
import epics


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

BACKGROUND_DEFAULT = '#efefef'
BACKGROUND_DONE_MOVING = BACKGROUND_DEFAULT
BACKGROUND_MOVING = 'lightgreen'
DMOV_COLOR_TABLE = {1: BACKGROUND_DONE_MOVING, 0: BACKGROUND_MOVING}

BLANKS = ' '*4


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
        if self.widget is not None:
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
    thread and the PyQt4 (main Qt4 GUI) thread.
    '''
    newFgColor = pyqtSignal()
    newBgColor = pyqtSignal()
    newText    = pyqtSignal(str)
    dmov       = pyqtSignal(int)


class BcdaQWidgetSuper(object):
    '''superclass for EPICS-aware widgets'''
    css = {}

    def __init__(self, pvname=None, useAlarmState=False):
        self.style_dict = {}
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
        self.updateStyleSheet(self.css)

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
            self.SetText(BLANKS)
            self.SetBackgroundColor()
            self.setToolTip(pvname + ' not connected')

    def onPVConnect(self, pvname='', **kw):
        '''respond to a PyEpics CA connection event'''
        conn = kw['conn']
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
        self.labelSignal.newText.emit(char_value)      # threadsafe update of the widget
        if self.ca_callback is not None:
            # caller wants to be notified of this camonitor event
            self.ca_callback(pvname=pvname, char_value=char_value, **kw)

    def SetText(self, text, *args, **kw):
        '''set the text of the widget (threadsafe update)'''
        self.setText(text)

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


class BcdaQLabel(QtGui.QLabel, BcdaQWidgetSuper):
    '''
    Provide the value of an EPICS PV on a PyQt4.QtGui.QLabel
    
    USAGE::
    
        import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQLabel()
        widget.ca_connect("example:m1.RBV")
        
    :param str pvname: epics process variable name for this widget
    :param bool useAlarmState: change the text color based on pv severity
    :param str bgColorPv: update widget's background color based on this pv's value
    
    '''
    css = {
           'background-color': 'bisque', 
           'border': '1px solid gray', 
           'font': 'bold', 
           }

    def __init__(self, pvname=None, useAlarmState=False, bgColorPv=None):
        ''':param str text: initial Label text (really, we can ignore this)'''
        QtGui.QLabel.__init__(self, BLANKS)
        BcdaQWidgetSuper.__init__(self, useAlarmState=useAlarmState)

        # define the signals we'll use in the camonitor handler to update the GUI
        self.labelSignal = BcdaQSignalDef()
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.updateStyleSheet(self.css)

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


class BcdaQLineEdit(QtGui.QLineEdit, BcdaQWidgetSuper):
    '''
    Provide the value of an EPICS PV on a PyQt4.QtGui.QLineEdit
    
    USAGE::
    
        import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQLineEdit()
        widget.ca_connect("example:m1.VAL")

    '''
    css = {
           'background-color': 'bisque', 
           'border': '3px inset gray', 
           }

    def __init__(self, pvname=None, useAlarmState=False):
        ''':param str text: initial Label text (really, we can ignore this)'''
        QtGui.QLineEdit.__init__(self, BLANKS)
        BcdaQWidgetSuper.__init__(self)

        # define the signals we'll use in the camonitor handler to update the GUI
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.clut = dict(CLUT)
        self.clut[AllowedStates.CONNECTED] = "bisque"
        self.updateStyleSheet(self.css)

        self.SetBackgroundColor()
        self.setAlignment(QtCore.Qt.AlignHCenter)
        self.returnPressed.connect(self.onReturnPressed)

        if pvname is not None and isinstance(pvname, str):
            self.ca_connect(pvname)

    def onReturnPressed(self):
        '''send the widget's text to the EPICS PV'''
        if self.pv is not None and len(self.text()) > 0:
            self.pv.put(self.text())

    def SetBackgroundColor(self, *args, **kw):
        '''set the background color of the QLineEdit() via its QPalette'''
        color = self.clut[self.state]
        self.updateStyleSheet({'background-color': color})


class BcdaQPushButton(QtGui.QPushButton, BcdaQWidgetSuper):
    '''
    Provide a QtGui.QPushButton connected to an EPICS PV
    
    It is necessary to also call the SetPressedValue() and/or
    SetReleasedValue() method to define the value to be sent 
    to the EPICS PV with the corresponding push button event.
    If left unconfigured, no action will be taken.
    
    USAGE::
    
        import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQPushButton()
        widget.ca_connect("example:bo0")
        widget.SetReleasedValue(1)
    
    '''
    css = {'font': 'bold',}

    def __init__(self, label='', pvname=None, pressed_value=None, released_value=None):
        ''':param str text: initial Label text (really, we can ignore this)'''
        QtGui.QPushButton.__init__(self, label)
        BcdaQWidgetSuper.__init__(self)

        self.labelSignal = BcdaQSignalDef()
        self.labelSignal.newBgColor.connect(self.SetBackgroundColor)
        self.labelSignal.newText.connect(self.SetText)

        self.clut = dict(CLUT)
        self.updateStyleSheet(self.css)

        self.pv = None
        self.ca_callback = None
        self.ca_connect_callback = None
        self.state = AllowedStates.DISCONNECTED
        self.setCheckable(True)
        self.SetBackgroundColor()
        self.clicked[bool].connect(self.onPressed)
        self.released.connect(self.onReleased)

        self.pressed_value = pressed_value
        self.released_value = released_value

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
    Send a value when released, label does not change if PV changes.
    
    It only acts on mouse pressed signal.
    
    This is a special case of a BcdaQPushButton where the text on the button
    does not respond to changes of the value of the attached EPICS PV.
    
    It is a good choice to use, for example, for a motor STOP button.
    
    USAGE::
    
        import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQMomentaryButton('Stop')
        widget.ca_connect("example:m1.STOP")
        widget.SetPressedValue(1)

    '''

    # disable these methods
    def SetText(self, *args, **kw): pass
    def onReleased(self, **kw): pass

    def onPressed(self, **kw):
        '''button was pressed, send preset value to EPICS'''
        if self.pv is not None and self.pressed_value is not None:
            self.pv.put(self.pressed_value)
            self.setCheckable(False)



class BcdaQToggleButton(BcdaQPushButton):
    '''
    Toggles boolean PV when pressed
    
    This is a special case of a BcdaQPushButton where the text on the button
    changes with the value of the attached EPICS PV.  In this case, the 
    displayed value is the name of the next state of the EPICS PV when 
    the button is pressed.
    
    It is a good choice to use, for example, for an ON/OFF button.
    
    USAGE::
    
        import bcdaqwidgets
        
        ...
    
        widget = bcdaqwidgets.BcdaQToggleButton()
        widget.ca_connect("example:room_light")
        widget.SetReleasedValue(1)

    '''

    def __init__(self, pvname=None):
        BcdaQPushButton.__init__(self, pvname=pvname)
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
        self.setText(self.value_names[self.pv.get()])


class BcdaQLabel_RBV(BcdaQLabel):
    '''
    makes motor readback field (BcdaQLabel) background green when motor is moving
    
    EXAMPLE::

        pvname = 'ioc:m1'
        w = bcdaqwidgets.RBV_BcdaQLabel()
        layout.addWidget(w)
        w.ca_connect(pvname+'.RBV')

    '''
    
    def __init__(self, *args, **kw):
        BcdaQLabel.__init__(self, *args, **kw)
        self.sty = StyleSheet(self)
        self.signal = BcdaQSignalDef()
        self.dmov = None
    
    def ca_connect(self, rbv_pv):
        #BcdaQLabel.ca_connect(rbv_pv)
        super(RBV_BcdaQLabel, self).ca_connect(rbv_pv)
        dmov_pv = rbv_pv.split('.')[0] + '.DMOV'
        self.dmov = epics.PV(dmov_pv, callback=self.dmov_callback)
        self.signal.dmov.connect(self.setBackgroundColor)
    
    def dmov_callback(self, *args, **kw):
        '''called in PyEpics thread'''
        self.signal.dmov.emit(kw['value'])
    
    def setBackgroundColor(self, value):
        '''called in GUI thread'''
        color = DMOV_COLOR_TABLE[value]
        self.sty.updateStyleSheet({'background-color': color})


RBV_BcdaQLabel = BcdaQLabel_RBV    # legacy name


########### SVN repository information ###################
# $Date: 2014-12-12 18:35:59 -0600 (Fri, 12 Dec 2014) $
# $Author: jemian $
# $Revision: 1611 $
# $URL: https://subversion.xray.aps.anl.gov/bcdaext/bcdaqwidgets/trunk/src/bcdaqwidgets/bcdaqwidgets.py $
# $Id: bcdaqwidgets.py 1611 2014-12-13 00:35:59Z jemian $
########### SVN repository information ###################
