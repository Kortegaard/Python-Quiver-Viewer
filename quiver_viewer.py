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


pos=nx.spring_layout(G, iterations=50)

fig, ax = plt.subplots()


pick_radius = 4
node_size = 8
arrow_shrink = 7

def draw_quiver(Q, ax):
    def plot_point(point):
        pl = ax.plot(*point, 
                marker='o',
                picker=True,
                pickradius=pick_radius,
                markersize=node_size,
        )
        #pl[0].set_pickradius(pick_radius)

    for v in Q.nodes():
        #print(pos[v])
        plot_point(pos[v])

    #for u,v in G.edges():
    for u in Q.nodes():
        for v in Q.adj.get(u):
            num_u_v = len(Q.adj.get(u).get(v)) if Q.adj.get(u).get(v) else 0
            num_v_u = len(Q.adj.get(v).get(u)) if Q.adj.get(v).get(u) else 0
            total_between = num_u_v + num_v_u

            step = 0.35
            rad = total_between // 2 * step
            
            d = pos[v] - pos[u] #direction
            ud = d/sqrt((d**2).sum()) # unit direction

            shrink = 0.1
            pos_u = pos[u] + ud * shrink
            d = d - 2*ud * shrink
            

            for _ in range(num_u_v):
                arr = patches.FancyArrowPatch(pos[u], pos[v],
                    arrowstyle='simple , tail_width=0.5, head_width=4, head_length=8',
                    shrinkA = arrow_shrink,
                    shrinkB = arrow_shrink,
                    color="k",
                    connectionstyle="arc3,rad="+str(rad)+"",
                )
                ax.add_patch(arr)
                rad -= step

##------------------------- Events

def on_click_add_point(event):
    if event and event.dblclick :
        #TODO Check if there is another of this name
        node_name = str(G.number_of_nodes()+1)
        G.add_node(node_name)
        print(type(event.xdata))
        pos[node_name] = np.array([event.xdata, event.ydata])

        ax.cla()
        ax.set_xlim(-2,2)
        ax.set_ylim(-2,2)
        draw_quiver(G, ax)
        plt.draw()



is_dragging = False
dragging_artist_name = None

def on_pick(event):
    print("PICK")
    global dragging_artist_name
    artist_point = np.array(list(zip(*event.artist.get_data()))[0])
    for m in pos:
        if np.array_equal(pos[m], artist_point):
            dragging_artist_name = m


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

    pos[dragging_artist_name] = np.array([event.xdata, event.ydata])
    ax.cla()
    ax.set_xlim(-2,2)
    ax.set_ylim(-2,2)
    draw_quiver(G, ax)
    plt.draw()

    pass

fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('button_press_event', on_click_add_point)
fig.canvas.mpl_connect('button_press_event', on_click)
fig.canvas.mpl_connect('motion_notify_event', on_motion)




draw_quiver(G,ax)
plt.draw()


ax.set_xlim(-2,2)
ax.set_ylim(-2,2)
# ax.set_xlim(-1500,1500)
# ax.set_ylim(-1500, 1500)
ax.set_aspect('equal')
#plt.axis('off')
plt.grid(False)
plt.show()



