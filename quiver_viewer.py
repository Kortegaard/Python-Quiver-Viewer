import numpy as np
import pyperclip
import matplotlib.patches as patches
import matplotlib.pyplot as plt

import networkx as nx
from math import sqrt, floor, comb, sin, cos

from matplotlib.widgets import TextBox

import re, json

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


#### ---------------- HELPER FUNCTIONS

def bernstein_poly(i, n, t):
    return comb(n, i) * ( t**(n-i) ) * (1 - t)**i


def bezier_curve(points, nTimes=1000, start_t = 0.0, end_t = 1.0):

    nPoints = len(points)
    xPoints = np.array([p[0] for p in points])
    yPoints = np.array([p[1] for p in points])

    t = np.linspace(start_t, end_t, nTimes)

    polynomial_array = np.array([ bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)   ])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    return xvals, yvals

def plot_self_bezier_curve(point, direction, angle, weight,  start_t = 0.0, end_t = 1.0, ax=None, color='k', pickradius = 1, picker = True):
    theta = np.deg2rad(angle)
    rot = np.array([[cos(theta), -sin(theta)], [sin(theta), cos(theta)]])
    backrot = np.array([[cos(theta), sin(theta)], [-sin(theta), cos(theta)]])

    unit_direction = direction / sqrt((direction**2).sum())
    d1 = np.dot(rot, unit_direction)
    d2 = np.dot(backrot, unit_direction)
    
    curve = bezier_curve(np.array([point,point + d1 * weight, point + d2 * weight ,point]), start_t = start_t, end_t = end_t)

    # Arrow for the head
    arr = patches.FancyArrowPatch(np.array([curve[0][-2], curve[1][-2]]), np.array([curve[0][-1], curve[1][-1]]),
        arrowstyle='simple, tail_width=0.5, head_width=4, head_length=8',
        capstyle='round',
        color=color,
    )
    ax.add_patch(arr)
    curve_patch = ax.plot(curve[0][0:-1], curve[1][0:-1], color, pickradius = pickradius, picker = picker)
    return curve_patch[0]



#### -------------QUIVERPLPOT

