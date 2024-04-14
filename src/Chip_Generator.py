import gdsfactory as gf
import numpy as np
from functools import partial
from math import *

from Parameters_Classes import *
from Layer_Definition import *
from Component_Generator import *

# ---------------------- GLOBAL CONSTANTS --------------------------
#Initialize GENERAL PARAMETERS
font_size = 400
x0 = 0
y0 = 0
via_pad_width = 20 # Size of via pads for capacitor and inductor to change metal plane 
tolerance = 4 # General tolerance
num_layers = 1 # number of layers used in this design
# capacitor_type = "PPC" # type of capacitor (PPC or IDC)
Frequency = 1e6 # capacity of the capacitor

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
def WaferCircle(Diameter_inch) -> gf.Component:
    '''
    Creates a new wafer circle.
    '''
    # Create a new component
    Wafer = gf.Component()
    # Calculate wafer radius
    Radius_microns = Diameter_inch/2 * 2.54/100 * 1e6 
    # Create wafer
    WaferCircle = Wafer << gf.components.circle(radius=Radius_microns, layer=LAYER.WAFER)
    return Wafer

@gf.cell
def newCArray(via_pad_width,Ctype,num_layers,num_column,num_row,Frequencies) -> gf.Component:
    '''
    Creates a new array of Cs.
    '''
    # Create a new component
    Array = gf.Component()
    
    # Create frame of LCs
    SingleCell = gf.components.rectangle(size=(chip.CellWidth, chip.CellHeight), layer=LAYER.Frame)
    CellFrame = Array.add_array(SingleCell, columns=num_column, rows=num_row, spacing=[chip.CellWidth, chip.CellHeight])
    
    # Create Pads
    Space_Pad = chip.CellHeight*num_row/(num_column*num_row)
    
    TPad = gf.Component()
    TPadself = TPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.Bond0)
    TPadin = TPad << gf.components.optimal_step(start_width=pad.width0/2, end_width=TL_width-tolerance/2, num_pts=100, layer=LAYER.Bond0, anticrowding_factor=0.1)
    TPadin.xmin = TPadself.xmax
    
    GPad = gf.Component()
    GPadself = GPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.GP)
    GPadin = GPad << gf.components.optimal_step(start_width=TL_width, end_width=pad.width0/2, num_pts=100, layer=LAYER.GP, anticrowding_factor=0.1).rotate(180)
    GPadin.xmin = GPadself.xmax
    GPadin.ymin = GPadself.ymin

    # Create Array
    LCs = []
    TPads = []
    GPads = []
    R = [0 for i in range(num_row)]
    for j in range(num_row):
        # Create LCs
        R[j] = gf.Component()
        for i in range(num_column):
            LCs.append(R[j].add_ref(CGenerator(via_pad_width,Ctype,num_layers,Frequencies[num_row-j-1][i])))
            # LC.movex(L.outer_diameter)
            LCs[5*j+i].xmin = i*chip.CellWidth
            LCs[5*j+i].ymin = j*chip.CellHeight
            R[j].add_port(name = 'Cin'+str(j)+str(i), port = LCs[5*j+i].ports['Cin'])
            R[j].add_port(name = 'Cout'+str(j)+str(i), port = LCs[5*j+i].ports['Cout'])
        Array << R[j]

        # Create Pads Arrays
        TPads.append(Array.add_array(TPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
        TPads[j].xmax = CellFrame.xmin - TL_width*2*num_row - pad.width0
        TPads[j].ymin = CellFrame.ymin + j*chip.CellHeight + pad.width0/2 + 100
        for i in range(num_column): # Add ports to pads
            Array.add_port(name = 'TPad' + str(j) + str(i), center=(TPads[j].xmax, TPads[j].ymax - i*Space_Pad - pad.width0/2 - tolerance/4 + TL_width/2), width=TL_width-tolerance, orientation=0, layer=LAYER.Bond0)
        
        GPads.append(Array.add_array(GPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
        GPads[j].xmax = CellFrame.xmin - TL_width*2*num_row - pad.width0
        GPads[j].ymin = CellFrame.ymin + j*chip.CellHeight
        for i in range(num_column): # Add ports to pads
            Array.add_port(name = 'GPad' + str(j) + str(i), center=(GPads[j].xmax, GPads[j].ymax - i*Space_Pad - TL_width/2), width=TL_width, orientation=0, layer=LAYER.GP)
        
        # Routing to Pads
        Troutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0].startswith('TPad'+str(j)) ], [x[1] for x in R[j].ports.items() if x[0].startswith('Cout'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width-tolerance/2, layer = LAYER.Bond0, separation=TL_width*2,
            steps=[
                {"dx": pad.width0/2, "dy": 0},
                {"dx": 0, "y":R[j].ymin - num_column*2*TL_width - chip.wire_corner_radius},
                {"x":R[j].ports['Cin'+str(j)+'0'].center[0], "dy":0},
            ],
        )
        for route in Troutes:
            Array.add(route.references)
        
        Groutes = []
        for i in range(num_column):
            Groutes.append(gf.routing.get_route_from_steps(Array.ports['GPad'+str(j)+str(i)], R[j].ports['Cin'+str(j)+str(i)], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width, layer = LAYER.GP,
                steps=[
                    {"dx": pad.width0/2 + (num_column-i-1)*2*TL_width, "dy": 0},
                    {"dx": 0, "y": R[j].ymin - (i+1)*2*TL_width - chip.wire_corner_radius},
                    {"x": LCs[5*j+i].xmax+chip.wire_corner_radius, "dy": 0},
                    {"dx" :0, "y": LCs[5*j+i].ymax+chip.wire_corner_radius},
                    {"x": R[j].ports['Cout'+str(j)+str(i)].center[0], "dy": 0},
                ],
            ))
        for route in Groutes:
            Array.add(route.references)

    #Add Bonding Pads and Holes for GPads
    GPadhole = gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0/2 - 2*tolerance), layer=LAYER.E0)
    GPadholes = Array.add_array(GPadhole, columns=1, rows=num_pads, spacing=[0,Space_Pad])
    GPadholes.ymin = GPads[0].ymin + tolerance
    GPadholes.xmin = GPads[0].xmin + tolerance

    GPadBondings = Array.add_array(gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.Bond0), columns=1, rows=num_pads, spacing=[0,Space_Pad])
    GPadBondings.ymin = GPads[0].ymin
    GPadBondings.xmin = GPads[0].xmin

    # Create etched edge for array
    Edge = Array << gf.geometry.outline(gf.components.rectangle(size=(Array.xsize + 250, Array.ysize + 250)), distance=75, layer=LAYER.E0)
    Edge.xmin = Array.xmin - 200
    Edge.ymin = Array.ymin - 200

    Coner = gf.Component()
    Coner.add_polygon([(0,0), (50,0), (50,450), (500,450), (500,500), (0,500)], layer=LAYER.GP)
    
    C1 = Array << Coner
    C2 = Array << Coner
    C3 = Array << Coner
    C4 = Array << Coner

    C1.xmin = Edge.xmin + 25
    C1.ymax = Edge.ymax - 25
    C2.rotate(-90)
    C2.xmax = Edge.xmax - 25
    C2.ymax = Edge.ymax - 25
    C3.rotate(90)
    C3.xmin = Edge.xmin + 25
    C3.ymin = Edge.ymin + 25
    C4.rotate(180)
    C4.xmax = Edge.xmax - 25
    C4.ymin = Edge.ymin + 25

    EdgeCenterY = gf.components.rectangle(size = (50, Array.ysize/20), layer=LAYER.GP)
    EdgeCenterX = gf.components.rectangle(size = (Array.xsize/20, 50), layer=LAYER.GP)
    
    EY1 = Array << EdgeCenterY
    EY2 = Array << EdgeCenterY
    EX1 = Array << EdgeCenterX
    EX2 = Array << EdgeCenterX

    EY1.xmin = Edge.xmin + 25
    EY1.ymin = Edge.ymin + Edge.ysize/2 - EY1.ysize/2
    EY2.xmax = Edge.xmax - 25
    EY2.ymin = Edge.ymin + Edge.ysize/2 - EY2.ysize/2
    EX1.ymax = Edge.ymax
    EX1.xmin = Edge.xmin + Edge.xsize/2 - EX1.xsize/2
    EX2.ymin = Edge.ymin + 25
    EX2.xmin = Edge.xmin + Edge.xsize/2 - EX2.xsize/2

    return Array 

