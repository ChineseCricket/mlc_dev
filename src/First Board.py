
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
#---------------------- FUNCTION DEFINITION --------------------------
def LGenerator(via_pad_width) -> gf.Component:
    '''
    GENERATE L COMPONENT.
    '''
    pitch = L.line_width + L.gap_width # define pitch of inductor
    L_pad_gap = via_pad_width/2 + pitch #offset to create via
    CoilPath = [(0,0)] # initialize path list
    LCircuit = gf.Component() # initialize component

    # generate path for inductor
    for i in range(L.num_turns):
        p1 = (i * pitch, L.outer_diameter - L.line_width - i*pitch)
        p2 = (L.outer_diameter - L.line_width - i*pitch, L.outer_diameter - L.line_width - i*pitch)
        p3 = (L.outer_diameter - L.line_width - i*pitch, i*pitch)
        p4 = ((i+1) * pitch, i * pitch)
        CoilPath += [p1, p2, p3, p4]

    i = i + 1
    CoilPath += [(i * pitch, L.outer_diameter - L.line_width - 1.5*i*pitch)] # add final half length up path

    CoilPath = gf.Path(CoilPath) # create path object for inductor
    Coil = LCircuit << gf.path.extrude(CoilPath, layer=LAYER.GP, width=L.line_width) # extrude path to create inductor

    inside_pad = LCircuit << gf.components.rectangle(size=(L.outer_diameter - L.line_width - 2*i*pitch + pitch/2, .5 * i* pitch), layer=LAYER.GP) # create inside pad
    inside_pad.xmin = i*pitch - L.line_width/2
    inside_pad.ymin = L.outer_diameter - L.line_width - 1.5*i*pitch

    return LCircuit

def CGenerator() -> gf.Component:
    '''
    GENERATE C COMPONENT.
    '''
    num_lines = 300
    CCircuit = gf.Component() # initialize component

    # calculate size
    C.line_height = 2000
    C.width = num_lines * (C.line_width + C.gap_width)
    C.height = C.base_height * 2 + C.line_height + C.gap_width # total height of capacitor

    # generate base
    bot = CCircuit << gf.components.rectangle(size=(C.width,C.base_height), layer=LAYER.GP) 
    top = CCircuit << gf.components.rectangle(size=(C.width,C.base_height), layer=LAYER.GP)
    top.movey(C.base_height + C.gap_width + C.line_height)

    # create lines
    for i in range(num_lines):
        line = CCircuit << gf.components.rectangle(size=(C.line_width, C.line_height), layer=LAYER.GP)
        line.xmin = i * (C.line_width + C.gap_width)
        if i % 2 == 0:
            line.ymin = C.base_height + C.gap_width
        else:
            line.ymin = C.base_height
    
    return CCircuit

@gf.cell
def LCGenerator(via_pad_width) -> gf.Component:
    ''' 
    GENERATE LC CELL.
    '''
    LCircuit = LGenerator(via_pad_width)
    CCircuit = CGenerator()
    LCCircuit = gf.Component() # initialize component
    Inductor = LCCircuit << LCircuit
    Capacitor = LCCircuit << CCircuit
    Capacitor.xmin = Inductor.xmin
    Capacitor.ymax = LCircuit.ymin - LC.gap
    ConnectingLine = LCCircuit << gf.components.rectangle(size=(L.line_width, LC.gap + L.line_width/2), layer=LAYER.GP)
    ConnectingLine.xmin = Inductor.xmin
    ConnectingLine.ymin = Capacitor.ymax
    
    return LCCircuit
# %%
LCCircuit = LCGenerator(via_pad_width)
# %%
LCCircuit
# %%
