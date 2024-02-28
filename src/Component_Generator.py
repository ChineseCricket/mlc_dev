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
tolerance = 5 # General tolerance
boundary = BoundaryClass()
num_layers = 1 # number of layers used in this design
# capacitor_type = "PPC" # type of capacitor (PPC or IDC)
BoardSize = 500 # size of the board
Frequency = 1e6 # capacity of the capacitor

#WIRING PARAMETERS
chip = Chip()
TL_width = chip.TL_width # width of transmission line
wire2wire_space = chip.wire2wire_space # space between wires
wiring_gap = chip.wiring_gap # for the corners

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
    GPvia = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=layer) # via in ground plane layer
    GPvia.movex(L.outer_diameter - i*pitch - L.line_width - via_pad_width - tolerance).movey(L.outer_diameter - i*pitch - L.line_width - via_pad_width - tolerance) # move via to correct position
    GPviapin = LCircuit << gf.components.optimal_step(start_width=L.line_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=layer)
    GPviapin.xmax = GPvia.xmin
    GPviapin.ymin = GPvia.ymin

    CoilPath += [(i*pitch, GPvia.ymin + via_pad_width/2)] # add final near full length up path
    CoilPath += [(GPviapin.xmin, GPvia.ymin + via_pad_width/2)] # add small horizontal path 

    CoilPath = gf.path.smooth(points=CoilPath, radius=10) # create path object for inductor
    Coil = LCircuit << gf.path.extrude(CoilPath, layer=layer, width=L.line_width) # extrude path to create inductor

    LCircuit.add_port(name='Coilin', center=[0,L.outer_diameter/2], orientation=270, width=L.line_width, layer=layer) # add port to inductor

    return LCircuit

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

        viahole = gf.components.rectangle(size = (TL_width,TL_width), layer=LAYER.E0)

        vh1 = LCircuit << viahole
        vh1.movex(L.outer_diameter - i*pitch - L.line_width - via_pad_width).movey(L.outer_diameter - i*pitch - L.line_width - via_pad_width)

        vh2 = LCircuit << viahole
        vh2.movex(L.outer_diameter - i*pitch - L.line_width - via_pad_width + L.gap_width).movey(L.outer_diameter - i*pitch - L.line_width - via_pad_width).rotate(-90)

        viapad = gf.components.rectangle(size = (via_pad_width,via_pad_width), layer=LAYER.TP)

        vp1 = LCircuit << viapad
        vp1.xmax = vh1.xmax+tolerance
        vp1.ymax = vh1.ymax+tolerance

        vp2 = LCircuit << viapad
        vp2.xmax = vh2.xmax+tolerance
        vp2.ymax = vh2.ymax+tolerance

        Pad2TL = gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.TP).rotate(90)

        pt1 = LCircuit << Pad2TL
        pt1.xmax = vp1.xmax
        pt1.ymax = vp1.ymin

        pt2 = LCircuit << Pad2TL
        pt2.rotate(180)
        pt2.ymin = vp2.ymax
        pt2.xmax = vp2.xmax

        LCircuit.add_port(name='TL0', port=pt1.ports['e1'])
        LCircuit.add_port(name='TL1', port=pt2.ports['e1'])
        
        Connecting14 = gf.routing.get_route_electrical(LCircuit.ports["TL0"], LCircuit.ports["TL1"], bend="bend_euler", radius=10, layer=LAYER.TP, width=TL_width)
        LCircuit.add(Connecting14.references)

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
def LCGenerator(via_pad_width,capacitor_type,num_layers) -> gf.Component:
    ''' 
    GENERATE LC CELL.
    '''

    global L
    global C
    L = InductorClass(num_layers)
    C = CapacitorClass(capacitor_type, num_layers, Frequency)

    #C component
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

        BondPad = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.Bond0) # dieletric material
        BondPad.movex(tolerance).movey(tolerance)

        TPlane = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.TP) # top plane
        TPlane.movex(tolerance).movey(tolerance)

        CCircuit.add_port(name='Cin', center=[TPlane.xmin + C.length/2, TPlane.ymin], orientation=270, width=TL_width, layer=LAYER.Bond0)
    
    else:
        raise KeyError('Invalid Capacitor Type.')
    
    # collect up
    LCCircuit = gf.Component()
    Inductor = LCCircuit << LGenerator(layer=LAYER.GP)
    LCCircuit.add_port(name='Coilin', port=Inductor.ports['Coilin'])
    Capacitor = LCCircuit << CCircuit
    
    # alignment and connection
    Capacitor.xmin = Inductor.xmin
    Capacitor.ymax = Inductor.ymin - LC.gap
    ConnectingLine = LCCircuit << gf.components.optimal_step(start_width=L.line_width, end_width=TL_width, num_pts=50, layer=LAYER.GP).rotate(-90)
    ConnectingLine.xmin = Inductor.xmin
    ConnectingLine.ymin = Capacitor.ymax
    LCCircuit.add_port(name='ConnectingLineout', center=[ConnectingLine.xmin + L.line_width/2, ConnectingLine.ymax], orientation=90, width=L.line_width, layer=LAYER.GP)
    LCconnecting = gf.routing.get_route_electrical(LCCircuit.ports["Coilin"], LCCircuit.ports["ConnectingLineout"], bend="bend_euler", radius=10, layer=LAYER.GP, width=L.line_width)
    LCCircuit.add(LCconnecting.references)

    # L wire parameters
    pitch = L.line_width + L.gap_width # define pitch of inductor
    L_pad_gap = via_pad_width/2 + pitch #offset to create via
    i = L.num_turns # number of turns in coil
    
    # L wire
    if L.num_layers == 3:
        ViaPadBond = LCCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Bond0) # via pad on Bond layer
        ViaPadBond.movex(L.outer_diameter - i*pitch - L.line_width - via_pad_width - tolerance).movey(L.outer_diameter - i*pitch - L.line_width - via_pad_width - tolerance)
        ViaPadBondpin = LCCircuit << gf.components.optimal_step(start_width=TL_width, end_width=via_pad_width, num_pts=100, symmetric=True, layer=LAYER.Bond0).rotate(-90)
        ViaPadBondpin.xmax = ViaPadBond.xmax
        ViaPadBondpin.ymin = ViaPadBond.ymax

        LCCircuit.add_port(name='ViaPadBondpin', center=[ViaPadBondpin.xmin + via_pad_width/2, ViaPadBondpin.ymax], orientation=90, width=TL_width, layer=LAYER.Bond0)
    elif L.num_layers == 1:
        pass
    else:
        raise KeyError('Invalid Number of Layers.')

    # suceed ports
    LCCircuit.add_port(name='Cin', port=Capacitor.ports['Cin'])

    if num_layers == 3:
        #creat pads
        OutPad = gf.components.rectangle((pad.width0, pad.width0), layer=LAYER.Bond0)
        TESPad = gf.components.rectangle((pad.length1, pad.width1), layer=LAYER.Bond0)

        Bias = LCCircuit << OutPad
        Bias.xmin = 0
        Bias.ymax = 3000
        Biaspin = LCCircuit << gf.components.optimal_step(start_width=TL_width, end_width=pad.width0, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(180)
        Biaspin.xmin = Bias.xmax
        Biaspin.ymin = Bias.ymin
        LCCircuit.add_port(name='Biasout', center=[Biaspin.xmax, Biaspin.ymax - pad.width0/2], orientation=0, width=TL_width, layer=LAYER.Bond0)

        TESin = LCCircuit << TESPad
        TESin.xmin = Inductor.xmin - 2*pad.length1
        # TESin.ymin = Inductor.ymax - pad.width1/2 + 50*tolerance
        TESinpin = LCCircuit << gf.components.optimal_step(start_width=TL_width, end_width=pad.width1, num_pts=100, symmetric=False, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(180)
        TESinpin.xmin = TESin.xmax
        TESinpin.ymax = TESin.ymax
        LCCircuit.add_port(name='TESinpin', center=[TESinpin.xmax, TESinpin.ymax - TL_width/2], orientation=0, width=TL_width, layer=LAYER.Bond0)

        TESout = LCCircuit << TESPad
        TESout.xmin = TESin.xmin
        TESout.ymin = TESin.ymax + pad.spacing
        TESoutpin = LCCircuit << gf.components.optimal_step(start_width=pad.width1, end_width=TL_width, num_pts=100, symmetric=False, layer=LAYER.Bond0, anticrowding_factor=0.5)
        TESoutpin.xmin = TESout.xmax
        TESoutpin.ymax = TESout.ymax
        LCCircuit.add_port(name='TESoutPadout', center=[TESoutpin.xmax, TESoutpin.ymin+TL_width/2], orientation=0, width=TL_width, layer=LAYER.Bond0)

        SPad = LCCircuit << OutPad
        SPad.xmin = 0
        SPad.ymin = 3050
        SPadpin = LCCircuit << gf.components.optimal_step(start_width=pad.width0, end_width=TL_width, num_pts=100, symmetric=True, layer=LAYER.Bond0, anticrowding_factor=0.5).rotate(0)
        SPadpin.xmin = SPad.xmax
        SPadpin.ymin = SPad.ymin
        LCCircuit.add_port(name='SPadin', center=[SPadpin.xmax, SPadpin.ymin + pad.width0/2], orientation=0, width=TL_width, layer=LAYER.Bond0)
        
        #create wires
        BiasWire = gf.routing.get_route_electrical(LCCircuit.ports["Biasout"], LCCircuit.ports["Cin"], layer=LAYER.Bond0, with_sbend=True, radius=30, width=TL_width, bend='bend_euler')
        LCCircuit.add(BiasWire.references)

        TESinWire = gf.routing.get_route_electrical(LCCircuit.ports["TESinpin"], LCCircuit.ports["ViaPadBondpin"], bend="bend_euler", radius = 30, layer=LAYER.Bond0)
        LCCircuit.add(TESinWire.references)

        GrondRoute = gf.routing.get_route_electrical(LCCircuit.ports["TESoutPadout"], LCCircuit.ports["SPadin"], bend="bend_euler", radius = 30, layer=LAYER.Bond0)
        LCCircuit.add(GrondRoute.references)

        #create invert layer
        if capacitor_type == 'PPC':
            CapacitorTPHole = LCCircuit << gf.components.rectangle(size=(C.length - 2*tolerance, C.length - 2*tolerance), layer=LAYER.E0)
            CapacitorTPHole.xmin = Capacitor.xmin + 2*tolerance
            CapacitorTPHole.ymin = Capacitor.ymin + 2*tolerance
        elif capacitor_type == 'IDC':
            CapacitorTPHole = LCCircuit << gf.components.rectangle(size=(C.width - 2*tolerance, C.base_height - 2*tolerance), layer=LAYER.E0)
            CapacitorTPHole.xmin = Capacitor.xmin + tolerance
            CapacitorTPHole.ymin = Capacitor.ymin + tolerance
        viahole = LCCircuit << gf.components.rectangle(size=(via_pad_width - tolerance, via_pad_width - tolerance), layer=LAYER.E0)
        viahole.xmin = ViaPadBond.xmin + tolerance/2
        viahole.ymin = ViaPadBond.ymin + tolerance/2
        
    
    return LCCircuit