@gf.cell
def newArray(via_pad_width,Ctype,num_layers,num_column,num_row,Frequencies,ratio_division) -> gf.Component:
    '''
    Creates a new array of LCs.
    '''
    if ratio_division == None:
        # Create a new component
        Array = gf.Component()
        Class_Array = ArrayClass(0,0,0)
        
        # Create frame of LCs
        SingleCell = gf.components.rectangle(size=(chip.CellWidth, chip.CellHeight), layer=LAYER.Frame)
        CellFrame = Array.add_array(SingleCell, columns=num_column, rows=num_row, spacing=[chip.CellWidth, chip.CellHeight])
        print('Frame created')

        # Create Pads
        Space_Pad = chip.CellHeight*num_row/(num_column*num_row)
        
        TPad = gf.Component()
        TPadself = TPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.Bond0)
        TPadin = TPad << gf.components.optimal_step(start_width=pad.width0/2, end_width=TL_width-tolerance/2, num_pts=100, layer=LAYER.Bond0, anticrowding_factor=0.1)
        TPadin.xmin = TPadself.xmax
        
        GPad = gf.Component()
        GPadself = GPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.GP)
        GPadin = GPad << gf.components.optimal_step(start_width=TL_width, end_width=pad.width0/2, num_pts=100, layer=LAYER.GP, anticrowding_factor=0.1).rotate(180)
        GPadin.xmin = GPadself.xmax
        GPadin.ymin = GPadself.ymin
        
        # Add Sum Pads
        SumPad1 = Array << gf.components.nxn(east=num_pads, west=0, south=0, north=0, ysize=(num_pads*2-1)*TL_width - tolerance/2, xsize=pad.length1, layer=LAYER.Bond0, wg_width=TL_width - tolerance/2, wg_margin=0)
        SumPad1.ymin = num_row*chip.CellHeight + 2*chip.wire_corner_radius
        Array.add_ports(SumPad1.ports,prefix='SumPad1')

        SumPad2 = Array << gf.components.nxn(east=num_pads, west=0, south=0, north=0, ysize=(num_pads*2-1)*TL_width+tolerance/2, xsize=pad.length1+tolerance, layer=LAYER.GP, wg_width=TL_width, wg_margin=tolerance/4)
        SumPad2.ymin = SumPad1.ymin - tolerance/2
        SumPad2.xmin = SumPad1.xmin - tolerance/2
        Array.add_ports(SumPad2.ports,prefix='SumPad2')

        # Add SQIUD Pad and GND Pad
        SquidPad = Array << gf.components.rectangle(size=(pad.width0, pad.width0), layer=LAYER.GP)
        SquidPad.ymin = SumPad1.ymin - (pad.width0 + chip.wire_corner_radius/2 - SumPad1.ysize/2)

        BiasPad = Array << gf.components.rectangle(size=(pad.width0, pad.width0), layer=LAYER.Bond0)
        BiasPad.ymin = SquidPad.ymax + chip.wire_corner_radius

        print('Pads created')

        # Create Array
        LCs = []
        TPads = []
        GPads = []
        R = [0 for i in range(num_row)]
        for j in range(num_row):
            # Create LCs
            R[j] = gf.Component()
            for i in range(num_column):
                LCs.append(R[j].add_ref(LCGenerator(via_pad_width,Ctype,num_layers,Frequencies[num_row-j-1][i],ratio_division)))
                # LC.movex(L.outer_diameter)
                LCs[5*j+i].xmin = i*chip.CellWidth
                LCs[5*j+i].ymax = (j+1)*chip.CellHeight - num_column*2*TL_width - chip.wire_corner_radius
                R[j].add_port(name = 'Lin'+str(j)+str(i), port = LCs[5*j+i].ports['Lin'])
                R[j].add_port(name = 'FCout'+str(j)+str(i), port = LCs[5*j+i].ports['FCout'])
            Array << R[j]

            # Create Pads Arrays
            TPads.append(Array.add_array(TPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
            TPads[j].xmax = CellFrame.xmin - TL_width*2*num_column - 10*TL_width - chip.wire_corner_radius - TL_width/2
            TPads[j].ymin = CellFrame.ymin + j*chip.CellHeight + pad.width0/2 + chip.wire_corner_radius
            for i in range(num_column): # Add ports to pads
                Array.add_port(name = 'TPad' + str(j) + str(i), center=(TPads[j].xmax, TPads[j].ymax - i*Space_Pad - pad.width0/2 - tolerance/4 + TL_width/2), width=TL_width-tolerance/2, orientation=0, layer=LAYER.Bond0)
            
            GPads.append(Array.add_array(GPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
            GPads[j].xmax = CellFrame.xmin - TL_width*2*num_column - 10*TL_width - chip.wire_corner_radius - TL_width/2
            GPads[j].ymin = CellFrame.ymin + j*chip.CellHeight
            for i in range(num_column): # Add ports to pads
                Array.add_port(name = 'GPad' + str(j) + str(i), center=(GPads[j].xmax, GPads[j].ymax - i*Space_Pad - TL_width/2), width=TL_width, orientation=0, layer=LAYER.GP)
            
            # Routing to Pads
            RLroutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0].startswith('TPad'+str(j)) ], [x[1] for x in R[j].ports.items() if x[0].startswith('Lin'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width-tolerance/2, layer = LAYER.Bond0, separation=TL_width*2,
                steps=[
                    {"dx": num_column*TL_width*2+chip.wire_corner_radius, "dy": 0},
                    {"dx": 0, "y": R[j].ymax + chip.wire_corner_radius + TL_width/2},
                    {"x": R[j].ports['Lin'+str(j)+'0'].center[0], "dy": 0},
                ],
            )
            for route in RLroutes:
                Array.add(route.references)
            
            CBroutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0] in ['SumPad1o'+str(j*num_column+1+i) for i in range(num_column)]], [x[1] for x in R[j].ports.items() if x[0].startswith('FCout'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width-tolerance/2, layer = LAYER.Bond0, separation=TL_width*2,
                steps=[
                    {"x": R[j].xmax + (num_pads-j*num_column+1-.75)*TL_width*2, "dy": 0},
                    {"dx": 0, "y": R[j].ymin - chip.wire_corner_radius},
                    {"x": R[j].ports['FCout'+str(j)+'0'].center[0], "dy": 0},
                ],
            ) #bundle 函数以最右侧线的中线算位置
            for route in CBroutes:
                Array.add(route.references)

            RSroutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0] in ['SumPad2o'+str(j*num_column+1+i) for i in range(num_column)]], [x[1] for x in Array.ports.items() if x[0].startswith('GPad'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width, layer = LAYER.GP, separation=TL_width*2,
                steps=[
                    {"x": R[j].xmax + (num_pads-j*num_column+1-.75)*TL_width*2, "dy": 0},
                    {"dx": 0, "y":R[j].ymax + chip.wire_corner_radius + (num_column*2-1.5)*TL_width},#这里以最下侧线为标准
                    {"x": R[j].xmin - (5+num_column-.75)*2*TL_width, "dy": 0},#这里又变成最左侧线了
                    {"dx": 0, "y": Array.ports['GPad'+str(j)+'0'].center[1]},
                ])
            for route in RSroutes:
                Array.add(route.references)
        
        # Correct the position of GND and Squid Pads and wire them to Sumpads
        SquidPad.xmin = GPads[0].xmin
        BiasPad.xmin = GPads[0].xmin

        BiasWire1 = Array.add_polygon([(BiasPad.xmax, SumPad1.ymax), (SumPad1.xmin, SumPad1.ymax), (SumPad1.xmin, BiasPad.ymin), (BiasPad.xmax, BiasPad.ymin)], layer=LAYER.Bond0)
        SquidWire1 = Array.add_polygon([(SquidPad.xmax, SquidPad.ymax), (SumPad2.xmin, SquidPad.ymax), (SumPad2.xmin, SumPad2.ymin), (SquidPad.xmax, SumPad2.ymin)], layer=LAYER.GP)
        
        # Add Bonding Pads and Holes for GPads, BiasPad and SquidPad
        GPadhole = gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0/2 - 2*tolerance), layer=LAYER.E0)
        GPadholes = Array.add_array(GPadhole, columns=1, rows=num_pads, spacing=[0,Space_Pad])
        GPadholes.ymin = GPads[0].ymin + tolerance
        GPadholes.xmin = GPads[0].xmin + tolerance

        GPadBondings = Array.add_array(gf.components.rectangle(size=(pad.width0 - tolerance, pad.width0/2 - tolerance), layer=LAYER.Bond0), columns=1, rows=num_pads, spacing=[0,Space_Pad])
        GPadBondings.ymin = GPads[0].ymin + tolerance/2
        GPadBondings.xmin = GPads[0].xmin + tolerance/2

        SquidPadhole = Array << gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0 - 2*tolerance), layer=LAYER.E0)
        SquidPadhole.ymax = SquidPad.ymax - tolerance
        SquidPadhole.xmin = SquidPad.xmin + tolerance

        SquidPadBonding = Array << gf.components.rectangle(size=(pad.width0 - tolerance, pad.width0 - tolerance), layer=LAYER.Bond0)
        SquidPadBonding.ymax = SquidPad.ymax - tolerance/2
        SquidPadBonding.xmin = SquidPad.xmin + tolerance/2

        # Create etched edge for array
        Edge = Array << gf.geometry.outline(gf.components.rectangle(size=(Array.xsize + 250, Array.ysize + 250)), distance=75, layer=LAYER.E0)
        Edge.xmin = Array.xmin - 200
        Edge.ymin = Array.ymin - 200

        Coner = gf.Component()
        Coner.add_polygon([(0,0), (50,0), (50,450), (500,450), (500,500), (0,500)], layer=LAYER.GP)
        
        C1 = Array << Coner
        C2 = Array << Coner
        C3 = Array << Coner
        C4 = Array << Coner

        C1.xmin = Edge.xmin + 25
        C1.ymax = Edge.ymax - 25
        C2.rotate(-90)
        C2.xmax = Edge.xmax - 25
        C2.ymax = Edge.ymax - 25
        C3.rotate(90)
        C3.xmin = Edge.xmin + 25
        C3.ymin = Edge.ymin + 25
        C4.rotate(180)
        C4.xmax = Edge.xmax - 25
        C4.ymin = Edge.ymin + 25

        EdgeCenterY = gf.components.rectangle(size = (50, Array.ysize/20), layer=LAYER.GP)
        EdgeCenterX = gf.components.rectangle(size = (Array.xsize/20, 50), layer=LAYER.GP)
        
        EY1 = Array << EdgeCenterY
        EY2 = Array << EdgeCenterY
        EX1 = Array << EdgeCenterX
        EX2 = Array << EdgeCenterX

        EY1.xmin = Edge.xmin + 25
        EY1.ymin = Edge.ymin + Edge.ysize/2 - EY1.ysize/2
        EY2.xmax = Edge.xmax - 25
        EY2.ymin = Edge.ymin + Edge.ysize/2 - EY2.ysize/2
        EX1.ymax = Edge.ymax
        EX1.xmin = Edge.xmin + Edge.xsize/2 - EX1.xsize/2
        EX2.ymin = Edge.ymin + 25
        EX2.xmin = Edge.xmin + Edge.xsize/2 - EX2.xsize/2

        # Add Notes
        NoteBias = Array << gf.components.text_freetype('LC BIAS', size=Class_Array.note_font_size, font = 'FangSong', justify='center', layer=LAYER.Bond0).rotate(90)
        NoteBias.xmax = BiasPad.xmin - chip.wire_corner_radius
        NoteBias.ymin = BiasPad.ymin + pad.width0/2 - NoteBias.ysize/2

        NoteSquid = Array << gf.components.text_freetype('SQUID IN', size=Class_Array.note_font_size, font = 'FangSong', justify='center', layer=LAYER.Bond0).rotate(90)
        NoteSquid.xmax = SquidPad.xmin - chip.wire_corner_radius
        NoteSquid.ymin = SquidPad.ymin + pad.width0/2 - NoteSquid.ysize/2
    else:
        # Create a new component
        Array = gf.Component()
        Class_Array = ArrayClass(0,0,0)
        
        # Create frame of LCs
        SingleCell = gf.components.rectangle(size=(chip.CellWidth, chip.CellHeight), layer=LAYER.Frame)
        CellFrame = Array.add_array(SingleCell, columns=num_column, rows=num_row, spacing=[chip.CellWidth, chip.CellHeight])
        print('Frame created')

        # Create Pads
        Space_Pad = chip.CellHeight*num_row/(num_column*num_row)
        
        TPad = gf.Component()
        TPadself = TPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.Bond0)
        TPadin = TPad << gf.components.optimal_step(start_width=pad.width0/2, end_width=TL_width-tolerance/2, num_pts=100, layer=LAYER.Bond0, anticrowding_factor=0.1)
        TPadin.xmin = TPadself.xmax
        
        GPad = gf.Component()
        GPadself = GPad << gf.components.rectangle(size=(pad.width0, pad.width0/2), layer=LAYER.GP)
        GPadin = GPad << gf.components.optimal_step(start_width=TL_width, end_width=pad.width0/2, num_pts=100, layer=LAYER.GP, anticrowding_factor=0.1).rotate(180)
        GPadin.xmin = GPadself.xmax
        GPadin.ymin = GPadself.ymin
        
        # Add Sum Pads
        SumPad1 = Array << gf.components.nxn(east=num_pads, west=0, south=0, north=0, ysize=(num_pads*2-1)*TL_width - tolerance/2, xsize=pad.length1, layer=LAYER.Bond0, wg_width=TL_width - tolerance/2, wg_margin=0)
        SumPad1.ymin = num_row*chip.CellHeight + num_pads*2*TL_width + chip.wire_corner_radius
        Array.add_ports(SumPad1.ports,prefix='SumPad1')

        SumPad2 = Array << gf.components.nxn(east=num_pads, west=0, south=0, north=0, ysize=(num_pads*2-1)*TL_width+tolerance/2, xsize=pad.length1+tolerance, layer=LAYER.GP, wg_width=TL_width, wg_margin=tolerance/4)
        SumPad2.ymin = SumPad1.ymin - tolerance/2
        SumPad2.xmin = SumPad1.xmin - tolerance/2
        Array.add_ports(SumPad2.ports,prefix='SumPad2')

        SumPad3 = Array << gf.components.nxn(south=num_pads, west=0, east=0, north=0, xsize=(num_pads*2-1)*TL_width, ysize=pad.length1, layer=LAYER.GP, wg_width=TL_width, wg_margin=0)
        SumPad3.ymax = SumPad2.ymin - chip.sumpad_gap - (pad.width0 + chip.wire_corner_radius/2 - SumPad1.ysize/2)
        SumPad3.xmax = - 10*TL_width
        Array.add_ports(SumPad3.ports,prefix='SumPad3')

        # Add SQIUD Pad and GND Pad
        BiasPad = Array << gf.components.rectangle(size=(pad.width0, pad.width0), layer=LAYER.GP)
        BiasPad.ymin = SumPad1.ymin - (pad.width0 + chip.wire_corner_radius/2 - SumPad1.ysize/2)

        GndPad = Array << gf.components.rectangle(size=(pad.width0, pad.width0), layer=LAYER.Bond0)
        GndPad.ymin = BiasPad.ymax + chip.wire_corner_radius

        SquidPad = Array << gf.components.rectangle(size=(pad.width0, pad.width0), layer=LAYER.GP)
        SquidPad.ymax = SumPad3.ymax

        print('Pads created')

        # Create Array
        LCs = []
        TPads = []
        GPads = []
        R = [0 for i in range(num_row)]
        for j in range(num_row):
            # Create LCs
            R[j] = gf.Component()
            for i in range(num_column):
                LCs.append(R[j].add_ref(LCGenerator(via_pad_width,Ctype,num_layers,Frequencies[num_row-j-1][i],ratio_division)))
                # LC.movex(L.outer_diameter)
                LCs[5*j+i].xmin = i*chip.CellWidth
                LCs[5*j+i].ymax = (j+1)*chip.CellHeight - num_column*2*TL_width - chip.wire_corner_radius
                R[j].add_port(name = 'Lin'+str(j)+str(i), port = LCs[5*j+i].ports['Lin'])
                R[j].add_port(name = 'FCout'+str(j)+str(i), port = LCs[5*j+i].ports['FCout'])
                R[j].add_port(name = 'CCout'+str(j)+str(i), port = LCs[5*j+i].ports['CCin'])
            Array << R[j]

            # Create Pads Arrays
            TPads.append(Array.add_array(TPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
            TPads[j].xmax = CellFrame.xmin - TL_width*2*num_pads - 10*TL_width - chip.wire_corner_radius - TL_width/2
            TPads[j].ymin = CellFrame.ymin + j*chip.CellHeight + pad.width0/2 + chip.wire_corner_radius
            for i in range(num_column): # Add ports to pads
                Array.add_port(name = 'TPad' + str(j) + str(i), center=(TPads[j].xmax, TPads[j].ymax - i*Space_Pad - pad.width0/2 - tolerance/4 + TL_width/2), width=TL_width-tolerance/2, orientation=0, layer=LAYER.Bond0)
            
            GPads.append(Array.add_array(GPad, columns=1, rows=num_column, spacing=[0,Space_Pad]))
            GPads[j].xmax = CellFrame.xmin - TL_width*2*num_pads - 10*TL_width - chip.wire_corner_radius - TL_width/2
            GPads[j].ymin = CellFrame.ymin + j*chip.CellHeight
            for i in range(num_column): # Add ports to pads
                Array.add_port(name = 'GPad' + str(j) + str(i), center=(GPads[j].xmax, GPads[j].ymax - i*Space_Pad - TL_width/2), width=TL_width, orientation=0, layer=LAYER.GP)
            
            # Routing to Pads
            RLroutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0].startswith('TPad'+str(j)) ], [x[1] for x in R[j].ports.items() if x[0].startswith('Lin'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width-tolerance/2, layer = LAYER.Bond0, separation=TL_width*2,
                steps=[
                    {"dx": num_pads*TL_width*2+chip.wire_corner_radius, "dy": 0},
                    {"dx": 0, "y":R[j].ymax + chip.wire_corner_radius + TL_width/2},
                    {"x":R[j].ports['Lin'+str(j)+'0'].center[0], "dy":0},
                ],
            )
            for route in RLroutes:
                Array.add(route.references)
            
            CGroutes = gf.routing.get_bundle_from_steps([x[1] for x in Array.ports.items() if x[0] in ['SumPad1o'+str(j*num_column+1+i) for i in range(num_column)]], [x[1] for x in R[j].ports.items() if x[0].startswith('FCout'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width-tolerance/2, layer = LAYER.Bond0, separation=TL_width*2,
                steps=[
                    {"x": R[j].xmax + (num_pads-j*num_column+1-.75)*TL_width*2, "dy": 0},
                    {"dx": 0, "y": R[j].ymin - chip.wire_corner_radius},
                    {"x": R[j].ports['FCout'+str(j)+'0'].center[0], "dy": 0},
                ],
            ) #bundle 函数以最右侧线的中线算位置
            for route in CGroutes:
                Array.add(route.references)

            CBroutes = []
            for i in range(num_column-1):
                CBroutes.append(gf.routing.get_route_from_steps(Array.ports['SumPad2o'+str(j*num_column+1+i)], R[j].ports['CCout'+str(j)+str(i)], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width, layer = LAYER.GP,
                    steps=[
                        {"x": R[j].xmax + (num_pads-j*num_column-i+5-.75)*TL_width*2, "dy": 0},
                        {"dx": 0, "y": R[j].ymin - (num_column-i-1)*2*TL_width - chip.wire_corner_radius},
                        {"x": R[j].ports['CCout'+str(j)+str(i)].center[0]+chip.wire_corner_radius, "dy": 0},
                        {"dx" :0, "y": R[j].ports['CCout'+str(j)+str(i)].center[1]},
                    ],
                ))
            i = num_column-1
            CBroutes.append(gf.routing.get_route_from_steps(Array.ports['SumPad2o'+str(j*num_column+1+i)], R[j].ports['CCout'+str(j)+str(i)], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width, layer = LAYER.GP,
                    steps=[
                        {"x": R[j].xmax + (num_pads-j*num_column-i+5-.75)*TL_width*2, "dy": 0},
                        {"dx": 0, "y": R[j].ports['CCout'+str(j)+str(i)].center[1]},
                    ],
                ))
            for route in CBroutes:
                Array.add(route.references)

            RSroutes = gf.routing.get_bundle([x[1] for x in Array.ports.items() if x[0] in ['SumPad3o'+str(j*num_column+1+i) for i in range(num_column)]], [x[1] for x in Array.ports.items() if x[0].startswith('GPad'+str(j))], bend = 'bend_euler', radius = chip.wire_corner_radius, width = TL_width, layer = LAYER.GP, separation=TL_width*2) #bundle 函数以最右侧线的中线算位置
            for route in RSroutes:
                Array.add(route.references)
        
        # Correct the position of GND and Squid Pads and wire them to Sumpads
        GndPad.xmin = GPads[0].xmin
        SquidPad.xmin = GPads[0].xmin
        BiasPad.xmin = GPads[0].xmin

        GndWire = Array << gf.components.optimal_step(start_width=pad.width0, end_width=SumPad1.ysize/2-chip.wire_corner_radius/2, num_pts=100, layer=LAYER.Bond0, anticrowding_factor=0.3)
        GndWire.xmin = GndPad.xmax
        GndWire.ymin = GndPad.ymin

        BiasWire = Array << gf.components.optimal_step(end_width=pad.width0, start_width=SumPad2.ysize/2-chip.wire_corner_radius/2, num_pts=100, layer=LAYER.GP, anticrowding_factor=0.3).rotate(180)
        BiasWire.xmin = BiasPad.xmax
        BiasWire.ymax = BiasPad.ymax

        GndWire1 = Array.add_polygon([(GndWire.xmax, SumPad1.ymax), (SumPad1.xmin, SumPad1.ymax), (SumPad1.xmin, GndWire.ymin), (GndWire.xmax, GndWire.ymin)], layer=LAYER.Bond0)
        BiasWire1 = Array.add_polygon([(BiasWire.xmax, BiasWire.ymax), (SumPad2.xmin, BiasWire.ymax), (SumPad2.xmin, SumPad2.ymin), (BiasWire.xmax, SumPad2.ymin)], layer=LAYER.GP)
        SquidPad1 = Array.add_polygon([(SquidPad.xmax, SquidPad.ymax), (SumPad3.xmin, SquidPad.ymax), (SumPad3.xmin, SumPad3.ymin), (SquidPad.xmax, SquidPad.ymin)], layer=LAYER.GP)
        
        # Add Bonding Pads and Holes for GPads, BiasPad and SquidPad
        GPadhole = gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0/2 - 2*tolerance), layer=LAYER.E0)
        GPadholes = Array.add_array(GPadhole, columns=1, rows=num_pads, spacing=[0,Space_Pad])
        GPadholes.ymin = GPads[0].ymin + tolerance
        GPadholes.xmin = GPads[0].xmin + tolerance

        GPadBondings = Array.add_array(gf.components.rectangle(size=(pad.width0 - tolerance, pad.width0/2 - tolerance), layer=LAYER.Bond0), columns=1, rows=num_pads, spacing=[0,Space_Pad])
        GPadBondings.ymin = GPads[0].ymin + tolerance/2
        GPadBondings.xmin = GPads[0].xmin + tolerance/2

        BiasPadhole = Array << gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0 - 2*tolerance), layer=LAYER.E0)
        BiasPadhole.ymin = BiasPad.ymin + tolerance
        BiasPadhole.xmin = BiasPad.xmin + tolerance

        BiasPadBonding = Array << gf.components.rectangle(size=(pad.width0 - tolerance, pad.width0 - tolerance), layer=LAYER.Bond0)
        BiasPadBonding.ymin = BiasPad.ymin + tolerance/2
        BiasPadBonding.xmin = BiasPad.xmin + tolerance/2

        SquidPadhole = Array << gf.components.rectangle(size=(pad.width0 - 2*tolerance, pad.width0 - 2*tolerance), layer=LAYER.E0)
        SquidPadhole.ymax = SquidPad.ymax - tolerance
        SquidPadhole.xmin = SquidPad.xmin + tolerance

        SquidPadBonding = Array << gf.components.rectangle(size=(pad.width0 - tolerance, pad.width0 - tolerance), layer=LAYER.Bond0)
        SquidPadBonding.ymax = SquidPad.ymax - tolerance/2
        SquidPadBonding.xmin = SquidPad.xmin + tolerance/2

        # Create etched edge for array
        Edge = Array << gf.geometry.outline(gf.components.rectangle(size=(Array.xsize + 250, Array.ysize + 250)), distance=75, layer=LAYER.E0)
        Edge.xmin = Array.xmin - 200
        Edge.ymin = Array.ymin - 200

        Coner = gf.Component()
        Coner.add_polygon([(0,0), (50,0), (50,450), (500,450), (500,500), (0,500)], layer=LAYER.GP)
        
        C1 = Array << Coner
        C2 = Array << Coner
        C3 = Array << Coner
        C4 = Array << Coner

        C1.xmin = Edge.xmin + 25
        C1.ymax = Edge.ymax - 25
        C2.rotate(-90)
        C2.xmax = Edge.xmax - 25
        C2.ymax = Edge.ymax - 25
        C3.rotate(90)
        C3.xmin = Edge.xmin + 25
        C3.ymin = Edge.ymin + 25
        C4.rotate(180)
        C4.xmax = Edge.xmax - 25
        C4.ymin = Edge.ymin + 25

        EdgeCenterY = gf.components.rectangle(size = (50, Array.ysize/20), layer=LAYER.GP)
        EdgeCenterX = gf.components.rectangle(size = (Array.xsize/20, 50), layer=LAYER.GP)
        
        EY1 = Array << EdgeCenterY
        EY2 = Array << EdgeCenterY
        EX1 = Array << EdgeCenterX
        EX2 = Array << EdgeCenterX

        EY1.xmin = Edge.xmin + 25
        EY1.ymin = Edge.ymin + Edge.ysize/2 - EY1.ysize/2
        EY2.xmax = Edge.xmax - 25
        EY2.ymin = Edge.ymin + Edge.ysize/2 - EY2.ysize/2
        EX1.ymax = Edge.ymax
        EX1.xmin = Edge.xmin + Edge.xsize/2 - EX1.xsize/2
        EX2.ymin = Edge.ymin + 25
        EX2.xmin = Edge.xmin + Edge.xsize/2 - EX2.xsize/2

        # Add Notes
        NoteGND = Array << gf.components.text_freetype('GND', size=Class_Array.note_font_size, font = 'FangSong', justify='center', layer=LAYER.Bond0).rotate(90)
        NoteGND.xmax = GndPad.xmin - chip.wire_corner_radius
        NoteGND.ymin = GndPad.ymin + pad.width0/2 - NoteGND.ysize/2

        NoteBias = Array << gf.components.text_freetype('LC BIAS', size=Class_Array.note_font_size, font = 'FangSong', justify='center', layer=LAYER.Bond0).rotate(90)
        NoteBias.xmax = BiasPad.xmin - chip.wire_corner_radius
        NoteBias.ymin = BiasPad.ymin + pad.width0/2 - NoteBias.ysize/2

        NoteSquid = Array << gf.components.text_freetype('SQUID IN', size=Class_Array.note_font_size, font = 'FangSong', justify='center', layer=LAYER.Bond0).rotate(90)
        NoteSquid.xmax = SquidPad.xmin - chip.wire_corner_radius
        NoteSquid.ymin = SquidPad.ymin + pad.width0/2 - NoteSquid.ysize/2

    return Array 

