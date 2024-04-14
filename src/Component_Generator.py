import gdsfactory as gf
import numpy as np

from Parameters_Classes import *
from Layer_Definition import *

# ---------------------- GLOBAL CONSTANTS --------------------------
#Initialize GENERAL PARAMETERS
font_size = 400
x0 = 0
y0 = 0
via_pad_width = 20 # Size of via pads for capacitor and inductor to change metal plane 
tolerance = 4 # General tolerance
num_layers = 3 # number of layers used in this design
# capacitor_type = "PPC" # type of capacitor (PPC or IDC)
BoardSize = 500 # size of the board
ConnectingPadSize = [90,30] # size of the connecting pads
# Frequency = 1e6 # capacity of the capacitor

#WIRING PARAMETERS
chip = Chip()
TL_width = chip.TL_width # width of transmission line
# wire2wire_space = chip.wire2wire_space # space between wires
# wiring_gap = chip.wiring_gap # for the corners

# INDUCTOR PARAMETERS
L = InductorClass(num_layers)

# LC PARAMETERS
LC_height = 2*L.outer_diameter 
if num_layers == 1:
    LC_height = LC_height + L.pad_gap + L.pad_width

LC = ResonatorClass( LC_height, L.outer_diameter ) # Individual Resonator Parameters. (height, width)

# WIREBOND PADS PARAMETERS
pad = PadClass()
num_pads = chip.num_LCs

@gf.cell
def AlignMarker(layer,num_mark) -> gf.Component:
    '''
    Create alignment marker.
    '''
    # Create a new component
    Marker = gf.Component()
    GShape = gf.Component()

    GShape.add_polygon([(-10,10), (-10, 100), (-60, 100), (-60, 120), (60,120), (60,100), (10,100), (10,10)], layer=LAYER.GP)
    GShape.add_polygon([(-2,195), (-2,240), (-60,240), (-60,260), (60,260), (60,240), (2,240), (2,195)], layer=LAYER.GP)
    GShape.add_polygon([(-1,335), (-1,380), (-60,380), (-60,400), (60,400), (60,380), (1,380), (1,335)], layer=LAYER.GP)
    GShape

    S1 = Marker << GShape
    S2 = Marker << GShape
    S3 = Marker << GShape
    S4 = Marker << GShape
    S2.rotate(90)
    S3.rotate(180)
    S4.rotate(270)

    Marker.add_polygon([(0,0), (0,10), (-10,10), (-10,0)], layer=LAYER.GP)

    Text0 = Marker.add_ref(gf.components.text_freetype('Mark '+str(num_mark), size=300, layer=LAYER.GP, font='FangSong'))
    Text0.movey(-125).movex(705)

    TShape = gf.Component()
    Inverse = gf.Component()

    TShape.add_polygon([(-10,120), (-10,125), (-30,125), (-30,130), (-60,130), (-60,150), (-2,150), (-2,195), (2,195), (2,150), (60,150), (60,130), (30,130), (30,125), (10,125), (10,120)], layer=layer)

    TShape.add_polygon([(-10,260), (-10,265), (-30,265), (-30,270), (-60,270), (-60,290), (-1,290), (-1,335), (1,335), (1,290), (60,290), (60,270), (30,270), (30,265), (10,265), (10,260)], layer=layer)

    TShape.add_polygon([(20,20), (11,20), (11,35), (12,35), (12,50), (13,50), (13,65), (14,65), (14,80), (15,80), (15,90), (30,90), (30,30), (90,30), (90,15), (80,15), (80,14), (65,14), (65,13), (50,13), (50,12), (35,12), (35,11), (20,11)], layer=layer)

    S5 = Inverse << TShape
    S6 = Inverse << TShape
    S7 = Inverse << TShape
    S8 = Inverse << TShape
    S6.rotate(90)
    S7.rotate(180)
    S8.rotate(270)

    Marker << gf.geometry.invert(Inverse, layer=layer, border=115)

    Text1 = Marker.add_ref(gf.components.text_freetype('Mark '+str(num_mark), size=300, layer=layer, font='FangSong'))
    Text1.movey(-125).movex(-1545)
    
    return Marker


