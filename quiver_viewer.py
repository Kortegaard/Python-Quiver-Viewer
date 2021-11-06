import numpy as np
import matplotlib.patches as patches
import matplotlib.pyplot as plt

import networkx as nx
from math import sqrt, floor

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


class QuiverPlot:

    Q = None
    
    fig = None
    ax = None

    pos = None

    pick_radius = 4
    node_size = 8
    arrow_shrink = 7

    xlim = (-2,2)
    ylim = (-2,2)

    def __init__(self, quiver = None, fig = None , ax =  None):
        self.fig = fig
        self.ax = ax
        self.Q = quiver
        self.refresh_layout()
        self.connect_events()
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

    def connect_events(self):
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click_add_point)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    is_dragging = False
    dragging_artist_name = None

    def on_click_add_point(self,event):
        if event and event.dblclick :
            #TODO Check if there is another of this name
            node_name = str(self.Q.number_of_nodes()+1)
            self.Q.add_node(node_name)
            print(type(event.xdata))
            self.set_node_pos(node_name, [event.xdata, event.ydata])
            self.redraw_quiver()

    def on_pick(self, event):
        print("PICK")
        artist_point = np.array(list(zip(*event.artist.get_data()))[0])
        self.dragging_artist_name = self.get_node_at_pos(artist_point)

    def on_click(self, event):
        print("DRAG")
        self.is_dragging = True

    def on_release(self, event):
        print("RELEASE")
        self.is_dragging = False
        self.dragging_artist_name = None

    def on_motion(self, event):
        if not self.is_dragging or self.dragging_artist_name == None:
            return
        print("HERE")
        self.set_node_pos(self.dragging_artist_name,[event.xdata, event.ydata])
        self.redraw_quiver()


##-----------------------------------------------------------------------------------------------------


fig, ax = plt.subplots()
qp = QuiverPlot(G, fig, ax)

ax.set_aspect('equal')
qp.redraw_quiver()
plt.show()

