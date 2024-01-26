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
BoardSize = 500 # size of the board

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



def LGenerator(layer) -> gf.Component:
    '''
    Generate L Component for GP layer and SiO2 layer.
    '''
    #L Component
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
    
    CoilPath += [(i*pitch, L.outer_diameter - L.line_width - i*pitch - L_pad_gap)] # add final near full length up path
    CoilPath += [(i*pitch + 4.5*L.line_width, L.outer_diameter - L.line_width - i*pitch - L_pad_gap)] # add small horizontal path 

    CoilPath = gf.Path(CoilPath) # create path object for inductor
    Coil = LCircuit << gf.path.extrude(CoilPath, layer=layer, width=L.line_width) # extrude path to create inductor

    GPvia = LCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=layer) # via in ground plane layer
    GPvia.movex(i*pitch + 4.5*L.line_width).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2)

    return LCircuit



@gf.cell
def LCGenerator_sim(via_pad_width,capacitor_type,num_layers) -> gf.Component:
    '''
    GENERATE SIMULATABLE LC CELL.
    '''
    
    global L
    global C
    L = InductorClass(num_layers)
    C = CapacitorClass(capacitor_type, num_layers)
    
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

        CCircuit.add_port(name='PPCin', center=[TPlane.xmin + C.length/2, TPlane.ymin], orientation=270, width=TL_width, layer=LAYER.TP)
    
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
    LCCircuit.add_port(name='PPCin', port=Capacitor.ports['PPCin'])

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

    #     GPad = LCCircuit << Pad
    #     GPad.xmin = TESout.xmin
    #     GPad.ymin = Bias.ymin
    #     LCCircuit.add_port(name='Biasout', center=[Bias.xmin + pad.width/2, Bias.ymax], orientation=90, width=TL_width, layer=LAYER.Top)

    #     #create wires
    #     BiasWire = gf.routing.get_route_electrical(LCCircuit.ports["Biasout"], LCCircuit.ports["PPCin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
    #     LCCircuit.add(BiasWire.references)

    #     TESinWire = LCCircuit << gf.components.rectangle((L.num_turns*(L.line_width+L.gap_width) + 4.5*L.line_width + via_pad_width/2 - pad.width, TL_width), layer=LAYER.Top)
    #     TESinWire.xmin = TESin.xmax
    #     TESinWire.ymax = Inductor.ymax

    #     LCCircuit.add_port(name='TESoutPadout', center=[TESout.xmin + pad.width/2, TESout.ymin], orientation=270, width=TL_width, layer=LAYER.Top)
    #     LCCircuit.add_port(name='GPadin', center=[GPad.xmin + pad.width/2, GPad.ymax], orientation=90, width=TL_width, layer=LAYER.Top)
    #     GrondRoute = gf.routing.get_route_electrical(LCCircuit.ports["TESoutPadout"], LCCircuit.ports["GPadin"], bend="bend_euler", radius = 30, layer=LAYER.Top)
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
    C = CapacitorClass(capacitor_type, num_layers)

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

        BondPad = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.Bond0) # dieletric material
        BondPad.movex(tolerance).movey(tolerance)

        TPlane = CCircuit << gf.components.rectangle((C.length, C.length), LAYER.TP) # top plane
        TPlane.movex(tolerance).movey(tolerance)

        CCircuit.add_port(name='PPCin', center=[TPlane.xmin + C.length/2, TPlane.ymin], orientation=270, width=TL_width, layer=LAYER.Bond0)
    
    else:
        raise KeyError('Invalid Capacitor Type.')
    
    # collect up
    LCCircuit = gf.Component()
    Inductor = LCCircuit << LGenerator(layer=LAYER.GP)
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
        wire = LCCircuit << gf.components.rectangle(size=(L.line_width, L.outer_diameter - (L.outer_diameter - L.line_width - i*pitch  - L_pad_gap + L.line_width/2 + via_pad_width/2) + 50*tolerance), layer=LAYER.Bond0) # wire on Bond layer
        wire.movex(i*pitch + 4*L.line_width +  via_pad_width/2).movey(L.outer_diameter - L.line_width - i*pitch - L_pad_gap + via_pad_width/2)
        ViaPadBond = LCCircuit << gf.components.rectangle(size=(via_pad_width, via_pad_width), layer=LAYER.Bond0) # via pad on Bond layer
        ViaPadBond.movex(i*pitch + 4.5*L.line_width).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2)
    elif L.num_layers == 1:
        pass
    else:
        raise KeyError('Invalid Number of Layers.')

    # suceed ports
    LCCircuit.add_port(name='PPCin', port=Capacitor.ports['PPCin'])

    if num_layers == 3:
        #creat pads
        Pad = gf.components.rectangle((pad.width, pad.width), layer=LAYER.Bond0)

        Bias = LCCircuit << Pad
        Bias.xmin = Capacitor.xmin
        Bias.ymax = Capacitor.ymin - 50*tolerance

        TESin = LCCircuit << Pad
        TESin.xmin = Inductor.xmin
        TESin.ymin = Inductor.ymax - pad.width/2 + 50*tolerance

        TESout = LCCircuit << Pad
        TESout.xmin = TESin.xmax + L.outer_diameter
        TESout.ymin = TESin.ymin

        GPad = LCCircuit << Pad
        GPad.xmin = TESout.xmin
        GPad.ymin = Bias.ymin
        LCCircuit.add_port(name='Biasout', center=[Bias.xmin + pad.width/2, Bias.ymax], orientation=90, width=TL_width, layer=LAYER.Bond0)

        #create wires
        BiasWire = gf.routing.get_route_electrical(LCCircuit.ports["Biasout"], LCCircuit.ports["PPCin"], bend="bend_euler", radius = 30, layer=LAYER.Bond0)
        LCCircuit.add(BiasWire.references)

        TESinWire = LCCircuit << gf.components.rectangle((L.num_turns*(L.line_width+L.gap_width) + 4.5*L.line_width + via_pad_width/2 - pad.width, TL_width), layer=LAYER.Bond0)
        TESinWire.xmin = TESin.xmax
        TESinWire.ymax = Inductor.ymax + 50*tolerance

        LCCircuit.add_port(name='TESoutPadout', center=[TESout.xmin + pad.width/2, TESout.ymin], orientation=270, width=TL_width, layer=LAYER.Bond0)
        LCCircuit.add_port(name='GPadin', center=[GPad.xmin + pad.width/2, GPad.ymax], orientation=90, width=TL_width, layer=LAYER.Bond0)
        GrondRoute = gf.routing.get_route_electrical(LCCircuit.ports["TESoutPadout"], LCCircuit.ports["GPadin"], bend="bend_euler", radius = 10, layer=LAYER.Bond0)
        LCCircuit.add(GrondRoute.references)

        #create invert layer
        CapacitorTPHole = LCCircuit << gf.components.rectangle(size=(C.length - 2*tolerance, C.length - 2*tolerance), layer=LAYER.E0)
        CapacitorTPHole.xmin = Capacitor.xmin + 2*tolerance
        CapacitorTPHole.ymin = Capacitor.ymin + 2*tolerance
        viahole = LCCircuit << gf.components.rectangle(size=(via_pad_width - 2*tolerance, via_pad_width - 2*tolerance), layer=LAYER.E0)
        viahole.movex(i*pitch + 4.5*L.line_width + tolerance).movey((L.outer_diameter - L.line_width - i*pitch) - L_pad_gap - via_pad_width/2 + tolerance)
        
    
    return LCCircuit