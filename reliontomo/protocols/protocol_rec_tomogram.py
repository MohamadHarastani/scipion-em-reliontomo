# *
# * Authors:     Scipion Team
# *
# * Unidad de  Bioinformatica of Centro Nacional de Biotecnologia , CSIC
# *
# * This program is free software; you can redistribute it and/or modify
# * it under the terms of the GNU General Public License as published by
# * the Free Software Foundation; either version 2 of the License, or
# * (at your option) any later version.
# *
# * This program is distributed in the hope that it will be useful,
# * but WITHOUT ANY WARRANTY; without even the implied warranty of
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# * GNU General Public License for more details.
# *
# * You should have received a copy of the GNU General Public License
# * along with this program; if not, write to the Free Software
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA
# * 02111-1307  USA
# *
# *  All comments concerning this program package may be sent to the
# *  e-mail address 'scipion-users@lists.sourceforge.net'
# *
# **************************************************************************
from enum import Enum
from pwem.convert.headers import fixVolume
from pyworkflow import BETA
from pyworkflow.protocol.params import FloatParam, IntParam, StringParam
from reliontomo import Plugin
from reliontomo.protocols.protocol_base_relion import ProtRelionTomoBase
from tomo.objects import Tomogram


class outputObjects(Enum):
    tomogram = Tomogram


class ProtRelionTomoReconstruct(ProtRelionTomoBase):
    """ This protocol reconstructs a single tomogram using Relion. It is very useful
    to check if the protocol "Prepare data" has been applied correctly (in terms of flip
    options, for example)
    """
    _label = 'Reconstruct tomogram'
    _devStatus = BETA

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # -------------------------- DEFINE param functions -----------------------
    def _defineParams(self, form):
        super()._defineCommonInputParams(form)
        form.addParam('tomoId', StringParam,
                      allowsNull=False,
                      label='Tomogram to be reconstructed')
        form.addParam('binFactor', FloatParam,
                      label='Binning factor',
                      default=8,
                      help='The binning will be applied concerning the size of '
                           'the tomograms used for the picking.')
        group = form.addGroup('Tomogram shape (pix.)')
        group.addParam('width', IntParam,
                       default=-1,
                       label='Width',
                       help='If -1, the width considered will be of the original tilt series after having applied the '
                            'introduced binning factor.')
        group.addParam('height', IntParam,
                       default=-1,
                       label='Height',
                       help='If -1, the height considered will be of the original tilt series after having applied the '
                            'introduced binning factor.')
        group.addParam('thickness', IntParam,
                       default=-1,
                       label='Thickness',
                       help='If -1, the thickness considered will be of the original tilt series after having applied '
                            'the introduced binning factor.')

        form.addParallelSection(threads=4, mpi=0)

    # -------------------------- INSERT steps functions -----------------------
    def _insertAllSteps(self):
        self._insertFunctionStep(self._reconstructStep)
        self._insertFunctionStep(self._createOutputStep)

    # -------------------------- STEPS functions ------------------------------

    def _reconstructStep(self):
        Plugin.runRelionTomo(self, 'relion_tomo_reconstruct_tomogram', self._genTomoRecCommand())

    def _createOutputStep(self):
        tomo = Tomogram()
        outFileName = self._getOutTomoFileName()
        fixVolume(outFileName)
        tomo.setLocation(outFileName)
        tomo.setSamplingRate(self.inReParticles.get().getTsSamplingRate() * self.binFactor.get())
        tomo.setOrigin()
        tomo.setTsId(self.tomoId.get())
        self._defineOutputs(**{outputObjects.tomogram.name: tomo})
        self._defineSourceRelation(self.inReParticles.get(), tomo)

    # -------------------------- INFO functions -------------------------------

    def _summary(self):
        summary = []
        if self.isFinished():
            summary.append('The selected tomogram was *%s*.' % self.tomoId.get())

        return summary

    # --------------------------- UTILS functions -----------------------------

    def _genTomoRecCommand(self):
        cmd = '--t %s ' % self.inReParticles.get().getTomograms()
        cmd += '--tn %s ' % self.tomoId.get()
        cmd += '--o %s ' % self._getOutTomoFileName()
        cmd += '--bin %.1f ' % self.binFactor.get()
        cmd += '--w %i ' % self.width.get()
        cmd += '--h %i ' % self.height.get()
        cmd += '--d %i ' % self.thickness.get()
        cmd += '--j %i ' % self.numberOfThreads.get()
        return cmd

    def _getOutTomoFileName(self):
        return self._getExtraPath(self.tomoId.get() + '.mrc')
















