import gdsfactory as gf
import numpy as np

from Parameters_Classes import *
from Layer_Definition import *

# ---------------------- GLOBAL CONSTANTS --------------------------
#Initialize GENERAL PARAMETERS
font_size = 400
x0 = 0
y0 = 0
via_pad_width = 40 # Size of via pads for capacitor and inductor to change metal plane 
tolerance = 10 # * 1000
boundary = BoundaryClass()
num_layers = 1 # number of layers used in this design
capacitor_type = "PPC" # type of capacitor (PPC or IDC)

#WIRING PARAMETERS
chip = Chip()
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
        p3 = (L.outer_diameter - L.line_width - i*pitch, i*pitch + L.line_width)
        p4 = ((i+1) * pitch, i * pitch + L.line_width)
        CoilPath += [p1, p2, p3, p4]

    i = i + 1

    if L.num_layers == 1:
        # need to create pads

        CoilPath += [(i * pitch, L.outer_diameter - L.line_width - 1.5*i*pitch)] # add final half length up path

        CoilPath = gf.Path(CoilPath) # create path object for inductor
        Coil = LCircuit << gf.path.extrude(CoilPath, layer=LAYER.GP, width=L.line_width) # extrude path to create inductor

        inside_pad = LCircuit << gf.components.rectangle(size=(L.outer_diameter - L.line_width - 2*i*pitch + pitch/2, .5 * i* pitch), layer=LAYER.GP) # create inside pad
        inside_pad.xmin = i*pitch - L.line_width/2
        inside_pad.ymin = L.outer_diameter - L.line_width - 1.5*i*pitch
    
    elif L.num_layers == 3:
        # need to create connecting wires

        CoilPath += [(i*pitch, L.outer_diameter - L.line_width - i*pitch - L_pad_gap)] # add final near full length up path
        CoilPath += [(i*pitch + 4.5*L.line_width, L.outer_diameter - L.line_width - i*pitch - L_pad_gap)] # add small horizontal path 

        CoilPath = gf.Path(CoilPath) # create path object for inductor
        Coil = LCircuit << gf.path.extrude(CoilPath, layer=LAYER.GP, width=L.line_width) # extrude path to create inductor

        GPvia = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.GP) # via in ground plane layer
        GPvia.movex(i*pitch + 4.5*L.line_width).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2)

        TMvia = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Top) # via in top layer
        TMvia.movex(i*pitch + 4.5*L.line_width).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2)

        Dhole = LCircuit << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance), layer=LAYER.D) # hole in dielectric layer
        Dhole.movex(TMvia.xmin + tolerance).movey(TMvia.ymin + tolerance)

        # Ohole = LCircuit << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance), layer=LAYER.Oxide) # hole in oxide layer
        # Ohole.movex(TMvia.xmin + tolerance).movey(TMvia.ymin + tolerance)

        wire = LCircuit << gf.components.rectangle(size=(L.line_width, L.outer_diameter - (L.outer_diameter - L.line_width - i*pitch  - L_pad_gap + L.line_width/2 + via_pad_width/2) + 50*tolerance), layer=LAYER.Top) # wire on top metal layer
        wire.movex(i*pitch + 4*L.line_width +  via_pad_width/2).movey(L.outer_diameter - L.line_width - i*pitch - L_pad_gap + via_pad_width/2)

    else:
        raise KeyError('Invalid Number of Layers.')

    return LCircuit

