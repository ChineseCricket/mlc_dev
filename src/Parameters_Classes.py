# THIS SCRIPT CONTAINS THE CLASSES USED IN THE GENERATION OF THE RESONATOR CHIP
import numpy
class Chip:
    def __init__(self):
        #general information
        self.name = "CHIP NAME"
        self.date = "DATE"
        #geometry
        self.num_LC_rows = 5
        self.num_LC_cols = 8
        self.CellHeight = 4000
        self.CellWidth = 2000
        self.num_LCs = 40 
        #WIRING PARAMETERS
        self.TL_width = 10 # width of transmission line
        self.wire2wire_space = self.TL_width # space between wires
        self.wire_corner_radius = 30 
        self.sumpad_gap = 100 # wiring gap for the corners of the chip
        self.array_gap_x = 2000 # gap between the array of LCs
        self.array_gap_y = 2000 # gap between the array of LCs
        self.MarkerPosition = (-41300, 21300) # position of center of alignment markers
        self.MaskLabelPosition = (25000, 37000) # position of center of mask label
        
class PadClass:
    def __init__(self):
        self.width0 = 500
        self.width1 = 100
        self.length1 = 350
        self.spacing = 20
        
        
class InductorClass:
# numLayers : number of etched layers    
    def __init__(self, numLayers):
        self.num_layers = numLayers # number of etched layers
        self.gap_width = 4#3#3#2 #microns 
        self.line_width = 4#3#3#2 # microns
        self.num_turns = 40#48#40#45 # number of turns in coil
        self.outer_diameter = 785#1560#705#650#500 # size of inductor
        self.inductance = 3.3257e-6 # inductance [Henry]
        
        if numLayers == 1:
            self.type = "with_pads"
            self.pad_gap = 20
            self.pad_width = 100
            self.pad_length = 248
            self.height = self.pad_width + self.pad_gap +  self.outer_diameter
        else:
            self.type = "without_pads"
            self.height = self.outer_diameter
        
class CapacitorClass:
    def __init__(self, Ctype, numLayers, Frequency,ratio):
    # numLayers : number of etched layers
        self.type = Ctype # save this information
        self.num_layers = numLayers
        if Ctype == "PPC":  # parallel plate capacitor
            #used in parallel plate capacitor -- maybe create this?
            self.er = 11
            self.h = 25e-9
            self.length = CalculatePPCapacitorParameters(Frequency,ratio,self.er,self.h)
        if Ctype == "IDC": #interdigital capacitor
            #used in interdigitated capacitor
            self.gap_width = 2
            self.line_width = 2
            self.base_height = 100 
            self.width = 100
            self.er = 11 # dielectric constant, using Silicon = 11.7
            self.h = 300  # [microns] thickness of substrate
            self.finger_num, self.line_height = CalculateIDCapacitorParameters(Frequency, self.h, self.line_width, self.er)
            self.height = self.base_height * 2 + self.line_height + self.gap_width # total height of capacitor
            self.small_freq_offset =  0 #6150 - (3850) + 500
        
class ResonatorClass:
    def __init__(self, height, width):
        self.height = height 
        self.width = width
        self.gap = 50 # space between capacitor and inductor
        self.channel_text_size = 80
        self.channel_text_gap = 10
        self.total_height = height

class ArrayClass:
    def __init__(self, row_position, column_position, rotation, array_type='default_array', label=None):
        self.row_position = row_position
        self.column_position = column_position
        self.rotation = rotation
        self.label = label
        self.note_font_size = 50
        self.array_type = array_type


L = InductorClass(1)

def CalculatePPCapacitorParameters(Frequency,ratio,er,h):
    # calculate the length of the parallel plate capacitor based on the desired capacity.
    # C = epsilon * A / d
    # A = length * length
    # d = 25 nm
    # epsilon = 11.7*8.85e-12
    # C = er*8.85e-12/h * S
    # S = C / (er*8.85e-12/h)
    Capacity = 1/(L.inductance*(2*Frequency*numpy.pi)**2)
    print (Capacity)
    return numpy.sqrt(ratio*Capacity / (er*8.85e-12/h))*1e6 # change its capacitor to specific ratio and convert its length to microns

def CalculateIDCapacitorParameters(Frequency, h, W, er):
    #Calculate capacitance
    Cap = 1/(L.inductance*(2*Frequency*numpy.pi)**2)# desired capacitance
    print("Capacitance = %.2E Farads" %(Cap), "Frequency = ", Frequency, "Inductance = ", L.inductance)        
        
    #SELECT LINE WIDTH, HEIGHT AND GAP WIDTH BASED ON FREQUENCY
    f = 0
    line_height_list = [6600,4000,3600,3000,2000,1500,1000]
    finger_freq_range = [1.8e6,1e6,2e6,3e6,4e6,5e6,6e6,7e6]
    l_um = line_height_list[0]
    while Frequency > finger_freq_range[f]:
        if Frequency > finger_freq_range[len(finger_freq_range) -1]:
            print("\nError!!! Frequency is out of range!\n")
            break 
        l_um = line_height_list[f]
        f = f + 1
        
    # calculate N   
    A1 = 4.409 * numpy.tanh( 0.55 * (h/W) ** (0.45)) * 1e-6 # (pF/um)
    A2 = 9.92 * numpy.tanh(0.52 * (h/W) ** (0.5)) * 1e-6   # (pF/um)

    print("A1 = %.2E (pF/um), A2 = %.2E (pF/um)" %(A1, A2))

    C_picoF = Cap * 1e12 # go from farad to pico farad
    #C = (er + 1) * l * ( (N-3) * A1 + A2)
    #?? C = (er + 1) * l * N*(1+gap/W)*( (N-3) * A1 + A2)
    # C / (  (er + 1) * l) = (N-3) * A1 + A2
    # ( C / ( (er + 1) * l ) - A2 ) / A1 = N -3
    # N = 3 + ( C / ( (er + 1) * l ) - A2 ) / A1
    
    N = int ( 3 + ( C_picoF / ( (er + 1) * l_um ) - A2 ) / A1 )
        
    print("N = %d , l = %.2E (um) " %(N, l_um))    
    return N, l_um # number of fingers, length of finger

# def CalculateCapacitanceFromFrequency( L, freq_array, nfreq):
    
#     if nfreq == 1:
#         desired_C = ( 1 / (2*numpy.pi * freq_array) ) ** 2 / L
#         return desired_C
    
#     else:
    
#         #nfreq = len(freq_array)
#         desired_C_array = numpy.zeros(nfreq)
    
#         for f in range(nfreq):
#             freq = freq_array[f]
#             desired_C_array[f] = ( 1 / (2*numpy.pi * freq) ) ** 2 / L
    
#     return desired_C_array