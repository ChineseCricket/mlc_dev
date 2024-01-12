import gdsfactory as gf
#---------------------- FUNCTION DEFINITION --------------------------
def LGenerator(L,LAYER,via_pad_width) -> gf.Component:
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

def CGenerator(C,LAYER) -> gf.Component:
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
def LCGenerator(L,C,LC,LAYER,via_pad_width) -> gf.Component:
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