@gf.cell
def SLGenerator(layer) -> gf.Component:
    '''
    Generate singgle L Component for GP layer and SiO2 layer.
    '''
    #L Component
    pitch = L.line_width + L.gap_width # define pitch of inductor
    L_pad_gap = via_pad_width/2 + pitch #offset to create via
    CoilPath = [(0,L.outer_diameter/2)] # initialize path list
    LCircuit = gf.Component() # initialize component

    # generate path for inductor
    for i in range(L.num_turns):
        p1 = (i * pitch, L.outer_diameter - L.line_width - i*pitch)
        p2 = (L.outer_diameter - L.line_width - i*pitch, L.outer_diameter - L.line_width - i*pitch)
        p3 = (L.outer_diameter - L.line_width - i*pitch, i*pitch + L.line_width)
        p4 = ((i+1) * pitch, i * pitch + L.line_width)
        CoilPath += [p1, p2, p3, p4]

    i = i + 1
    L2TL = LCircuit << gf.components.optimal_step(start_width=TL_width, end_width=L.line_width, num_pts=100, layer=layer, anticrowding_factor=0.5).rotate(-90)
    L2TL.xmin = i*pitch - L.line_width/2
    L2TL.ymin = i*pitch + 20
    GPvia = LCircuit << gf.components.rectangle(size=(via_pad_width + tolerance, via_pad_width + tolerance), layer=layer) # via in ground plane layer
    GPvia.movex(L.outer_diameter/2 - via_pad_width/2 - tolerance/2).movey(L.outer_diameter/2 - via_pad_width/2 - tolerance/2) # move via to correct position
    GPviapin = LCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width + tolerance, num_pts=100, symmetric=True, layer=layer, anticrowding_factor=0.5)
    GPviapin.xmax = GPvia.xmin
    GPviapin.ymin = GPvia.ymin

    CoilPath += [(i*pitch, i*pitch + 20)] # add small vertical line to connect to via

    CoilPath = gf.path.smooth(points=CoilPath, radius=10) # create path object for inductor
    # CoilPath = gf.Path(CoilPath)
    Coil = LCircuit << gf.path.extrude(CoilPath, layer=layer, width=L.line_width) # extrude path to create inductor

    LCircuit.add_port(name='via0', port=L2TL.ports['e1'])
    LCircuit.add_port(name='via1', port=GPviapin.ports['e1'])
    ViaLine = gf.routing.get_route_electrical(LCircuit.ports["via0"], LCircuit.ports["via1"], bend="bend_euler", radius=10, layer=layer, width=TL_width)
    LCircuit.add(ViaLine.references)

    LCircuit.add_port(name='Coilin', center=[0,L.outer_diameter/2], orientation=270, width=L.line_width, layer=layer) # add port to inductor

    return LCircuit