def CGenerator() -> gf.Component:
    '''
    GENERATE C COMPONENT.
    '''
    CCircuit = gf.Component() # initialize component
    if C.type == 'IDC':
        num_lines = 300

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
        
        # if C.num_layer == 3:
        #     # if use 3 layer, create vias.
        #     via = CCircuit << gf.components.rectangle((via_pad_width, via_pad_width), LAYER.Oxide) # via in SiO2
        #     via.movex(C.length/2 - via_pad_width/2).movey(11*tolerance)
            
        #     square = CCircuit << gf.components.rectangle((via_pad_width + 4*tolerance, via_pad_width + 4*tolerance), LAYER.Top) # square pad
        #     square.movex(via.xmin - 2*tolerance).movey(via.ymin - 2*tolerance)

        #     wire = CCircuit << gf.components.rectangle((TL_width, square.ymin), LAYER.Top) # wire
        #     wire.movex(square.xmin + via_pad_width/2 + 2*tolerance - TL_width/2)
        return CCircuit
    
    elif C.type == 'PPC':
        CCircuit = gf.Component() # initialize component

        GPlane = CCircuit << gf.components.rectangle((C.length + 2*tolerance,C.length + 2*tolerance), LAYER.GP) # ground plane

        Dielectric = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.D) # dieletric material
        Dielectric.movex(tolerance).movey(tolerance)

        TPlane = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.Top) # top plane
        TPlane.movex(tolerance).movey(tolerance)

        CCircuit.add_port(name='PPCin', center=[TPlane.xmin + C.length/2, TPlane.ymin], orientation=270, width=TL_width, layer=LAYER.Top)
        # via = CCircuit << gf.components.rectangle((via_pad_width, via_pad_width), LAYER.Oxide) # via in SiO2
        # via.movex(C.length/2 + tolerance - via_pad_width/2).movey(11*tolerance)

        # #WIRING LAYER (MICROSTRIP)
        # square = CCircuit << gf.components.rectangle((via_pad_width + 4*tolerance, via_pad_width + 4*tolerance), LAYER.Top) # square pad
        # square.movex(via.xmin - 2*tolerance).movey(via.ymin - 2*tolerance)

        # wire = CCircuit << gf.components.rectangle((TL_width, square.ymin), LAYER.Top) # wire
        # wire.movex(square.xmin + via_pad_width/2 + 2*tolerance - TL_width/2)
       
        return CCircuit
    
    else:
        raise KeyError('Invalid Capacitor Type.')

@gf.cell
def LCGenerator(via_pad_width,capacitor_type,num_layers) -> gf.Component:
    ''' 
    GENERATE LC CELL.
    '''

    global L
    global C
    L = InductorClass(num_layers)
    C = CapacitorClass(capacitor_type, num_layers)

    # initialize component
    LCircuit = LGenerator(via_pad_width)
    CCircuit = CGenerator()
    LCCircuit = gf.Component()
    
    # collect up
    Inductor = LCCircuit << LCircuit
    Capacitor = LCCircuit << CCircuit
    
    # alignment
    Capacitor.xmin = Inductor.xmin
    Capacitor.ymax = LCircuit.ymin - LC.gap
    ConnectingLine = LCCircuit << gf.components.rectangle(size=(TL_width, LC.gap), layer=LAYER.GP)
    ConnectingLine.xmin = Inductor.xmin
    ConnectingLine.ymin = Capacitor.ymax

    # suceed ports
    LCCircuit.add_port(name='PPCin', port=Capacitor.ports['PPCin'])

    if num_layers == 3:
        #creat pads
        Pad = gf.components.rectangle((pad.width, pad.width), layer=LAYER.Top)

        Bias = LCCircuit << Pad
        Bias.xmin = Capacitor.xmin
        Bias.ymax = Capacitor.ymin - 50*tolerance

        TESin = LCCircuit << Pad
        TESin.xmin = Inductor.xmin
        TESin.ymin = Inductor.ymax - pad.width/2

        TESout = LCCircuit << Pad
        TESout.xmin = TESin.xmax + L.outer_diameter
        TESout.ymin = TESin.ymin

        GPad = LCCircuit << Pad
        GPad.xmin = TESout.xmin
        GPad.ymin = Bias.ymin
        LCCircuit.add_port(name='Biasout', center=[Bias.xmin + pad.width/2, Bias.ymax], orientation=90, width=TL_width, layer=LAYER.Top)

        #create wires
        BiasWire = gf.routing.get_route_electrical(LCCircuit.ports["Biasout"], LCCircuit.ports["PPCin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
        LCCircuit.add(BiasWire.references)

        TESinWire = LCCircuit << gf.components.rectangle((L.num_turns*(L.line_width+L.gap_width) + 4.5*L.line_width + via_pad_width/2 - pad.width, TL_width), layer=LAYER.Top)
        TESinWire.xmin = TESin.xmax
        TESinWire.ymax = Inductor.ymax

        LCCircuit.add_port(name='TESoutPadout', center=[TESout.xmin + pad.width/2, TESout.ymin], orientation=270, width=TL_width, layer=LAYER.Top)
        LCCircuit.add_port(name='GPadin', center=[GPad.xmin + pad.width/2, GPad.ymax], orientation=90, width=TL_width, layer=LAYER.Top)
        GrondRoute = gf.routing.get_route_electrical(LCCircuit.ports["TESoutPadout"], LCCircuit.ports["GPadin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
        LCCircuit.add(GrondRoute.references)
    
    return LCCircuit