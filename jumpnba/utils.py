import matplotlib as mpl
from matplotlib import pyplot as plt
import base64
from io import BytesIO
def get_graph():
    buffer = BytesIO()
    plt.savefig(buffer, format='png', transparent=True)
    buffer.seek(0)
    image_png = buffer.getvalue()
    graph = base64.b64encode(image_png)
    graph = graph.decode('utf-8')
    buffer.close()
    return graph

def get_plot(_p):
    mpl.rcParams['font.size'] = 40
    plt.switch_backend('AGG')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    fig.figsize=(5,5)
    sizes = [_p,1-_p]

    ax.pie(sizes,
        shadow=True,startangle=90)
    
    ax.axis('equal')
    fig.subplots_adjust(top=0.99,left=0.01,right=0.99,bottom=0.01)
    graph = get_graph()
    return graph
