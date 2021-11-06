import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from math import sqrt, floor
try:
    import matplotlib.pyplot as plt
except:
    raise 

import networkx as nx
import math
try:
    from networkx import graphviz_layout
    layout=nx.graphviz_layout
except ImportError:
    print("PyGraphviz not found; drawing with spring layout; will be slow.")
    layout=nx.spring_layout


G = nx.MultiDiGraph()
G.add_edge('1','2')
G.add_edge('1','2')
G.add_edge('1','2')
G.add_edge('1','3')
G.add_edge('3','2')
G.add_edge('3','4')
G.add_edge('4','3')


#pos=nx.spring_layout(G, iterations=50)

fig, ax = plt.subplots()

class QuiverPlot:

    Q = None
    
    plt = None
    ax = None

    pos = None

    pick_radius = 4
    node_size = 8
    arrow_shrink = 7

    xlim = (-2,2)
    ylim = (-2,2)

    def __init__(self, quiver = None):
        self.Q = quiver
        self.refresh_layout()
        pass

    def get_node_at_pos(self, point):
        for p in self.pos:
            if np.array_equal(self.pos[p], point):
                return p
        return None

    def set_node_pos(self, node_name, point):
        self.pos[node_name] = np.array(point)

    def refresh_layout(self):
        if self.Q != None:
            self.pos=nx.spring_layout(self.Q, iterations=50)

    def set_quiver(self, Q):
        self.Q = Q
        self.refresh_layout()

    def redraw_quiver(self):
        ax.cla()
        ax.set_xlim(*self.xlim)
        ax.set_ylim(*self.ylim)
        self.plot_quiver_vertices()
        self.plot_quiver_arrows()
        plt.draw()


    def plot_quiver_vertices(self):
        for v in self.Q.nodes():
            self._plot_point(self.pos[v])

    def plot_quiver_arrows(self):
        for u in self.Q.nodes():
            for v in self.Q.adj.get(u):
                num_u_v = len(self.Q.adj.get(u).get(v)) if self.Q.adj.get(u).get(v) else 0
                num_v_u = len(self.Q.adj.get(v).get(u)) if self.Q.adj.get(v).get(u) else 0
                total_between = num_u_v + num_v_u

                step = 0.35
                rad = total_between // 2 * step
                
                d = self.pos[v] - self.pos[u] #direction
                ud = d/sqrt((d**2).sum()) # unit direction

                shrink = 0.1
                self.pos_u = self.pos[u] + ud * shrink
                d = d - 2*ud * shrink
                

                for _ in range(num_u_v):
                    arr = patches.FancyArrowPatch(self.pos[u], self.pos[v],
                        arrowstyle='simple , tail_width=0.5, head_width=4, head_length=8',
                        shrinkA = self.arrow_shrink,
                        shrinkB = self.arrow_shrink,
                        color="k",
                        connectionstyle="arc3,rad="+str(rad)+"",
                    )
                    ax.add_patch(arr)
                    rad -= step

    def _plot_point(self, point):
        pl = self.ax.plot(*point, 
                marker = 'o',
                picker = True,
                pickradius = self.pick_radius,
                markersize = self.node_size,
        )




##------------------------- Events

is_dragging = False
dragging_artist_name = None

qp = QuiverPlot(G)
qp.ax = ax
qp.plt = plt


def on_click_add_point(event):
    if event and event.dblclick :
        #TODO Check if there is another of this name
        node_name = str(qp.Q.number_of_nodes()+1)
        qp.Q.add_node(node_name)
        print(type(event.xdata))
        qp.set_node_pos(node_name, [event.xdata, event.ydata])
        qp.redraw_quiver()



def on_pick(event):
    print("PICK")
    global dragging_artist_name
    artist_point = np.array(list(zip(*event.artist.get_data()))[0])
    dragging_artist_name = qp.get_node_at_pos(artist_point)

def on_click(event):
    print("DRAG")
    global is_dragging
    is_dragging = True

def on_release(event):
    print("RELEASE")
    global is_dragging, dragging_artist_name
    is_dragging = False
    dragging_artist_name = None

def on_motion(event):
    global is_dragging, dragging_artist_name, ax, pos

    if not is_dragging or dragging_artist_name == None:
        return
    print("HERE")

    qp.set_node_pos(dragging_artist_name,[event.xdata, event.ydata])
    qp.redraw_quiver()


fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('button_press_event', on_click_add_point)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_motion)




# ax.set_xlim(-1500,1500)
# ax.set_ylim(-1500, 1500)
ax.set_aspect('equal')
#plt.axis('off')
# plt.grid(False)
# plt.show()


qp.redraw_quiver()
plt.show()