class QuiverPlot:

    Q = None
    
    fig = None
    ax = None

    pos = None

    pick_radius = 4
    node_size = 8
    arrow_shrink = 7

    xlim = (-4,4)
    ylim = (-2.5,2.5)


    edge_patches = []
    node_patches = []

    def __init__(self, quiver = None, fig = None , ax =  None):
        self.fig = fig
        self.ax = ax
        self.Q = quiver
        self.refresh_layout()
        self.connect_events()
        pass

    def set_quiver(self, Q):
        self.ax.cla()
        self.edge_patches = []
        self.node_patches = []
        self.pos = None
        self.Q = Q
        self.refresh_layout()
        self.redraw_quiver()
        #pls.draw()

    def get_node_at_pos(self, point):
        for p in self.pos:
            if np.array_equal(self.pos[p], point):
                return p
        return None

    def set_node_pos(self, node_name, point):
        self.pos[node_name] = np.array(point)

    def refresh_layout(self):
        if self.Q != None:
            self.pos=nx.spring_layout(self.Q, iterations=100)

    def set_quiver(self, Q):
        self.Q = Q
        self.refresh_layout()
        self.redraw_quiver()

    def redraw_quiver(self):
        # self.xlim = ax.get_xlim()
        # self.ylim = ax.get_ylim()
        self.ax.cla()
        self.ax.set_xlim(*self.xlim)
        self.ax.set_ylim(*self.ylim)
        self.plot_quiver_vertices()
        self.plot_quiver_arrows()
        plt.draw()
        
    def plot_quiver_vertices(self):
        for v in self.Q.nodes():
            pl = self._plot_point(self.pos[v])
            self.node_patches.append((pl, v))

    def plot_quiver_arrows(self):
        for u in self.Q.nodes():
            for v in self.Q.adj.get(u):
                u_to_v = self.Q.adj.get(u).get(v) or dict()
                v_to_u = self.Q.adj.get(v).get(u) or dict()

                num_u_v = len(u_to_v)
                num_v_u = len(v_to_u)

                total_between = num_u_v + num_v_u

                if u == v:
                    for index in u_to_v:
                        arr_info = u_to_v[index]

                        arr_direction = arr_info.get('direction', np.array([1,1]))
                        arr_info['direction'] = arr_direction

                        arr_magnitude = arr_info.get('magnitude', 1)
                        arr_info['magnitude'] = arr_magnitude

                        arr_angle = arr_info.get('angle', 40)
                        arr_info['angle'] = arr_angle

                        arr_info['point'] = u

                        arr = plot_self_bezier_curve(self.pos[u], arr_direction, arr_angle, arr_magnitude, 0.05, 0.95, ax=self.ax, pickradius=self.pick_radius, picker=True)
                        self.edge_patches.append((arr,arr_info))

                step = 0.35
                rad = total_between // 2 * step
                if u == v:
                    rad = 1
                
                shrink = 0.1
                

                for _ in range(num_u_v):
                    arr = patches.FancyArrowPatch(self.pos[u], self.pos[v],
                        arrowstyle='simple, tail_width=0.5, head_width=4, head_length=8',
                        capstyle='round',
                        shrinkA = self.arrow_shrink,
                        shrinkB = self.arrow_shrink,
                        color="k",
                        connectionstyle="arc3,rad="+str(rad)+"",
                    )
                    self.ax.add_patch(arr)
                    rad -= step

    def _plot_point(self, point):
        pl = self.ax.plot(*point, 
                marker = 'o',
                picker = True,
                pickradius = self.pick_radius,
                markersize = self.node_size,
        )
        return pl[0]

    def connect_events(self):
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        self.fig.canvas.mpl_connect('pick_event', self.on_pick)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click_add_point)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_motion)

    is_dragging = False
    is_dragging_edge = False
    is_dragging_node= False
    dragging_artist_name = None
    draggin_info = None
    
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
        print(event.artist)
        for i, patch in enumerate(self.node_patches):
            if event.artist == patch[0]:
                self.is_dragging_node = True
                self.draggin_info = patch[1]
                break
        for i, patch in enumerate(self.edge_patches):
            if event.artist == patch[0]:
                self.is_dragging_edge = True
                self.draggin_info = patch[1]
                break
        #artist_point = np.array(list(zip(*event.artist.get_data()))[0])
        #self.dragging_artist_name = self.get_node_at_pos(artist_point)

    def on_click(self, event):
        print("DRAG")
        self.is_dragging = True

    def on_release(self, event):
        print("RELEASE")
        self.is_dragging_edge = False
        self.is_dragging_node = False
        self.is_dragging = False
        self.dragging_artist_name = None
        draggin_info = None

    def on_motion(self, event):
        if not self.is_dragging or self.draggin_info == None:
            return
        if self.is_dragging_node:
            self.set_node_pos(self.draggin_info,[event.xdata, event.ydata])
        if self.is_dragging_edge:
            mouse_point = np.array([event.xdata, event.ydata])
            direction = mouse_point - self.pos[self.draggin_info['point']]

            self.draggin_info['direction'] = direction
            self.draggin_info['magnitude'] = sqrt((direction**2).sum()) * 1.7
        self.redraw_quiver()




def load_gap_quiver(string):
    pure_gap_string = "[" + re.findall(r'Quiver\(\s+(.*)\s+\)', string)[0] + "]"
    gap_quiver_arr = json.loads(pure_gap_string)
    G = nx.MultiDiGraph()
    G.add_nodes_from(gap_quiver_arr[0])
    G.add_edges_from(list(map(tuple, gap_quiver_arr[1])))
    return G

##-----------------------------------------------------------------------------------------------------



fig, ax = plt.subplots()
plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
# plt.subplots_adjust(bottom=0.2)
ax.axes.get_xaxis().set_visible(False)
ax.axes.get_yaxis().set_visible(False)

k = 'Quiver( ["u","v"], [["u","u","a"],["u","v","b"],["v","u","c"],["v","v","d"]] )'
ax.set_autoscaley_on(True)
qp = QuiverPlot(load_gap_quiver(k), fig, ax)


def on_key(event):

    print(event.key)
    global qp
    if event.key in ["ctrl+V", "cmd+V", "ctrl+v", "cmd+v"]:
        print("SET QUIVER")
        try:
            q = load_gap_quiver(pyperclip.paste())
            qp.set_quiver(q)

        except:
            print("Err")
fig.canvas.mpl_connect('key_press_event', on_key)


# def submit(text):
#     global qp
#     try:
#         q = load_gap_quiver(text)
#         qp.set_quiver(q)
#     except:
#         print("Err")

# axbox = plt.axes([0.1, 0.05, 0.8, 0.075])
# l = 'Quiver( ["u","v"], [["u","u","a"],["u","v","b"],["v","u","d"]] )'
# text_box = TextBox(axbox, 'Evaluate', initial=l)
# text_box.on_submit(submit)

plt.draw()
ax.set_aspect('equal')
qp.redraw_quiver()
plt.show()

