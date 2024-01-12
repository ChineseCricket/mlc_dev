
# %%
from pydantic import BaseModel
import numpy as np
import os

import gdsfactory as gf
from gdsfactory.generic_tech import LAYER, LAYER_STACK
from gdsfactory.generic_tech.get_klayout_pyxs import get_klayout_pyxs
from gdsfactory.technology import LayerLevel, LayerStack, LayerViews, LayerMap
from gdsfactory.generic_tech import get_generic_pdk

from Parameters_Classes import *
from Component import *
# %%
# ---------------------- INITIAILIZATION --------------------------
print("Note: default length unit is microns. \n")
# import chip parameters from text file
# directory = os.getcwd() + "/"
# filename = 'Parameters_128mux_example_chip.txt'
# chip, C = read_chip_parameters( directory, filename) # read general chip + capacitor parameters
# print("Chip parameters read sucessfully.")
chip = Chip()
# Output location for gds file
directory = '../output/'
filename = 'test.gds'
fileoutput = directory + filename
# %%
# ---------------------- LAYER DEFINITION --------------------------
Layer = tuple[int, int]

class LCLayerMap(LayerMap):
    '''
    Generates a LayerMap for LC components.
    '''
    WAFER: Layer = (99999, 0)

    GP: Layer = (1, 0)
    D: Layer = (4, 4)
    MS: Layer = (2, 5)
    Oxide: Layer = (10, 10)
    Top: Layer = (11, 11)

    class Config:
        """pydantic config."""

        frozen = True
        extra = "forbid"

LAYER = LCLayerMap()
# %%
# ---------------------- GLOBAL CONSTANTS --------------------------
#GENERAL PARAMETERS
font_size = 400
x0 = 0
y0 = 0
via_pad_width = 40 # Size of via pads for capacitor and inductor to change metal plane 
tolerance = 10 # * 1000
boundary = BoundaryClass()
num_layers = 1 # number of layers used in this design
capacitor_type = "IDC" # type of capacitor (PPC or IDC)

#WIRING PARAMETERS
TL_width = chip.TL_width # width of transmission line
wire2wire_space = chip.wire2wire_space # space between wires
wiring_gap = chip.wiring_gap # for the corners

# INDUCTOR PARAMETERS
L = InductorClass(num_layers)

# CAPACITOR PARAMETERS
freq_array = chip.frequency_schedule  # frequency schedule (rest of parameters were imported from text file earlier)
C = CapacitorClass(capacitor_type, num_layers)

# LC PARAMETERS
LC_height = 2*L.outer_diameter 
if num_layers == 1:
    LC_height = LC_height + L.pad_gap + L.pad_width

LC = ResonatorClass( LC_height, L.outer_diameter ) # Individual Resonator Parameters. (height, width)

# WIREBOND PADS PARAMETERS
pad = PadClass()
num_pads = chip.num_LCs
# %%
print('Start')
# %%
LCCircuit = LCGenerator(L,C,LC,LAYER,via_pad_width)
print('Pass')
# %%
LCCircuit.plot()
# %%
