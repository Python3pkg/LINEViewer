import wx
import numpy as np
from os import remove
from os.path import splitext, exists
from FileHandler import ReadXYZ
from scipy.signal import butter, filtfilt


class Results():

    def __init__(self):
        """EMPTY INITIATION"""

    def updateAll(self, Data):

        # Get Specifications
        self.sampleRate = Data.Datasets[0].sampleRate
        self.removeDC = Data.Specs.CheckboxDC.GetValue()
        self.average = Data.Specs.CheckboxAverage.GetValue()
        self.newReference = Data.Specs.DropDownNewRef.GetValue()
        try:
            self.preEpoch = float(Data.Specs.PreEpoch.GetValue())
        except ValueError:
            self.preEpoch = 100.0
            Data.Specs.PreEpoch.SetValue(str(self.preEpoch))
        try:
            self.postEpoch = float(Data.Specs.PostEpoch.GetValue())
        except ValueError:
            self.postEpoch = 500.0
            Data.Specs.PostEpoch.SetValue(str(self.postEpoch))
        self.doPass = Data.Specs.CheckboxPass.GetValue()
        try:
            self.lowcut = float(Data.Specs.LowPass.GetValue())

            # Checks that Lowpass value is below nyquist frequency
            nyquistFreq = self.sampleRate * 0.5
            if self.lowcut > nyquistFreq:
                self.lowcut = nyquistFreq - 0.001
                Data.Specs.LowPass.SetValue(str(self.lowcut))
                dlg = wx.MessageDialog(
                    Data.Overview, "Low pass value was above the nyquist " +
                    "frequency (%s Hz). The value was set to %s Hz." % (
                        nyquistFreq, self.lowcut),
                    "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except ValueError:
            self.lowcut = 0
            Data.Specs.LowPass.SetValue(str(self.lowcut))
        try:
            self.highcut = float(Data.Specs.HighPass.GetValue())

            # Checks that Highpass value is above sampling frequency
            minFreq = 1. / int(np.round(
                (self.preEpoch + self.postEpoch) * self.sampleRate * 0.001))
            if self.highcut <= minFreq:
                self.highcut = minFreq
                Data.Specs.HighPass.SetValue(str(self.highcut))
                dlg = wx.MessageDialog(
                    Data.Overview, "High pass value was below minimum " +
                    "Frequency and was adjusted to %.4f Hz." % minFreq,
                    "Info", wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
        except ValueError:
            self.highcut = 0
            Data.Specs.HighPass.SetValue(str(self.highcut))
        self.doNotch = Data.Specs.CheckboxNotch.GetValue()
        try:
            self.notchValue = float(Data.Specs.Notch.GetValue())
        except ValueError:
            self.notchValue = 50.0
            Data.Specs.Notch.SetValue(str(self.notch))

        # Data object to save original epoch information
        Data.Orig = type('Orig', (object,), {})()

        # Filter Channel Signal
        for i, d in enumerate(Data.Datasets):

            tmpFilename = splitext(d.filename)[0]+'.lineviewerTemp'
            tmpDataset = np.memmap(tmpFilename, mode='w+', dtype='float32', shape=d.rawdata.shape)
            tmpDataset[:] = d.rawdata[:]

            # 1. Remove DC
            if self.removeDC:
                dcOffset = np.vstack(tmpDataset.mean(axis=1))
                for t in range(tmpDataset.shape[0]):
                    tmpDataset[t] -= dcOffset[t]

            # 2. Average or specific reference
            if self.average or self.newReference != 'None':

                print "Hallo"

                if self.average:
                    refOffset = tmpDataset.mean(axis=0)
                elif self.newReference != 'None':
                    electrodeID = np.where(d.labelsChannel == self.newReference)[0]
                    if self.newReference != 'Average':
                        refOffset = tmpDataset[electrodeID]
                for t in range(tmpDataset.shape[0]):
                    tmpDataset[t] -= refOffset[t]

            # 3. Run Butterworth Low-, High- or Bandpassfilter
            if self.doPass and self.lowcut != 0 and self.highcut != 0:
                b, a = butter_bandpass_param(d.sampleRate,
                                             highcut=self.highcut,
                                             lowcut=self.lowcut)
                for t in range(tmpDataset.shape[0]):
                    tmpDataset[t] = filtfilt(b, a, tmpDataset[t])

            # 4. Notch Filter
            if self.doNotch:
                b, a = butter_bandpass_param(d.sampleRate,
                                             notch=self.notchValue)
                for t in range(tmpDataset.shape[0]):
                    tmpDataset[t] = filtfilt(b, a, tmpDataset[t])

            # Create epochs
            self.preFrame = int(
                np.round(self.preEpoch * self.sampleRate * 0.001))
            self.preCut = np.copy(self.preFrame)
            self.postFrame = int(
                np.round(self.postEpoch * self.sampleRate * 0.001))
            self.postCut = np.copy(self.postFrame)

            # Drop markers if there's not enough preFrame or postFrame to cut
            cutsIO = [True if m > self.preCut and m < tmpDataset.shape[
                1] - self.postCut else False for m in d.markerTime]

            epochs = np.array([tmpDataset[:, m - self.preCut:m + self.postCut]
                               for m in d.markerTime[np.where(cutsIO)]])

            # Accumulate epoch information
            if i == 0:
                Data.Orig.epochs = epochs
                Data.Orig.markers = d.markerValue[np.where(cutsIO)]
                Data.Orig.labelsChannel = d.labelsChannel
            else:
                Data.Orig.epochs = np.vstack((Data.Orig.epochs, epochs))
                Data.Orig.markers = np.hstack(
                    (Data.Orig.markers, d.markerValue[np.where(cutsIO)]))

            # Clean up of temporary files and variables
            del tmpDataset
            if exists(tmpFilename):
                remove(tmpFilename)

            Data.interpolEpochs = np.copy(Data.Orig.epochs)

        self.interpolationCheck(Data, False)

    def interpolationCheck(self, Data, forceInterpolation):

        # Reset matrixSelected if updateAll or interpolationCheck is called
        if hasattr(self, 'matrixSelected'):
            del self.matrixSelected

        # Do interpolation if needed
        if Data.Specs.channels2interpolate != [] or forceInterpolation:
            Data.interpolEpochs = np.copy(Data.Orig.epochs)
            Data = interpolateChannels(self, Data, Data.Specs.xyzFile)

        self.updateEpochs(Data)

    def updateEpochs(self, Data):

        # Get Specifications
        self.baselineCorr = Data.Specs.CheckboxBaseline.GetValue()
        self.bridgeCorr = Data.Specs.CheckboxBridge.GetValue()
        self.blinkCorr = Data.Specs.CheckboxBlink.GetValue()
        self.thresholdCorr = Data.Specs.CheckboxThreshold.GetValue()
        try:
            self.threshold = float(Data.Specs.ThreshValue.GetValue())
        except ValueError:
            self.threshold = 80.0
            Data.Specs.ThreshValue.SetValue(str(self.threshold))
        self.excludeChannel = Data.Specs.channels2exclude

        # Copy epoch and marker values
        epochs = np.copy(Data.interpolEpochs)
        markers = np.copy(Data.Orig.markers)

        # Baseline Correction
        if self.baselineCorr:
            for e in epochs:
                baselineAvg = [
                    [c] for c in np.mean(e[:, self.preCut -
                                           self.preFrame:self.preCut],
                                         axis=1)]
                e -= baselineAvg

        # Correct Epochs for Threshold, Bridge and Blink outliers
        if self.thresholdCorr or self.bridgeCorr or self.blinkCorr:

            # Create Progressbar for outlier detection
            progressMax = epochs.shape[0]
            dlg = wx.ProgressDialog(
                "Outlier detection progress",
                "Time remaining for Outlier Detection", progressMax,
                style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)

            # Common parameters
            emptyMatrix = np.zeros(
                (epochs.shape[0], epochs.shape[1])).astype('bool')
            self.matrixThreshold = np.copy(emptyMatrix)
            self.matrixBridge = np.copy(emptyMatrix)
            self.matrixBlink = np.zeros(
                (epochs.shape[0], epochs.shape[2])).astype('bool')

            # Go through all the epochs
            for i, e_long in enumerate(epochs):

                e_short = epochs[i][:,
                                    self.preCut - self.preFrame:self.preCut +
                                    self.postFrame]

                # Check for Threshold outliers
                badThresholdChannelID = []
                if self.thresholdCorr:
                    badChannels = np.where(
                        ((e_short > self.threshold) |
                         (e_short < -self.threshold)).mean(axis=1))[0]
                    self.matrixThreshold[i][badChannels] = True

                # Check for Bridge outliers
                if self.bridgeCorr:
                    corrMatrix = np.where(np.corrcoef(e_short) > .999)
                    badBridgeChannelID = np.unique(
                        [corrMatrix[0][m] for m in range(len(corrMatrix[0]))
                         if corrMatrix[0][m] != corrMatrix[1][m]])
                    if badBridgeChannelID.size != 0:
                        self.matrixBridge[i][
                            np.unique(badBridgeChannelID)] = True

                # Check for Blink outliers
                if self.blinkCorr:
                    channels2Check = [j for j in range(e_long.shape[0])
                                      if j not in badThresholdChannelID]
                    stdOverTime = e_long[channels2Check].std(axis=0)
                    blinkTimes = stdOverTime > stdOverTime.mean() * 3
                    blinks = np.where(blinkTimes)[0]
                    blinkGroups = np.split(
                        blinks, np.where(np.diff(blinks) != 1)[0] + 1)
                    blinkPhase = [b for b in blinkGroups if b.shape[0] > 10]
                    blinkTimes *= False
                    if blinkPhase != []:
                        blinkTimes[np.hstack(blinkPhase)] = True
                    if blinkTimes.sum() != 0:
                        self.matrixBlink[i][blinkTimes] = True

                dlg.Update(i)
            dlg.Destroy()

            # Exclude Channels from thresholding
            if self.excludeChannel != []:
                excludeID = [i for i, e in enumerate(Data.Orig.labelsChannel)
                             if e in self.excludeChannel]
                self.matrixThreshold[:, excludeID] *= False

            # Specifying ID of good and bad epochs
            self.badBlinkEpochs = self.matrixBlink[
                :, self.preCut - self.preFrame:self.preCut +
                self.postFrame].sum(axis=1).astype('bool')
            badIDs = self.matrixThreshold.sum(
                axis=1) + self.matrixBridge.sum(axis=1) + self.badBlinkEpochs
            self.badID = badIDs.astype('bool')
            self.okID = np.invert(self.badID)

        # Connect all epochs and markers to self
        self.epochs = epochs
        self.markers = markers

        # Correct for selected outliers
        if not hasattr(self, 'matrixSelected'):
            self.matrixSelected = np.repeat('ok_normal', self.epochs.shape[0])
            self.matrixSelected[np.where(
                self.matrixThreshold.sum(axis=1))[0]] = 'threshold'
            self.matrixSelected[np.where(
                self.matrixBlink.sum(axis=1))[0]] = 'blink'
            self.matrixSelected[np.where(
                self.matrixBridge.sum(axis=1))[0]] = 'bridge'

        else:

            # Check if new datasets were loaded
            if self.matrixSelected.shape[0] < self.markers.shape[0]:
                startID = self.matrixSelected.shape[0]
                newLength = self.markers.shape[0] - startID
                newSelectedMatrix = np.repeat('ok_normal', newLength)
                newSelectedMatrix[np.where(self.matrixThreshold[
                    startID:].sum(axis=1))[0]] = 'threshold'
                newSelectedMatrix[np.where(self.matrixBlink[
                    startID:].sum(axis=1))[0]] = 'blink'
                newSelectedMatrix[np.where(self.matrixBridge[
                    startID:].sum(axis=1))[0]] = 'bridge'
                self.matrixSelected = np.hstack([self.matrixSelected,
                                                 newSelectedMatrix])

            # Correct if correction filters are off
            if not self.thresholdCorr:
                self.matrixSelected[
                    [i for i, e in enumerate(self.matrixSelected)
                     if 'thresh' in e]] = 'ok_normal'
                self.matrixThreshold *= False
            if not self.bridgeCorr:
                self.matrixSelected[
                    [i for i, e in enumerate(self.matrixSelected)
                     if 'bridge' in e]] = 'ok_normal'
                self.matrixBridge *= False
            if not self.blinkCorr:
                self.matrixSelected[
                    [i for i, e in enumerate(self.matrixSelected)
                     if 'blink' in e]] = 'ok_normal'
                self.matrixBlink *= False

            # Correct if correction filters are on
            if self.thresholdCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixThreshold.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'threshold'
            if self.bridgeCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixBridge.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'bridge'
            if self.blinkCorr:
                self.matrixSelected[
                    [i for i in np.where(self.matrixBlink.sum(axis=1))[0]
                     if self.matrixSelected[i] == 'ok_normal']] = 'blink'

            # Update List of ok and bad IDs
            self.okID = np.array([True if 'ok_' in e else False
                                  for e in self.matrixSelected])
            self.badID = np.invert(self.okID)

        # Drop bad Epochs for average
        goodEpochs = epochs[self.okID]
        goodMarkers = markers[self.okID]

        # Create average epochs but weighs collapsed markers accordingly
        if not hasattr(self, 'collapsedMarkers'):
            self.uniqueMarkers = np.unique(goodMarkers)
            self.avgEpochs = [
                goodEpochs[np.where(goodMarkers == u)].mean(axis=0)
                for u in self.uniqueMarkers]
        else:
            # Create average epochs but weigh collapsed markers
            self.avgEpochs = []
            self.uniqueMarkers = np.unique(self.collapsedMarkers[self.okID])

            for i, u in enumerate(self.uniqueMarkers):

                # Weigh collapsed markers to get average
                if len(markers[markers == u]) == 0:

                    collapseID = [c[1] for c in self.collapsedTransform
                                  if c[0] == u][0]
                    self.avgEpochs.append(
                        np.array([goodEpochs[np.where(
                            goodMarkers == c)[0]].mean(axis=0)
                            for c in collapseID]).mean(axis=0))
                else:
                    self.avgEpochs.append(
                        goodEpochs[np.where(goodMarkers == u)[0]].mean(axis=0))

            self.markers = self.collapsedMarkers

        self.avgGFP = [calculateGFP(a) for a in self.avgEpochs]
        self.avgGMD = [calculateGMD(a) for a in self.avgEpochs]

        Data.Overview.update(self)

        # Don't show more if no epoch survived
        if self.okID.sum() != 0:
            Data.GFPSummary.update(self)
            Data.GFPDetail.update(self)
            Data.EpochsDetail.update([])
            Data.ERPSummary.update([])


def butter_bandpass_param(fs, highcut=0, lowcut=0, order=2, notch=-1.0):

    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    notch = notch / nyq

    if notch > 0:
        b, a = butter(order, [notch - 1. / nyq, notch + 1. / nyq],
                      btype='bandstop')
    else:
        if lowcut == 0:
            b, a = butter(order, high, btype='high')
        elif highcut == 0:
            b, a = butter(order, low, btype='low')
        else:
            b, a = butter(order, [high, low], btype='band')
    return b, a


def butter_bandpass_param_old(fs, highcut=0, lowcut=0, order=2, notch=-1.0):
    # CARTOOL Version

    N = np.log2(fs)
    divisorHigh = float(2**(N - 1) + 2**(N - 3))
    divisorLow = float(2**(N - 2) + 2**(N - 3) + 2**(N - 5))

    if notch > 0:
        b, a = butter(order, [(notch / divisorHigh) - 1. / divisorHigh,
                              (notch / divisorLow) + 1. / divisorLow],
                      btype='bandstop')
    else:
        if lowcut == 0:
            b, a = butter(order, highcut / divisorHigh, btype='high')
        elif highcut == 0:
            b, a = butter(order, lowcut / divisorLow, btype='low')
        else:
            b, a = butter(order, [highcut / divisorHigh, lowcut / divisorLow],
                          btype='band')
    return b, a


def calculateGFP(dataset):
    # Global Field Potential
    return dataset.std(axis=0)


def calculateGMD(dataset):
    # Global Map Dissimilarity
    GFP = calculateGFP(dataset)
    unitaryStrength = dataset / GFP
    GMD = np.diff(unitaryStrength).std(axis=0)
    return np.insert(GMD, 0, 0)


def interpolateChannels(self, Data, xyz):

    xyz = ReadXYZ(xyz)
    channels2interpolate = Data.Specs.channels2interpolate

    id2interp = [i for i, e in enumerate(xyz.labels)
                 if e in channels2interpolate]
    id2keep = [i for i, e in enumerate(xyz.labels)
               if e not in channels2interpolate]

    matriceE = np.array([np.insert(e, 0, 1)
                         for e in xyz.coord[id2keep]])
    matriceK = np.zeros((len(id2keep), len(id2keep)))
    for i, r1 in enumerate(xyz.coord[id2keep]):
        for j, r2 in enumerate(xyz.coord[id2keep]):
            if i == j:
                matriceK[i, j] = 0
            else:
                Diff = (np.square(r1 - r2)).sum()
                matriceK[i, j] = Diff * np.log(Diff)
    matrice = np.concatenate((matriceK, matriceE), axis=1)
    addZeros = np.concatenate((matriceE.T, np.zeros((4, 4))), axis=1)
    matrice = np.concatenate((matrice, addZeros), axis=0)
    matriceInv = np.linalg.inv(matrice)

    # Create Progressbar for interpolation
    progressMax = Data.interpolEpochs.shape[0]
    dlg = wx.ProgressDialog(
        "Interpolation Progress", "Time remaining for Interpolation",
        progressMax,
        style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_SMOOTH)

    for count, epoch in enumerate(Data.interpolEpochs):

        signal = np.copy(epoch.T)

        Coef = []
        potential = np.concatenate((signal[:, id2keep],
                                    np.zeros((signal.shape[0], 4))),
                                   axis=1)
        for v in potential:
            Coef.append(np.dot(matriceInv, v))
        Coef = np.array(Coef)

        for b in id2interp:
            xyzInter = xyz.coord[b]
            Q = np.insert(xyzInter, 0, 1)
            CorrectCoord = xyz.coord[id2keep]
            Diff = np.array([np.square(xyzInter - c).sum()
                             for c in CorrectCoord])
            K = Diff * np.log(Diff)
            K[np.isnan(K)] = 0
            IntData = np.dot(Coef, np.concatenate((K, Q), axis=0))
            signal[:, b] = IntData
        Data.interpolEpochs[count] = signal.T

        dlg.Update(count)

    dlg.Destroy()

    return Data