@gf.cell
def newChip(ArrayFunction,Radius_inch,labelpath = False, distribution = 'Default',inverse=False, InverseArrayPath = None,**kwargs) -> gf.Component:
    '''
    Creates a new chip.
    '''
    # Create a new component
    Chip = gf.Component()
    print(kwargs)

    # Create wafer layer
    Wafer = Chip << WaferCircle(Radius_inch)

    if distribution == 'Default':
        if Radius_inch == 2:
            # Create array of LCs
            Arrays = gf.Component()
            num_row = kwargs['num_row']
            
            Array1 = Arrays << ArrayFunction(**kwargs)
            Array1.movey(-chip.CellHeight*num_row/2)
            Array1.xmin = (Wafer.xmax+Wafer.xmin)/2 - (Array1.xmax-Array1.xmin)/2

            Array2 = Arrays << ArrayFunction(**kwargs)
            Array2.movey(-chip.CellHeight*num_row/2)
            Array2.xmax = Array1.xmin - chip.CellWidth + 400

            Array3 = Arrays << ArrayFunction(**kwargs)
            Array3.movey(-chip.CellHeight*num_row/2)
            Array3.xmin = Array1.xmax + chip.CellWidth - 400

            Arrays_ref = Chip << Arrays

            #Create alignment markers
            Marker = gf.Component()
            M1 = Marker << AlignMarker(LAYER.TP, 1)
            M2 = Marker << AlignMarker(LAYER.E0, 2)
            M3 = Marker << AlignMarker(LAYER.Bond0, 3)

            M2.movey(1500*1)
            M3.movey(1500*2)

            LMarker = Chip << Marker
            LMarker.xmax = Arrays_ref.xmin - chip.CellWidth/2
            LMarker.movey(-LMarker.ysize/2)

            RMarker = Chip << Marker
            RMarker.xmin = Arrays_ref.xmax + chip.CellWidth/2
            RMarker.movey(-RMarker.ysize/2)
            
            # Create Mask Order label
            '''
            This order should be easily user-defined in the future.
            '''
            MaskOrder = gf.Component()
            O1 = MaskOrder.add_ref(gf.components.text_freetype('Mask 01', size=1500, font = 'FangSong', justify='center', layer=LAYER.GP))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 02', size=1500, font = 'FangSong', justify='center', layer=LAYER.TP))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 03', size=1500, font = 'FangSong', justify='center', layer=LAYER.E0))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 04', size=1500, font = 'FangSong', justify='center', layer=LAYER.Bond0))

            # Create Label for the chip (if have)
            if labelpath:
                label = MaskOrder << gf.import_gds(labelpath)
                label.xmax = O1.xmin - 3000
                label.ymin = MaskOrder.ymin
            
            MaskOrder = Chip << MaskOrder
            MaskOrder.ymin = Arrays_ref.ymax + 1000
            MaskOrder.xmin = -MaskOrder.xsize/2


        elif Radius_inch == 4:
            Array_num = 13
            # Create arrays with basic parameters
            oriArray = ArrayFunction(**kwargs)
            Arrays = [Chip << oriArray for i in range(Array_num)]
            ArrayClasses = [ArrayClass(1,1,90),ArrayClass(2,1,90),ArrayClass(2,2,90),ArrayClass(3,1,0),ArrayClass(3,2,0),ArrayClass(3,3,0),ArrayClass(3,4,0),ArrayClass(3,5,0),ArrayClass(3,6,0),ArrayClass(3,7,0),ArrayClass(4,1,90),ArrayClass(4,2,90),ArrayClass(5,1,90)]
            
            # Alter the orientation of arrays and determine height of every row and width of every column
            Heights = []
            Widths = [[]]
            for i in range(Array_num):
                Arrays[i].rotate(ArrayClasses[i].rotation)
                try:
                    if Arrays[i].ysize > Heights[ArrayClasses[i].row_position - 1]:
                        Heights[ArrayClasses[i].row_position - 1] = Arrays[i].ysize
                    Widths[ArrayClasses[i].row_position - 1] += [Arrays[i].xsize]
                except:
                    Heights.append(Arrays[i].ysize)
                    Widths.append([])
                    Widths[ArrayClasses[i].row_position - 1] += [Arrays[i].xsize]
            Widths = Widths[:-1]
            
            # Position for rows
            centerrow = len(Heights)/2
            if centerrow % 1 != 0:
                centerrow = floor(centerrow)
                RowBasePoint = - Heights[int(centerrow)].max()/2
            else:
                centerrow = int(centerrow) - 1
                RowBasePoint = chip.array_gap_y/2
            
            # Position for columns
            ColumnBasePoints = []
            centercolumns = []
            for i in range(len(Widths)):
                centercolumns += [len(Widths[i])/2]
                if centercolumns[i] % 1 != 0:
                    centercolumns[i] = floor(centercolumns[i])
                    ColumnBasePoints += [- Widths[i][int(centercolumns[i])]/2]
                else:
                    centercolumns[i] = int(centercolumns[i]) - 1
                    ColumnBasePoints += [- Widths[i][centercolumns[i]] - chip.array_gap_x/2]
            # print(centerrow, RowBasePoint,centercolumns,ColumnBasePoints,Widths,Heights)
            
            # Place arrays
            for i in range(Array_num):
                if ArrayClasses[i].row_position - 1 < centerrow:
                    Arrays[i].ymin = RowBasePoint + sum(Heights[ArrayClasses[i].row_position:int(centerrow + 1)]) + chip.array_gap_y*(int(centerrow + 1)-ArrayClasses[i].row_position)
                else:
                    Arrays[i].ymin = RowBasePoint - sum(Heights[int(centerrow + 1):ArrayClasses[i].row_position]) - chip.array_gap_y*(ArrayClasses[i].row_position - int(centerrow + 1))
                if ArrayClasses[i].column_position - 1 < centercolumns[ArrayClasses[i].row_position - 1]:
                    Arrays[i].xmin = ColumnBasePoints[ArrayClasses[i].row_position - 1] - sum(Widths[ArrayClasses[i].row_position - 1][ArrayClasses[i].column_position - 1:centercolumns[ArrayClasses[i].row_position - 1]]) - chip.array_gap_x*(centercolumns[ArrayClasses[i].row_position - 1] - ArrayClasses[i].column_position + 1)
                else: 
                    Arrays[i].xmin = ColumnBasePoints[ArrayClasses[i].row_position - 1] + sum(Widths[ArrayClasses[i].row_position - 1][centercolumns[ArrayClasses[i].row_position - 1]:ArrayClasses[i].column_position - 1]) + chip.array_gap_x*(ArrayClasses[i].column_position - 1 - centercolumns[ArrayClasses[i].row_position - 1])
                    # print(ColumnBasePoints[ArrayClasses[i].column_position - 1],Widths[ArrayClasses[i].row_position - 1][centercolumns[ArrayClasses[i].row_position - 1]:ArrayClasses[i].column_position - 1],Arrays[i].xmin)
            
            #Create alignment markers
            Marker = gf.Component()
            M1 = Marker << AlignMarker(LAYER.TP, 1)
            M2 = Marker << AlignMarker(LAYER.E0, 2)
            M3 = Marker << AlignMarker(LAYER.Bond0, 3)

            M2.movey(1500*1)
            M3.movey(1500*2)

            LMarker = Chip << Marker
            LMarker.xmin, LMarker.ymin = chip.MarkerPosition
            LMarker.movex(-LMarker.xsize/2).movey(-LMarker.ysize/2)

            RMarker = Chip << Marker
            RMarker.xmin, RMarker.ymin = -chip.MarkerPosition[0], chip.MarkerPosition[1]
            RMarker.movex(-RMarker.xsize/2).movey(-RMarker.ysize/2)

            # Create Mask Order label
            '''
            This order should be easily user-defined in the future.
            '''
            MaskOrder = gf.Component()
            O1 = MaskOrder.add_ref(gf.components.text_freetype('Mask 01', size=1500, font = 'FangSong', justify='center', layer=LAYER.GP))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 02', size=1500, font = 'FangSong', justify='center', layer=LAYER.TP))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 03', size=1500, font = 'FangSong', justify='center', layer=LAYER.E0))
            MaskOrder.add_ref(gf.components.text_freetype('Mask 04', size=1500, font = 'FangSong', justify='center', layer=LAYER.Bond0))

            # Create Label for the chip (if have)
            if labelpath:
                label = MaskOrder << gf.import_gds(labelpath)
                label.xmax = O1.xmin - 3000
                label.ymin = MaskOrder.ymin
            
            MaskOrder = Chip << MaskOrder
            MaskOrder.xmin, MaskOrder.ymin = chip.MaskLabelPosition
            MaskOrder.movex(-MaskOrder.xsize/2).movey(-MaskOrder.ysize/2)

        else:
            raise ValueError('Invalid wafer size')
        
    else:
        try:
            # Create arrays with basic parameters
            Array_num = len(distribution)
            oriArray = ArrayFunction(**kwargs)
            Arrays = [Chip << oriArray for i in range(Array_num)]
            ArrayClasses = []
            for array in distribution:
                ArrayClasses.append(ArrayClass(array[0],array[1],array[2]))
        except:
            raise ValueError('Please input a list of Array postions and rotations as distribution')
        
        # Alter the orientation of arrays and determine height of every row and width of every column
        Heights = []
        Widths = [[]]
        for i in range(Array_num):
            Arrays[i].rotate(ArrayClasses[i].rotation)
            try:
                if Arrays[i].ysize > Heights[ArrayClasses[i].row_position - 1]:
                    Heights[ArrayClasses[i].row_position - 1] = Arrays[i].ysize
                Widths[ArrayClasses[i].row_position - 1] += [Arrays[i].xsize]
            except:
                Heights.append(Arrays[i].ysize)
                Widths.append([])
                Widths[ArrayClasses[i].row_position - 1] += [Arrays[i].xsize]
        Widths = Widths[:-1]
            
        # Position for rows
        centerrow = len(Heights)/2
        if centerrow % 1 != 0:
            centerrow = floor(centerrow)
            RowBasePoint = - Heights[int(centerrow)].max()/2
        else:
            centerrow = int(centerrow) - 1
            RowBasePoint = chip.array_gap_y/2
        
        # Position for columns
        ColumnBasePoints = []
        centercolumns = []
        for i in range(len(Widths)):
            centercolumns += [len(Widths[i])/2]
            if centercolumns[i] % 1 != 0:
                centercolumns[i] = floor(centercolumns[i])
                ColumnBasePoints += [- Widths[i][int(centercolumns[i])]/2]
            else:
                centercolumns[i] = int(centercolumns[i]) - 1
                ColumnBasePoints += [- Widths[i][centercolumns[i]] - chip.array_gap_x/2]
        # print(centerrow, RowBasePoint,centercolumns,ColumnBasePoints,Widths,Heights)
        
        # Place arrays
        for i in range(Array_num):
            if ArrayClasses[i].row_position - 1 < centerrow:
                Arrays[i].ymin = RowBasePoint + sum(Heights[ArrayClasses[i].row_position:int(centerrow + 1)]) + chip.array_gap_y*(int(centerrow + 1)-ArrayClasses[i].row_position)
            else:
                Arrays[i].ymin = RowBasePoint - sum(Heights[int(centerrow + 1):ArrayClasses[i].row_position]) - chip.array_gap_y*(ArrayClasses[i].row_position - int(centerrow + 1))
            if ArrayClasses[i].column_position - 1 < centercolumns[ArrayClasses[i].row_position - 1]:
                Arrays[i].xmin = ColumnBasePoints[ArrayClasses[i].row_position - 1] - sum(Widths[ArrayClasses[i].row_position - 1][ArrayClasses[i].column_position - 1:centercolumns[ArrayClasses[i].row_position - 1]]) - chip.array_gap_x*(centercolumns[ArrayClasses[i].row_position - 1] - ArrayClasses[i].column_position + 1)
            else: 
                Arrays[i].xmin = ColumnBasePoints[ArrayClasses[i].row_position - 1] + sum(Widths[ArrayClasses[i].row_position - 1][centercolumns[ArrayClasses[i].row_position - 1]:ArrayClasses[i].column_position - 1]) + chip.array_gap_x*(ArrayClasses[i].column_position - 1 - centercolumns[ArrayClasses[i].row_position - 1])
                # print(ColumnBasePoints[ArrayClasses[i].column_position - 1],Widths[ArrayClasses[i].row_position - 1][centercolumns[ArrayClasses[i].row_position - 1]:ArrayClasses[i].column_position - 1],Arrays[i].xmin)
        
        #Create alignment markers
        Marker = gf.Component()
        M1 = Marker << AlignMarker(LAYER.TP, 1)
        M2 = Marker << AlignMarker(LAYER.E0, 2)
        M3 = Marker << AlignMarker(LAYER.Bond0, 3)

        M2.movey(1500*1)
        M3.movey(1500*2)

        LMarker = Chip << Marker
        LMarker.xmin, LMarker.ymin = chip.MarkerPosition
        LMarker.movex(-LMarker.xsize/2).movey(-LMarker.ysize/2)

        RMarker = Chip << Marker
        RMarker.xmin, RMarker.ymin = -chip.MarkerPosition[0], chip.MarkerPosition[1]
        RMarker.movex(-RMarker.xsize/2).movey(-RMarker.ysize/2)

        # Create Mask Order label
        '''
        This order should be easily user-defined in the future.
        '''
        MaskOrder = gf.Component()
        O1 = MaskOrder.add_ref(gf.components.text_freetype('Mask 01', size=1500, font = 'FangSong', justify='center', layer=LAYER.GP))
        MaskOrder.add_ref(gf.components.text_freetype('Mask 02', size=1500, font = 'FangSong', justify='center', layer=LAYER.TP))
        MaskOrder.add_ref(gf.components.text_freetype('Mask 03', size=1500, font = 'FangSong', justify='center', layer=LAYER.E0))
        MaskOrder.add_ref(gf.components.text_freetype('Mask 04', size=1500, font = 'FangSong', justify='center', layer=LAYER.Bond0))

        # Create Label for the chip (if have)
        if labelpath:
            label = MaskOrder << gf.import_gds(labelpath)
            label.xmax = O1.xmin - 3000
            label.ymin = MaskOrder.ymin
        
        MaskOrder = Chip << MaskOrder
        MaskOrder.xmin, MaskOrder.ymin = chip.MaskLabelPosition
        MaskOrder.movex(-MaskOrder.xsize/2).movey(-MaskOrder.ysize/2)

    if inverse:
        # GPinverse = gf.geometry.boolean(Wafer,Chip.extract([LAYER.Bond0]),'A-B')
        # Chip.remove_layers(layers=[LAYER.Bond0,LAYER.WAFER])
        # Chip.add_ref(GPinverse.references)
        ArrayFrame = gf.components.rectangle(size = (oriArray.xsize, oriArray.ysize))
        ArrayFrames = gf.Component()
        frames = []
        for i,array in enumerate(Arrays):
            frames.append(ArrayFrames << ArrayFrame)
            frames[-1].rotate(ArrayClasses[i].rotation)
            frames[-1].xmin = array.xmin
            frames[-1].ymin = array.ymin
        O1r = ArrayFrames.add_ref(gf.components.text_freetype('Mask 01', size=1500, font = 'FangSong', justify='center', layer=LAYER.GP))
        O1r.ymin = MaskOrder.ymin
        O1r.xmin = chip.MaskLabelPosition[0]
        O1r.movex(-MaskOrder.xsize/2+label.xsize+3000)
        MarkerGP = Marker.extract([LAYER.GP])
        LMarkerGP = ArrayFrames << MarkerGP
        LMarkerGP.xmax = LMarker.xmax
        LMarkerGP.ymin = chip.MarkerPosition[1]
        LMarkerGP.movey(-LMarkerGP.ysize/2)
        RMarkerGP = ArrayFrames << MarkerGP
        RMarkerGP.xmax = RMarker.xmax
        RMarkerGP.ymin = chip.MarkerPosition[1]
        RMarkerGP.movey(-RMarkerGP.ysize/2)

        Chip = Chip.remove_layers([LAYER.GP])

        Chip << gf.geometry.boolean(Wafer,ArrayFrames,'A-B',layer=LAYER.GP)
        InverseArray = gf.import_gds(InverseArrayPath)
        InverseArrays = []
        for i,frame in enumerate(frames):
            InverseArrays.append(Chip << InverseArray)
            InverseArrays[-1].rotate(ArrayClasses[i].rotation)
            InverseArrays[-1].xmin = frame.xmin
            InverseArrays[-1].ymin = frame.ymin
    return Chip