@gf.cell
def LGenerator(layer) -> gf.Component:
    '''
    Generator multiplied L Component for GP layer and SiO2 layer.
    '''
    SL = SLGenerator(layer) # initialize single coil component
    LCircuit = gf.Component() # initialize component
    
    # Create coils
    L1 = LCircuit << SL # coil on phase 1
    L2 = LCircuit << SL # coil on phase 2
    L2.rotate(90)
    L2.movex(-L.gap_width)
    L3 = LCircuit << SL # coil on phase 3
    L3.rotate(180)
    L3.movex(-L.gap_width).movey(-L.gap_width)
    L4 = LCircuit << SL # coil on phase 4
    L4.rotate(270)
    L4.movey(-L.gap_width)

    # Create connecting lines
    LCircuit.add_port(name='Coilin1', port=L1.ports['Coilin'])
    LCircuit.add_port(name='Coilin2', port=L2.ports['Coilin'])
    LCircuit.add_port(name='Coilin3', port=L3.ports['Coilin'])
    LCircuit.add_port(name='Coilin4', port=L4.ports['Coilin'])
    Connecting12 = gf.routing.get_route_electrical(LCircuit.ports["Coilin1"], LCircuit.ports["Coilin2"], bend="bend_euler", radius=10, layer=LAYER.GP, width=L.line_width)
    LCircuit.add(Connecting12.references)
    Connecting34 = gf.routing.get_route_electrical(LCircuit.ports["Coilin3"], LCircuit.ports["Coilin4"], bend="bend_euler", radius=10, layer=LAYER.GP, width=L.line_width)
    LCircuit.add(Connecting34.references)

    if L.num_layers == 3:
        i = L.num_turns
        pitch = L.line_width + L.gap_width

        viahole = gf.components.rectangle(size = (via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)

        vh1 = LCircuit << viahole
        vh1.movex(L.outer_diameter/2 - via_pad_width/2 + tolerance/2).movey(L.outer_diameter/2 - via_pad_width/2 + tolerance/2)
        vh2 = LCircuit << viahole
        vh2.movex(L.outer_diameter/2 - via_pad_width/2 + tolerance/2 + L.gap_width).movey(L.outer_diameter/2 - via_pad_width/2 + tolerance/2).rotate(-90)

        viapad = gf.components.rectangle(size = (via_pad_width,via_pad_width), layer=LAYER.Bond0)

        vp1 = LCircuit << viapad
        vp1.xmax = vh1.xmax + tolerance/2
        vp1.ymax = vh1.ymax + tolerance/2

        vp2 = LCircuit << viapad
        vp2.xmax = vh2.xmax + tolerance/2
        vp2.ymax = vh2.ymax + tolerance/2

        Pad2TL = gf.components.optimal_step(start_width=L.line_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(90)

        pt1 = LCircuit << Pad2TL
        pt1.xmax = vp1.xmax
        pt1.ymax = vp1.ymin

        pt2 = LCircuit << Pad2TL
        pt2.rotate(180)
        pt2.ymin = vp2.ymax
        pt2.xmax = vp2.xmax

        LCircuit.add_port(name='TL0', port=pt1.ports['e1'])
        LCircuit.add_port(name='TL1', port=pt2.ports['e1'])
        
        Connecting14 = gf.routing.get_route_electrical(LCircuit.ports["TL0"], LCircuit.ports["TL1"], bend="bend_euler", radius=10, layer=LAYER.Bond0, width=L.line_width)
        LCircuit.add(Connecting14.references)

        ViaPadBond1 = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Bond0) # via pad on Bond layer
        ViaPadBond1.movex(L.outer_diameter/2 - via_pad_width/2).movey(L.outer_diameter/2 - via_pad_width/2 + L.gap_width).rotate(90)
        ViaPadBondpin1 = LCircuit << gf.components.optimal_step(start_width=TL_width - tolerance/2, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0).rotate(-90)
        ViaPadBondpin1.xmax = ViaPadBond1.xmax
        ViaPadBondpin1.ymin = ViaPadBond1.ymax

        LCircuit.add_port(name='Lin', center=[ViaPadBondpin1.xmin + via_pad_width/2, ViaPadBondpin1.ymax], orientation=90, width=TL_width - tolerance/2, layer=LAYER.Bond0)

        ViaPadBond2 = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Bond0) # via pad on Bond layer
        ViaPadBond2.movex(L.outer_diameter/2 - via_pad_width/2 + L.gap_width).movey(L.outer_diameter/2 - via_pad_width/2 + L.gap_width).rotate(180)
        ViaPadBondpin2 = LCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0).rotate(90)
        ViaPadBondpin2.xmax = ViaPadBond2.xmax
        ViaPadBondpin2.ymax = ViaPadBond2.ymin

        LCircuit.add_port(name='Lout', center=[ViaPadBondpin2.xmin + via_pad_width/2, ViaPadBondpin2.ymin], orientation=-90, width=TL_width, layer=LAYER.Bond0)

        viahole1 = LCircuit << gf.components.rectangle(size=(via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)
        viahole1.xmin = ViaPadBond1.xmin + tolerance/2
        viahole1.ymin = ViaPadBond1.ymin + tolerance/2
        viahole2 = LCircuit << gf.components.rectangle(size=(via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)
        viahole2.xmin = ViaPadBond1.xmin + tolerance/2
        viahole2.ymin = ViaPadBond1.ymin + tolerance/2

    return LCircuit

@gf.cell
def SLGenerator_sim(num_layers) -> gf.Component:
    '''
    Generate single L Component for Simulation.
    '''
    global L
    L = InductorClass(num_layers)

    LCircuit = gf.Component()
    Inductor = LCircuit << SLGenerator(layer=LAYER.GP)

    viahole = gf.components.rectangle(size = (via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)

    vh1 = LCircuit << viahole
    vh1.movex(L.outer_diameter/2 - via_pad_width/2 + tolerance/2).movey(L.outer_diameter/2 - via_pad_width/2 + tolerance/2)

    viapad = gf.components.rectangle(size = (via_pad_width,via_pad_width), layer=LAYER.TP)

    vp1 = LCircuit << viapad
    vp1.xmax = vh1.xmax + tolerance/2
    vp1.ymax = vh1.ymax + tolerance/2

    Pad2TL = gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.TP, anticrowding_factor=0.75).rotate(90)

    pt1 = LCircuit << Pad2TL
    pt1.xmax = vp1.xmax
    pt1.ymax = vp1.ymin

    OutLine = gf.components.rectangle(size=(TL_width, pt1.xmin - LCircuit.xmin + 2*tolerance), layer=LAYER.TP)

    OL1 = LCircuit << OutLine
    OL1.xmin = pt1.xmin + (via_pad_width-TL_width)/2
    OL1.ymax = pt1.ymin

    OutPad = gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.TP)

    OP1 = LCircuit << OutPad
    OP1.xmin = OL1.xmin - (via_pad_width-TL_width)/2
    OP1.ymax = OL1.ymin

    vh2 = LCircuit << viahole
    vh2.ymax = OP1.ymax - tolerance/2
    vh2.xmin = -(via_pad_width - tolerance)/2

    vp2 = LCircuit << viapad
    vp2.xmin = vh2.xmin - tolerance/2
    vp2.ymax = vh2.ymax + tolerance/2

    gvp2 = LCircuit << gf.components.rectangle(size=(via_pad_width + tolerance, via_pad_width + tolerance), layer=LAYER.GP)
    gvp2.xmin = vp2.xmin - tolerance/2
    gvp2.ymax = vp2.ymax + tolerance/2

    gp2L = LCircuit << gf.components.optimal_step(start_width=L.line_width, end_width=via_pad_width + tolerance, num_pts=100, symmetric=True, layer=LAYER.GP, anticrowding_factor=0.75).rotate(-90)
    gp2L.xmin = gvp2.xmin
    gp2L.ymin = gvp2.ymax

    LCircuit.add_port(name='gp2L', port=gp2L.ports['e1'])
    LCircuit.add_port(name='Coil', port=Inductor.ports['Coilin'])

    ConnectingLine = gf.routing.get_route_electrical(LCircuit.ports["gp2L"], LCircuit.ports["Coil"], bend="bend_euler", radius=10, layer=LAYER.GP, width=L.line_width)
    LCircuit.add(ConnectingLine.references)

    return LCircuit

@gf.cell
def LGenerator_sim(num_layers) -> gf.Component:
    '''
    Generate L Component for Simulation.
    '''
    global L
    L = InductorClass(num_layers)
    
    LCircuit = gf.Component()
    Inductor = LCircuit << LGenerator(layer=LAYER.GP)
    i = L.num_turns
    pitch = L.line_width + L.gap_width

    viahole = gf.components.rectangle(size = (via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)

    vh1 = LCircuit << viahole
    vh1.movex(-L.outer_diameter/2 - via_pad_width/2 + tolerance/2 - L.gap_width).movey(L.outer_diameter/2 - via_pad_width/2 + tolerance/2)
    vh2 = LCircuit << viahole
    vh2.movex(-L.outer_diameter/2 - via_pad_width/2 + tolerance/2 - L.gap_width).movey(L.outer_diameter/2 - via_pad_width/2 + tolerance/2 + L.gap_width).rotate(90)

    viapad = gf.components.rectangle(size = (via_pad_width,via_pad_width), layer=LAYER.TP)

    vp1 = LCircuit << viapad
    vp1.xmax = vh1.xmax + tolerance/2
    vp1.ymax = vh1.ymax + tolerance/2

    vp2 = LCircuit << viapad
    vp2.xmax = vh2.xmax + tolerance/2
    vp2.ymax = vh2.ymax + tolerance/2

    Pad2TL = gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.TP, anticrowding_factor=0.75)

    pt1 = LCircuit << Pad2TL
    pt1.xmax = vp1.xmin
    pt1.ymax = vp1.ymax

    pt2 = LCircuit << Pad2TL
    pt2
    pt2.ymin = vp2.ymin
    pt2.xmax = vp2.xmin

    OutLine = gf.components.rectangle(size=(pt1.xmin - LCircuit.xmin + 2*tolerance, TL_width), layer=LAYER.TP)

    OL1 = LCircuit << OutLine
    OL1.xmax = pt1.xmin
    OL1.ymin = pt1.ymin + (via_pad_width-TL_width)/2

    OL2 = LCircuit << OutLine
    OL2.xmax = pt2.xmin
    OL2.ymin = pt2.ymin + (via_pad_width-TL_width)/2

    OutPad = gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.TP)

    OP1 = LCircuit << OutPad
    OP1.xmax = OL1.xmin
    OP1.ymax = OL1.ymax + (via_pad_width-TL_width)/2

    OP2 = LCircuit << OutPad
    OP2.xmax = OL2.xmin
    OP2.ymax = OL2.ymax + (via_pad_width-TL_width)/2

    # LCircuit.add_port(name='TL0', port=pt1.ports['e1'])
    # LCircuit.add_port(name='TL1', port=pt2.ports['e1'])
    
    # Connecting14 = gf.routing.get_route_electrical(LCircuit.ports["TL0"], LCircuit.ports["TL1"], bend="bend_euler", radius=10, layer=LAYER.TP, width=L.line_width)
    # LCircuit.add(Connecting14.references)
    # LCircuit.add_port(name='Coilin', port=Inductor.ports['Coilin'])

    # # L wire parameters
    # pitch = L.line_width + L.gap_width # define pitch of inductor
    # L_pad_gap = via_pad_width/2 + pitch #offset to create via
    # i = L.num_turns # number of turns in coil
    
    # ConnectingLine = LCircuit << gf.components.optimal_step(start_width=L.line_width, end_width=TL_width, num_pts=50, layer=LAYER.GP).rotate(-90)
    # ConnectingLine.xmin = Inductor.xmin
    # ConnectingLine.ymin = Inductor.ymin - LC.gap
    # LCircuit.add_port(name='ConnectingLineout', center=[ConnectingLine.xmin + L.line_width/2, ConnectingLine.ymax], orientation=90, width=L.line_width, layer=LAYER.GP)

    # LCconnecting = gf.routing.get_route_electrical(LCircuit.ports["Coilin"], LCircuit.ports["ConnectingLineout"], bend="bend_euler", radius=10, layer=LAYER.GP, width=L.line_width)
    # LCircuit.add(LCconnecting.references)


    return LCircuit

