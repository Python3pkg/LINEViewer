﻿import wx
import numpy as np
from os.path import dirname


class Specification(wx.Panel):

    """
    SOME TEXT
    """

    def __init__(self, ParentFrame, Data):

        # Create Specification Frame window
        wx.Panel.__init__(self, parent=ParentFrame, size=(210, 1000),
                          style=wx.SUNKEN_BORDER)

        # Specify relevant variables
        self.Data = Data
        self.Data.Specs = type('Specs', (object,), {})()

        # Panel: Specs Handler
        PanelSpecs = wx.Panel(self, wx.ID_ANY)
        sizerPanelSpecs = wx.BoxSizer(wx.VERTICAL)

        # Text: Data Filters Specifications
        TxtSpecData = wx.StaticText(PanelSpecs,
                                    wx.ID_ANY, style=wx.CENTRE,
                                    label=" Dataset Filters")
        TxtSpecData.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecData, 0, wx.EXPAND)

        # High- & Lowpass Filter
        self.Data.Specs.CheckboxPass = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                   'Use Pass Filters')
        self.Data.Specs.CheckboxPass.SetValue(True)
        sizerPanelSpecs.Add(self.Data.Specs.CheckboxPass, 0, wx.EXPAND)

        PanelPassTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerPassTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerPassTitle.AddSpacer(5)

        TextHighPass = wx.StaticText(PanelPassTitle, wx.ID_ANY,
                                     label="Highpass [Hz]")
        sizerPassTitle.Add(TextHighPass, 0, wx.EXPAND)
        sizerPassTitle.AddSpacer(5)
        TextLowPass = wx.StaticText(PanelPassTitle, wx.ID_ANY,
                                    label="Lowpass [Hz]")
        sizerPassTitle.Add(TextLowPass, 0, wx.EXPAND)
        PanelPassTitle.SetSizer(sizerPassTitle)
        sizerPanelSpecs.Add(PanelPassTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelPassField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerPassField = wx.BoxSizer(wx.HORIZONTAL)
        sizerPassField.AddSpacer(3)
        self.Data.Specs.HighPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                               size=(67, 25),
                                               style=wx.TE_PROCESS_ENTER,
                                               value=str(0.1))
        sizerPassField.Add(self.Data.Specs.HighPass, 0, wx.EXPAND)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(15)
        sizerPassField.AddSpacer(3)
        self.Data.Specs.LowPass = wx.TextCtrl(PanelPassField, wx.ID_ANY,
                                              size=(67, 25),
                                              style=wx.TE_PROCESS_ENTER,
                                              value=str(80.0))
        sizerPassField.Add(self.Data.Specs.LowPass, 0, wx.EXPAND)
        PanelPassField.SetSizer(sizerPassField)
        sizerPanelSpecs.Add(PanelPassField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Notch Filter
        PanelNotch = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNotch = wx.BoxSizer(wx.HORIZONTAL)
        self.Data.Specs.CheckboxNotch = wx.CheckBox(PanelNotch, wx.ID_ANY,
                                                    'Notch [Hz]')
        self.Data.Specs.CheckboxNotch.SetValue(True)
        self.Data.Specs.Notch = wx.TextCtrl(PanelNotch, wx.ID_ANY,
                                            size=(67, 25),
                                            style=wx.TE_PROCESS_ENTER,
                                            value=str(50.0))
        sizerNotch.Add(self.Data.Specs.CheckboxNotch, 0, wx.EXPAND)
        sizerNotch.AddSpacer(5)
        sizerNotch.Add(self.Data.Specs.Notch, 0, wx.EXPAND)
        PanelNotch.SetSizer(sizerNotch)
        sizerPanelSpecs.Add(PanelNotch, 0, wx.EXPAND)

        # Use DC Filter
        self.Data.Specs.CheckboxDC = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                 'Remove DC')
        self.Data.Specs.CheckboxDC.SetValue(True)
        sizerPanelSpecs.Add(self.Data.Specs.CheckboxDC, 0, wx.EXPAND)

        # Average Reference
        self.Data.Specs.CheckboxAverage = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                      'Average Reference')
        self.Data.Specs.CheckboxAverage.SetValue(True)
        sizerPanelSpecs.Add(self.Data.Specs.CheckboxAverage, 0, wx.EXPAND)

        # Specific Reference
        PanelNewRef = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerNewRef = wx.BoxSizer(wx.HORIZONTAL)
        sizerNewRef.AddSpacer(5)
        TextNewRef = wx.StaticText(PanelNewRef, wx.ID_ANY,
                                   label="Reference", style=wx.CENTRE)
        sizerNewRef.Add(TextNewRef, 0, wx.CENTER)
        sizerNewRef.AddSpacer(5)

        self.Data.Specs.DropDownNewRef = wx.ComboBox(PanelNewRef, wx.ID_ANY,
                                                     value='', choices=[],
                                                     style=wx.CB_READONLY,
                                                     size=(100, 25))
        sizerNewRef.Add(self.Data.Specs.DropDownNewRef, 0, wx.EXPAND)
        PanelNewRef.SetSizer(sizerNewRef)
        sizerPanelSpecs.Add(PanelNewRef, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(40)

        # Text: Data Interpolation Specifications
        TxtInterpolation = wx.StaticText(PanelSpecs,
                                         wx.ID_ANY, style=wx.CENTRE,
                                         label=" Channel Interpolation")
        TxtInterpolation.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtInterpolation, 0, wx.EXPAND)

        self.ButtonInterpolate = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Channels to interpolate")
        self.ButtonInterpolate.Enable()
        self.Data.Specs.channels2Interpolate = []
        sizerPanelSpecs.Add(self.ButtonInterpolate, 0, wx.EXPAND)
        self.Data.Specs.xyzFile = ''
        sizerPanelSpecs.AddSpacer(40)

        # Text: Epoch Filters Specifications
        TxtSpecEpoch = wx.StaticText(PanelSpecs,
                                     wx.ID_ANY, style=wx.CENTRE,
                                     label=" Epoch Filters")
        TxtSpecEpoch.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecEpoch, 0, wx.EXPAND)

        # Epoch Specification
        PanelEpochTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerEpochTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerEpochTitle.AddSpacer(5)

        TextHighEpoch = wx.StaticText(PanelEpochTitle, wx.ID_ANY,
                                      label="Pre [ms]")
        sizerEpochTitle.Add(TextHighEpoch, 0, wx.EXPAND)
        sizerEpochTitle.AddSpacer(15)
        sizerEpochTitle.AddSpacer(15)
        sizerEpochTitle.AddSpacer(12)
        TextLowEpoch = wx.StaticText(PanelEpochTitle, wx.ID_ANY,
                                     label="Post [ms]")
        sizerEpochTitle.Add(TextLowEpoch, 0, wx.EXPAND)
        PanelEpochTitle.SetSizer(sizerEpochTitle)
        sizerPanelSpecs.Add(PanelEpochTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelEpochField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerEpochField = wx.BoxSizer(wx.HORIZONTAL)
        sizerEpochField.AddSpacer(3)
        self.Data.Specs.PreEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                               size=(67, 25),
                                               style=wx.TE_PROCESS_ENTER,
                                               value=str(100.0))
        sizerEpochField.Add(self.Data.Specs.PreEpoch, 0, wx.EXPAND)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(15)
        sizerEpochField.AddSpacer(3)
        self.Data.Specs.PostEpoch = wx.TextCtrl(PanelEpochField, wx.ID_ANY,
                                                size=(67, 25),
                                                style=wx.TE_PROCESS_ENTER,
                                                value=str(500.0))
        sizerEpochField.Add(self.Data.Specs.PostEpoch, 0, wx.EXPAND)
        PanelEpochField.SetSizer(sizerEpochField)
        sizerPanelSpecs.Add(PanelEpochField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Baseline Correction
        self.Data.Specs.CheckboxBaseline = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                       'Baseline Correction')
        self.Data.Specs.CheckboxBaseline.SetValue(True)
        sizerPanelSpecs.Add(self.Data.Specs.CheckboxBaseline, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        # Threshold Specification
        self.Data.Specs.CheckboxThreshold = wx.CheckBox(PanelSpecs, wx.ID_ANY,
                                                        'Threshold Correction')
        self.Data.Specs.CheckboxThreshold.SetValue(True)
        sizerPanelSpecs.Add(self.Data.Specs.CheckboxThreshold, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        PanelThreshTitle = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerThreshTitle = wx.BoxSizer(wx.HORIZONTAL)
        sizerThreshTitle.AddSpacer(5)

        TextThreshValue = wx.StaticText(PanelThreshTitle, wx.ID_ANY,
                                        label="Thresh. [uV]")
        sizerThreshTitle.Add(TextThreshValue, 0, wx.EXPAND)
        sizerThreshTitle.AddSpacer(15)
        sizerThreshTitle.AddSpacer(2)
        TextThreshWindow = wx.StaticText(PanelThreshTitle, wx.ID_ANY,
                                         label="Window [ms]")
        sizerThreshTitle.Add(TextThreshWindow, 0, wx.EXPAND)
        PanelThreshTitle.SetSizer(sizerThreshTitle)
        sizerPanelSpecs.Add(PanelThreshTitle, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(2)

        PanelThreshField = wx.Panel(PanelSpecs, wx.ID_ANY)
        sizerThreshField = wx.BoxSizer(wx.HORIZONTAL)
        sizerThreshField.AddSpacer(3)
        self.Data.Specs.ThreshValue = wx.TextCtrl(PanelThreshField, wx.ID_ANY,
                                                  size=(67, 25),
                                                  style=wx.TE_PROCESS_ENTER,
                                                  value=str(80.0))
        sizerThreshField.Add(self.Data.Specs.ThreshValue, 0, wx.EXPAND)
        sizerThreshField.AddSpacer(15)
        sizerThreshField.AddSpacer(15)
        sizerThreshField.AddSpacer(3)
        self.Data.Specs.ThreshWindow = wx.TextCtrl(PanelThreshField, wx.ID_ANY,
                                                   size=(67, 25),
                                                   style=wx.TE_PROCESS_ENTER,
                                                   value=str(100.0))
        sizerThreshField.Add(self.Data.Specs.ThreshWindow, 0, wx.EXPAND)
        PanelThreshField.SetSizer(sizerThreshField)
        sizerPanelSpecs.Add(PanelThreshField, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(5)

        self.ButtonExclude = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="&Exclude Channels for Thr.")
        self.ButtonExclude.Enable()
        self.Data.Specs.channels2exclude = []
        sizerPanelSpecs.Add(self.ButtonExclude, 0, wx.EXPAND)
        sizerPanelSpecs.AddSpacer(40)

        # Text: Marker Specifications
        TxtSpecMarker = wx.StaticText(PanelSpecs,
                                      wx.ID_ANY, style=wx.CENTRE,
                                      label=" Marker Options")
        TxtSpecMarker.SetFont(wx.Font(11, wx.DEFAULT, wx.NORMAL, wx.BOLD))
        sizerPanelSpecs.Add(TxtSpecMarker, 0, wx.EXPAND)

        self.ButtonMarker = wx.Button(
            PanelSpecs, wx.ID_ANY, size=(200, 28), style=wx.CENTRE,
            label="Choose &markers to show")
        self.ButtonMarker.Enable()
        self.markers2use = []
        sizerPanelSpecs.Add(self.ButtonMarker, 0, wx.EXPAND)

        # Create vertical structure of Data Handler Frame
        sizerFrame = wx.BoxSizer(wx.VERTICAL)
        sizerFrame.AddSpacer(3)
        sizerFrame.Add(PanelSpecs, 0)
        self.SetSizer(sizerFrame)
        PanelSpecs.SetSizer(sizerPanelSpecs)

        # Specification of events
        wx.EVT_TEXT_ENTER(self.Data.Specs.HighPass,
                          self.Data.Specs.HighPass.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.LowPass, self.Data.Specs.LowPass.Id,
                          self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.Notch, self.Data.Specs.Notch.Id,
                          self.drawAll)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxAverage,
                        self.Data.Specs.CheckboxAverage.Id, self.useAverage)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxDC,
                        self.Data.Specs.CheckboxDC.Id, self.useDC)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxNotch,
                        self.Data.Specs.CheckboxNotch.Id, self.useNotch)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxPass,
                        self.Data.Specs.CheckboxPass.Id, self.usePass)
        wx.EVT_COMBOBOX(self.Data.Specs.DropDownNewRef,
                        self.Data.Specs.DropDownNewRef.Id, self.useNewRef)
        wx.EVT_BUTTON(self.ButtonInterpolate, self.ButtonInterpolate.Id,
                      self.interpolateChannels)

        wx.EVT_TEXT_ENTER(self.Data.Specs.PreEpoch,
                          self.Data.Specs.PreEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.PostEpoch,
                          self.Data.Specs.PostEpoch.Id, self.drawAll)
        wx.EVT_TEXT_ENTER(self.Data.Specs.ThreshValue,
                          self.Data.Specs.ThreshValue.Id, self.drawEpochs)
        wx.EVT_TEXT_ENTER(self.Data.Specs.ThreshWindow,
                          self.Data.Specs.ThreshWindow.Id, self.drawEpochs)
        wx.EVT_BUTTON(self.ButtonExclude, self.ButtonExclude.Id,
                      self.excludeChannel)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxThreshold,
                        self.Data.Specs.CheckboxThreshold.Id,
                        self.useThreshold)
        wx.EVT_CHECKBOX(self.Data.Specs.CheckboxBaseline,
                        self.Data.Specs.CheckboxBaseline.Id, self.drawEpochs)

        wx.EVT_BUTTON(self.ButtonMarker, self.ButtonMarker.Id,
                      self.selectMarkers)

    def drawAll(self, event):
        if self.Data.Datasets != []:
            self.Data.Results.updateAll(self.Data)
        event.Skip()

    def drawEpochs(self, event):
        if self.Data.Datasets != []:
            self.Data.Results.updateEpochs(self.Data)
        event.Skip()

    def useAverage(self, event):
        if self.Data.Specs.CheckboxAverage.GetValue():
            self.Data.Specs.DropDownNewRef.SetSelection(0)
            self.Data.Specs.DropDownNewRef.SetValue('')
        self.drawAll(event)

    def useNewRef(self, event):
        if self.Data.Specs.DropDownNewRef.GetSelection() == 0:
            self.useAverage(event)
            event.Skip()
        else:
            self.Data.Specs.CheckboxAverage.SetValue(False)
            self.drawAll(event)

    def useDC(self, event):
        self.drawAll(event)

    def interpolateChannels(self, event):
        if self.Data.Datasets != []:
            channels = self.Data.Datasets[0].labelsChannel
            dlgSelect = wx.MultiChoiceDialog(
                self, caption="Select channels to interpolate",
                message='Which channels should be interpolated?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.Data.Specs.channels2Interpolate]
            dlgSelect.SetSelections(selected)
            if dlgSelect.ShowModal() == wx.ID_OK:
                self.Data.Specs.channels2Interpolate = [
                    channels[x] for x in dlgSelect.GetSelections()]

                if self.Data.Specs.xyzFile == '':
                    self.xyzPath = self.Data.DirPath
                else:
                    self.xyzPath = dirname(self.Data.Specs.xyzFile)

                dlgXYZ = wx.FileDialog(None, "Load xyz file",
                                       defaultDir=self.xyzPath,
                                       wildcard='*.xyz')
                if dlgXYZ.ShowModal() == wx.ID_OK:
                    self.Data.Specs.xyzFile = dlgXYZ.GetPath()
                dlgXYZ.Destroy()

                self.Data.Results.interpolationCheck(self.Data)
            dlgSelect.Destroy()
        event.Skip()

    def useThreshold(self, event):
        if self.Data.Specs.CheckboxThreshold.GetValue():
            self.Data.Specs.ThreshValue.Enable()
            self.Data.Specs.ThreshWindow.Enable()
        else:
            self.Data.Specs.ThreshValue.Disable()
            self.Data.Specs.ThreshWindow.Disable()
        self.drawEpochs(event)

    def useNotch(self, event):
        if self.Data.Specs.CheckboxNotch.GetValue():
            self.Data.Specs.Notch.Enable()
        else:
            self.Data.Specs.Notch.Disable()
        self.drawAll(event)

    def usePass(self, event):
        if self.Data.Specs.CheckboxPass.GetValue():
            self.Data.Specs.HighPass.Enable()
            self.Data.Specs.LowPass.Enable()
        else:
            self.Data.Specs.HighPass.Disable()
            self.Data.Specs.LowPass.Disable()
        self.drawAll(event)

    def excludeChannel(self, event):
        if self.Data.Datasets != []:
            channels = self.Data.Datasets[0].labelsChannel
            dlg = wx.MultiChoiceDialog(
                self, caption="Select channels to exclude",
                message='Which channels should be ingored?',
                choices=channels)
            selected = [i for i, e in enumerate(channels)
                        if e in self.Data.Specs.channels2exclude]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.Data.Specs.channels2exclude = [
                    channels[x] for x in dlg.GetSelections()]
            dlg.Destroy()
            self.Data.Results.updateAll(self.Data)
        event.Skip()

    def selectMarkers(self, event):

        # TODO: This function doesnt do anything right now

        if self.Data.Datasets != []:
            markers = np.unique([m.markerValue
                                 for m in self.Data.Datasets])
            markerTxt = [str(m) for m in markers]
            dlg = wx.MultiChoiceDialog(
                self, caption="Select markers to show",
                message='Which markers should be visualized?',
                choices=markerTxt)
            if self.markers2use == []:
                selected = range(
                    np.unique([m.markerValue
                               for m in self.Data.Datasets]).shape[0])
            else:
                selected = [i for i, e in enumerate(markers)
                            if e in self.markers2use]
            dlg.SetSelections(selected)
            if dlg.ShowModal() == wx.ID_OK:
                self.markers2use = [markers[x]
                                    for x in dlg.GetSelections()]
            dlg.Destroy()

        event.Skip()


"""
PREPROCESSING (under development)
?? envelope filter (only if high and low pass)
?? if yes, than absolute or power: both have averagign window in ms
interpolation: how?
calculate also Global Map Dissimilarity (GMD)
check that GFP is calculated correct (GFP of average or average of GFPs?)
TODO: Create a figure that shows 1 electrode per marker and overlays mean and std for the epoch
"""
"""
ERP ANALYSIS (under development)
data normalization (according to GFP, yes or no)
"""
"""
OUTPUT (under development)
write eph, marker and tva files (also marker for origin)
write or load tvas
create and save figures
"""
"""
https://sites.google.com/site/cartoolcommunity/user-s-guide/analysis/artefacts-rejection-single-subjects-averages
"""