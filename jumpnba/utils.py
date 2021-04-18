import matplotlib as mpl
from matplotlib import pyplot as plt
import base64
from io import BytesIO

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(_p,c1,c2):
    mpl.rcParams['font.size'] = 40
    plt.switch_backend('AGG')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.figsize=(5,5)
    sizes = [_p,1-_p]

    ax.pie(sizes,
        shadow=True,startangle=90,colors=[c1,c2])
    
    ax.axis('equal')
    fig.subplots_adjust(top=0.99,left=0.01,right=0.99,bottom=0.01)
    graph = get_graph()
    return graph

def compare_colors(c1,c2):
    color1_rgb = sRGBColor.new_from_rgb_hex(c1)
    color2_rgb = sRGBColor.new_from_rgb_hex(c2)

    # Convert from RGB to Lab Color Space
    color1_lab = convert_color(color1_rgb, LabColor);
    color2_lab = convert_color(color2_rgb, LabColor);

    # Find the color difference
    delta_e = delta_e_cie2000(color1_lab, color2_lab);

    if delta_e>20:
        return 1
    else:
        return 0