@gf.cell
def CGenerator(via_pad_width,capacitor_type,num_layers,Frequency,ratio = 1) -> gf.Component:
    ''' 
    GENERATE only C CELL.
    '''

    global C
    C = CapacitorClass(capacitor_type, num_layers, Frequency,ratio)
    global L
    L = InductorClass(num_layers)

    #C component
    CCircuit = gf.Component() # initialize component
    
    if C.type == 'IDC':
        num_lines = C.finger_num

        # calculate size
        C.width = num_lines * (C.line_width + C.gap_width)
        C.height = C.base_height * 2 + C.line_height + C.gap_width # total height of capacitor

        # generate base
        bot = CCircuit << gf.components.rectangle(size=(C.width,C.base_height), layer=LAYER.GP) 
        top = CCircuit << gf.components.rectangle(size=(C.width,C.base_height), layer=LAYER.GP)
        top.movey(C.base_height + C.gap_width + C.line_height)
        botBond = CCircuit << gf.components.rectangle(size=(C.width,C.base_height), layer=LAYER.Bond0)

        # create lines
        for i in range(num_lines):
            line = CCircuit << gf.components.rectangle(size=(C.line_width, C.line_height), layer=LAYER.GP)
            line.xmin = i * (C.line_width + C.gap_width)
            if i % 2 == 0:
                line.ymin = C.base_height + C.gap_width
            else:
                line.ymin = C.base_height
        
        CCircuit.add_port(name='Cin', center=[(CCircuit.xmax+CCircuit.xmin) / 2, CCircuit.ymin], orientation=270, width=TL_width, layer=LAYER.Bond0)
    
    elif C.type == 'PPC':
        CCircuit = gf.Component() # initialize component

        GPlane = CCircuit << gf.components.rectangle((C.length + 2*tolerance,C.length + 2*tolerance), LAYER.GP) # ground plane

        Cpin = CCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.GP, anticrowding_factor=0.5).rotate(-90)
        Cxp1 = GPlane.xmin + C.length/2 - via_pad_width/2 + tolerance
        Cxp2 = GPlane.xmin + L.outer_diameter/2 - ConnectingPadSize[0] + via_pad_width/2 - tolerance
        Cpin.xmin = min([Cxp1,Cxp2])
        Cpin.ymin = GPlane.ymax

        CCircuit.add_port(name='Cin', port=Cpin.ports['e1'])

        BondPad = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.Bond0) # bonding pad
        BondPad.movex(tolerance).movey(tolerance)

        TPlane = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.TP) # top plane and dielectric
        TPlane.movex(tolerance).movey(tolerance)

        Cpout = CCircuit << gf.components.optimal_step(start_width=TL_width-tolerance/2, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(90)
        Cpout.xmin = BondPad.xmin + C.length/2 - via_pad_width/2
        Cpout.ymax = BondPad.ymin

        CCircuit.add_port(name='Cout', port=Cpout.ports['e1'])

    else:
        raise KeyError('Invalid Capacitor Type.')

    if num_layers == 3:
        #create invert layer
        if capacitor_type == 'PPC':
            CapacitorTPHole = CCircuit << gf.components.rectangle(size=(C.length - 2*tolerance, C.length - 2*tolerance), layer=LAYER.E0)
            CapacitorTPHole.xmin = GPlane.xmin + 2*tolerance
            CapacitorTPHole.ymin = GPlane.ymin + 2*tolerance
        elif capacitor_type == 'IDC':
            CapacitorTPHole = CCircuit << gf.components.rectangle(size=(C.width - 2*tolerance, C.base_height - 2*tolerance), layer=LAYER.E0)
            CapacitorTPHole.xmin = CCircuit.xmin + 2*tolerance
            CapacitorTPHole.ymin = CCircuit.ymin + 2*tolerance
    
    return CCircuit

@gf.cell
def LCGenerator_sim(via_pad_width,capacitor_type,num_layers) -> gf.Component:
    '''
    GENERATE SIMULATABLE LC CELL.
    '''
    
    global L
    global C
    L = InductorClass(num_layers)
    C = CapacitorClass(capacitor_type, num_layers, Frequency)
    
    #C component
    CCircuit = gf.Component() # initialize component
    
    if C.type == 'IDC':
        num_lines = C.finger_num

        # calculate size
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
    
    elif C.type == 'PPC':
        CCircuit = gf.Component() # initialize component

        GPlane = CCircuit << gf.components.rectangle((C.length + 2*tolerance,C.length + 2*tolerance), LAYER.GP) # ground plane
        GPlanehole = gf.components.rectangle((C.length + 2*tolerance,C.length + 2*tolerance), LAYER.E0) # ground plane hole

        Dielectric = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.D) # dieletric material
        Dielectric.movex(tolerance).movey(tolerance)

        TPlane = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.TP) # top plane
        TPlane.movex(tolerance).movey(tolerance)
        CPlane_low = CCircuit << gf.components.rectangle((C.length - 2*tolerance, C.length - 2*tolerance), LAYER.Bond3) # top plane
        CPlane_low.movex(2*tolerance).movey(2*tolerance)

        CCircuit.add_port(name='Cin', center=[TPlane.xmin + C.length/2, TPlane.ymin], orientation=270, width=TL_width, layer=LAYER.TP)
    
    else:
        raise KeyError('Invalid Capacitor Type.')
    
    # collect up
    LCCircuit = gf.Component()
    Inductor = LCCircuit << LGenerator(LAYER.GP)
    Capacitor = LCCircuit << CCircuit 
    
    # alignment
    Capacitor.xmin = Inductor.xmin
    Capacitor.ymax = Inductor.ymin - LC.gap
    ConnectingLine = LCCircuit << gf.components.rectangle(size=(TL_width, LC.gap), layer=LAYER.GP)
    ConnectingLine.xmin = Inductor.xmin
    ConnectingLine.ymin = Capacitor.ymax

    # L wire parameters
    pitch = L.line_width + L.gap_width # define pitch of inductor
    L_pad_gap = via_pad_width/2 + pitch #offset to create via
    i = L.num_turns # number of turns in coil
    
    # L wire
    if L.num_layers == 3:
        wire = LCCircuit << gf.components.rectangle(size=(L.line_width, L.outer_diameter - (L.outer_diameter - L.line_width - i*pitch  - L_pad_gap + L.line_width/2 + via_pad_width/2)), layer=LAYER.Bond2) # wire on Bond2 layer
        wire.movex(i*pitch + 4*L.line_width +  via_pad_width/2).movey(L.outer_diameter - L.line_width - i*pitch - L_pad_gap + via_pad_width/2)
        wire2 = LCCircuit << gf.components.rectangle(size=(L.line_width, 50*tolerance), layer=LAYER.Bond1) # wire on Bond1 layer
        wire2.xmin = wire.xmin
        wire2.ymin = wire.ymax
    elif L.num_layers == 1:
        pass
    else:
        raise KeyError('Invalid Number of Layers.')

    # suceed ports
    LCCircuit.add_port(name='Cin', port=Capacitor.ports['Cin'])

    # if num_layers == 3:
    #     #creat pads
    #     Pad = gf.components.rectangle((pad.width, pad.width), layer=LAYER.Top)

    #     Bias = LCCircuit << Pad
    #     Bias.xmin = Capacitor.xmin
    #     Bias.ymax = Capacitor.ymin - 50*tolerance

    #     TESin = LCCircuit << Pad
    #     TESin.xmin = Inductor.xmin
    #     TESin.ymin = Inductor.ymax - pad.width/2

    #     TESout = LCCircuit << Pad
    #     TESout.xmin = TESin.xmax + L.outer_diameter
    #     TESout.ymin = TESin.ymin

    #     SPad = LCCircuit << Pad
    #     SPad.xmin = TESout.xmin
    #     SPad.ymin = Bias.ymin
    #     LCCircuit.add_port(name='Biasout', center=[Bias.xmin + pad.width/2, Bias.ymax], orientation=90, width=TL_width, layer=LAYER.Top)

    #     #create wires
    #     BiasWire = gf.routing.get_route_electrical(LCCircuit.ports["Biasout"], LCCircuit.ports["Cin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
    #     LCCircuit.add(BiasWire.references)

    #     TESinWire = LCCircuit << gf.components.rectangle((L.num_turns*(L.line_width+L.gap_width) + 4.5*L.line_width + via_pad_width/2 - pad.width, TL_width), layer=LAYER.Top)
    #     TESinWire.xmin = TESin.xmax
    #     TESinWire.ymax = Inductor.ymax

    #     LCCircuit.add_port(name='TESoutPadout', center=[TESout.xmin + pad.width/2, TESout.ymin], orientation=270, width=TL_width, layer=LAYER.Top)
    #     LCCircuit.add_port(name='SPadin', center=[SPad.xmin + pad.width/2, SPad.ymax], orientation=90, width=TL_width, layer=LAYER.Top)
    #     GrondRoute = gf.routing.get_route_electrical(LCCircuit.ports["TESoutPadout"], LCCircuit.ports["SPadin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
    #     LCCircuit.add(GrondRoute.references)
    
    # Correct Top layer structures to fix the fabrication rule.
    TMvia = gf.Component() # via in top layer
    viahole_TM = TMvia << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance))
    viahole_TM.movex(tolerance).movey(tolerance)
    TMvia = LCCircuit << gf.geometry.boolean(gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Bond2), viahole_TM, 'not', layer=LAYER.Bond2) # sink the metal on top of the via hole.
    TMvia.movex(i*pitch + 4.5*L.line_width).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2)
    TMviaLow = LCCircuit << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance), layer=LAYER.Bond0) # sinked top metal.
    TMviaLow.movex(TMvia.xmin + tolerance).movey(TMvia.ymin + tolerance)

    # create SiO2layer on Base.
    SiO2layer = gf.Component() # initialize inverted layer
    Coilhole = SiO2layer << LGenerator(LAYER.E0) # copy inductor shape into SiO2 layer
    DielectricHole = SiO2layer << gf.components.rectangle((C.length, C.length))
    DielectricHole.movex(tolerance-L.line_width/2).movey(-C.length-LC.gap-tolerance)
    Capacitorhole = SiO2layer << GPlanehole # copy capacitor shape into SiO2 layer
    Capacitorhole.xmin = Inductor.xmin
    Capacitorhole.ymax = Inductor.ymin - LC.gap
    ConnectingLinehole = SiO2layer << gf.components.rectangle(size=(TL_width, LC.gap), layer=LAYER.GP)
    ConnectingLinehole.xmin = Inductor.xmin
    ConnectingLinehole.ymin = Capacitor.ymax

    SiO2onBase = LCCircuit << gf.geometry.invert(SiO2layer,border=BoardSize,layer=LAYER.E0) # Make it as inverted layer.

    # Create SiO2layer on Coil and Capacitor Ground pad
    SiO2onCoil = gf.Component()
    Coil = LGenerator(LAYER.E1) # copy capacitor shape into SiO2 layer
    viahole = SiO2onCoil << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance)) # holeshape in dielectric layer
    viahole.movex(TMvia.xmin + tolerance).movey(TMvia.ymin + tolerance)
    SiO2onCoil = LCCircuit << gf.geometry.boolean(Coil,viahole,'not',layer=LAYER.E1) # Give out the SiO2 layer on Coil
    
    SiO2onCapacitorGP = gf.Component()
    CapacitorGPShape = SiO2onCapacitorGP << gf.components.rectangle(size=(C.length + 2*tolerance, C.length + 2*tolerance))
    CapacitorTPShape = SiO2onCapacitorGP << gf.components.rectangle(size=(C.length, C.length))
    CapacitorTPShape.move([tolerance, tolerance])
    SiO2onCapacitorGP = LCCircuit << gf.geometry.boolean(CapacitorGPShape, CapacitorTPShape, 'not', layer=LAYER.E1) # Create SiO2 layer on naked Capacitor GP.
    SiO2onCapacitorGP.xmin = Capacitor.xmin
    SiO2onCapacitorGP.ymin = Capacitor.ymin

    SiO2onCL = LCCircuit << gf.components.rectangle(size=(TL_width, LC.gap), layer=LAYER.E1)
    SiO2onCL.xmin = Inductor.xmin
    SiO2onCL.ymin = Capacitor.ymax

    #Create SiO2 on Capacitor Top Pad
    SiO2onCapacitorTP = gf.Component()
    CapacitorTPShape = SiO2onCapacitorTP << gf.components.rectangle(size=(C.length, C.length))
    CapacitorTPHole = SiO2onCapacitorTP << gf.components.rectangle(size=(C.length - 2*tolerance, C.length - 2*tolerance))
    CapacitorTPHole.move([tolerance, tolerance])
    SiO2onCapacitorTP = LCCircuit << gf.geometry.boolean(CapacitorTPShape, CapacitorTPHole, 'not', layer=LAYER.E2) # Create SiO2 layer on naked Capacitor GP.
    SiO2onCapacitorTP.xmin = Capacitor.xmin + tolerance
    SiO2onCapacitorTP.ymin = Capacitor.ymin + tolerance

    return LCCircuit

@gf.cell
def LCGenerator(via_pad_width,capacitor_type,num_layers,Frequency,ratio_division) -> gf.Component:
    ''' 
    GENERATE LC CELL.
    '''

    global L
    global C
    L = InductorClass(num_layers)
    if ratio_division == None:
        LCCircuit = gf.Component()
        Inductor = LCCircuit << LGenerator(layer=LAYER.GP)
        FC = LCCircuit << CGenerator(via_pad_width,capacitor_type,num_layers,Frequency)
        
        # alignment
        FC.xmin = Inductor.xmin
        FC.ymax = Inductor.ymin - LC.gap

        # suceed ports
        LCCircuit.add_port(name='FCin', port=FC.ports['Cin'])
        LCCircuit.add_port(name='FCout', port=FC.ports['Cout'])
        LCCircuit.add_port(name='Lin', port=Inductor.ports['Lin'])
        LCCircuit.add_port(name='Lout', port=Inductor.ports['Lout'])

        # connecting
        ConnectingPadT = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[1], ConnectingPadSize[1]), layer=LAYER.Bond0)
        ConnectingPadT.xmax = LCCircuit.ports['Lout'].x + via_pad_width/2
        ConnectingPadT.ymin = LCCircuit.ports['FCin'].y + (LC.gap - ConnectingPadSize[1])/2
        
        ConnectingPadB = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[1] + tolerance, ConnectingPadSize[1] + tolerance), layer=LAYER.GP)
        ConnectingPadB.xmax = ConnectingPadT.xmax + tolerance/2
        ConnectingPadB.ymin = ConnectingPadT.ymin - tolerance/2

        ConnectingPadHole = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[1] - tolerance, ConnectingPadSize[1] - tolerance), layer=LAYER.E0)
        ConnectingPadHole.xmin = ConnectingPadT.xmin + tolerance/2
        ConnectingPadHole.ymin = ConnectingPadT.ymin + tolerance/2
        
        Padin = LCCircuit << gf.components.optimal_step(start_width=TL_width - tolerance/2, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(-90)
        Padin.xmax = ConnectingPadT.xmax
        Padin.ymin = ConnectingPadT.ymax
        LCCircuit.add_port(name='Padin', port=Padin.ports['e1'])

        PadoutFC = LCCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.GP, anticrowding_factor=0.5)
        PadoutFC.xmax = ConnectingPadB.xmin
        PadoutFC.ymin = ConnectingPadB.ymin
        LCCircuit.add_port(name='PadoutFC', port=PadoutFC.ports['e1'])

        if LCCircuit.ports['PadoutFC'].x - (ConnectingPadSize[0]-ConnectingPadSize[1]-via_pad_width/2-PadoutFC.xsize) != LCCircuit.ports['FCin'].x:
            FC.movex(LCCircuit.ports['PadoutFC'].x - (ConnectingPadSize[0]-ConnectingPadSize[1]-via_pad_width/2-PadoutFC.xsize) - LCCircuit.ports['FCin'].x)
            LCCircuit.ports['FCin'].x = LCCircuit.ports['PadoutFC'].x - (ConnectingPadSize[0]-ConnectingPadSize[1]-via_pad_width/2-PadoutFC.xsize)
            LCCircuit.ports['FCout'].x = LCCircuit.ports['PadoutFC'].x - (ConnectingPadSize[0]-ConnectingPadSize[1]-via_pad_width/2-PadoutFC.xsize)

        L2Pad = gf.routing.get_route_electrical(LCCircuit.ports["Padin"], LCCircuit.ports["Lout"], bend="bend_euler", radius=10, layer=LAYER.Bond0, width=TL_width - tolerance/2)
        LCCircuit.add(L2Pad.references)
        Pad2FC = gf.routing.get_route_electrical(LCCircuit.ports["PadoutFC"], LCCircuit.ports["FCin"], bend="bend_euler", radius=10, layer=LAYER.GP, width=TL_width)
        LCCircuit.add(Pad2FC.references)

    else:
        try:
            ratio_division = np.array(ratio_division)

            # construct L and C components
            LCCircuit = gf.Component()
            Inductor = LCCircuit << LGenerator(layer=LAYER.GP)
            CC = LCCircuit << CGenerator(via_pad_width,capacitor_type,num_layers,Frequency,ratio_division[0]/ratio_division.sum())
            FC = LCCircuit << CGenerator(via_pad_width,capacitor_type,num_layers,Frequency,ratio_division[1]/ratio_division.sum())
        except:
            raise KeyError('Please input the ratio_division as a list of two elements.')
    
        # alignment
        FC.xmin = Inductor.xmin
        CC.rotate(-90)
        CC.xmax = Inductor.xmax
        CC.ymax = Inductor.ymin - LC.gap
        FC.ymax = CC.ymin - LC.gap

        # suceed ports
        LCCircuit.add_port(name='FCin', port=FC.ports['Cin'])
        LCCircuit.add_port(name='FCout', port=FC.ports['Cout'])
        LCCircuit.add_port(name='CCin', port=CC.ports['Cin'])
        LCCircuit.add_port(name='CCout', port=CC.ports['Cout'])
        LCCircuit.add_port(name='Lin', port=Inductor.ports['Lin'])
        LCCircuit.add_port(name='Lout', port=Inductor.ports['Lout'])

        # connecting
        ConnectingPadT = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[0], ConnectingPadSize[1]), layer=LAYER.Bond0)
        ConnectingPadT.xmax = LCCircuit.ports['Lout'].x + via_pad_width/2
        ConnectingPadT.ymin = LCCircuit.ports['CCin'].y - ConnectingPadSize[1]/2
        
        ConnectingPadB = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[0] + tolerance, ConnectingPadSize[1] + tolerance), layer=LAYER.GP)
        ConnectingPadB.xmax = ConnectingPadT.xmax + tolerance/2
        ConnectingPadB.ymin = ConnectingPadT.ymin - tolerance/2

        ConnectingPadHole = LCCircuit << gf.components.rectangle(size=(ConnectingPadSize[0] - tolerance, ConnectingPadSize[1] - tolerance), layer=LAYER.E0)
        ConnectingPadHole.xmin = ConnectingPadT.xmin + tolerance/2
        ConnectingPadHole.ymin = ConnectingPadT.ymin + tolerance/2
        
        Padin = LCCircuit << gf.components.optimal_step(start_width=TL_width - tolerance/2, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(-90)
        Padin.xmax = ConnectingPadT.xmax
        Padin.ymin = ConnectingPadT.ymax
        LCCircuit.add_port(name='Padin', port=Padin.ports['e1'])

        PadoutFC = LCCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.GP, anticrowding_factor=0.5).rotate(90)
        PadoutFC.xmin = ConnectingPadB.xmin
        PadoutFC.ymax = ConnectingPadB.ymin
        LCCircuit.add_port(name='PadoutFC', port=PadoutFC.ports['e1'])

        PadoutCC = LCCircuit << gf.components.optimal_step(start_width=ConnectingPadSize[1], end_width=TL_width - tolerance/2, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=1)
        PadoutCC.xmin = ConnectingPadT.xmax
        PadoutCC.ymin = ConnectingPadT.ymin
        LCCircuit.add_port(name='PadoutCC', port=PadoutCC.ports['e2'])

        if LCCircuit.ports['PadoutFC'].x != LCCircuit.ports['FCin'].x:
            FC.movex(LCCircuit.ports['PadoutFC'].x - LCCircuit.ports['FCin'].x)
            LCCircuit.ports['FCin'].x = LCCircuit.ports['PadoutFC'].x
            LCCircuit.ports['FCout'].x = LCCircuit.ports['PadoutFC'].x

        L2Pad = gf.routing.get_route_electrical(LCCircuit.ports["Padin"], LCCircuit.ports["Lout"], bend="bend_euler", radius=10, layer=LAYER.Bond0, width=TL_width - tolerance/2)
        LCCircuit.add(L2Pad.references)
        Pad2FC = gf.routing.get_route_electrical(LCCircuit.ports["PadoutFC"], LCCircuit.ports["FCin"], bend="bend_euler", radius=10, layer=LAYER.GP, width=TL_width)
        LCCircuit.add(Pad2FC.references)
        Pad2CC = gf.routing.get_route_electrical(LCCircuit.ports["PadoutCC"], LCCircuit.ports["CCout"], bend="bend_euler", radius=10, layer=LAYER.Bond0, width=TL_width - tolerance/2)
        LCCircuit.add(Pad2CC.references)

    return LCCircuit