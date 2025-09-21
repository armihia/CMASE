import re

from matplotlib.ticker import MaxNLocator, FuncFormatter

from env import Env
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter
import seaborn as sns
from scipy.interpolate import make_interp_spline

def draw(data,xlabel,ylabel,title=""):
    if(str(type(data))=="<class 'dict'>"):
        unique_keys=list(data.keys())
        time_series=data
        time_slots=len(data[unique_keys[0]])
    else:
        unique_keys = sorted({element for sublist in data for element in sublist})
        time_slots = len(data)

        counters = [Counter(time_slot) for time_slot in data]
        time_series = {
            key: [counters[i].get(key, 0) for i in range(time_slots)]
            for key in unique_keys
        }
    print(unique_keys)
    print(time_series)

    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.2)
    plt.figure(figsize=(10, 6), dpi=100)
    palette = sns.color_palette("husl", n_colors=len(unique_keys))

    x_ticks = np.array(range(time_slots))
    x_smooth = np.linspace(x_ticks.min(), x_ticks.max(), 300)

    for idx, key in enumerate(unique_keys):
        y_original = np.array(time_series[key])

        if len(x_ticks) > 3:
            spline = make_interp_spline(x_ticks, y_original, k=min(3, len(x_ticks) - 1))
        else:
            spline = make_interp_spline(x_ticks, y_original, k=1)

        y_smooth = spline(x_smooth)

        plt.plot(
            x_smooth,
            y_smooth,
            color=palette[idx],
            linewidth=2.5,
            alpha=0.8,
            zorder=1
        )
        plt.scatter(
            x_ticks,
            y_original,
            color=palette[idx],
            s=120,
            edgecolor='white',
            linewidth=2,
            zorder=2,
            label=key
        )

    plt.title(title, fontsize=14, pad=20)
    plt.xlabel(xlabel, fontsize=40, labelpad=10)
    plt.ylabel(ylabel, fontsize=40, labelpad=10)

    plt.grid(True, which='major', linestyle='--', alpha=0.7)
    plt.grid(True, which='minor', linestyle=':', alpha=0.4)
    plt.minorticks_on()

    handles, labels = plt.gca().get_legend_handles_labels()
    plt.legend(
        handles, labels,
        frameon=True,
        loc='upper left',
        bbox_to_anchor=(1, 0.95),
        fontsize=10,
        title_fontsize=11
    )

    ax = plt.gca()
    ax.xaxis.set_major_locator(MaxNLocator(nbins='auto', steps=[1, 2, 5, 10], integer=True))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'Step {int(x) + 1}'))
    plt.xticks(rotation=45, ha='right', fontsize=18)
    plt.yticks(fontsize=18)

    max_value = max(max(v) for v in time_series.values())
    min_value = min(min(v) for v in time_series.values())
    if(min_value>0):
        min_value*=0.8
    elif (min_value == 0):
        min_value = max_value*-0.1
    else:
        min_value *= 1.2
    plt.ylim(1.2 * min_value, max_value * 1.2)

    sns.despine(left=True, bottom=True)
    plt.gca().spines['bottom'].set_color('#808080')
    plt.gca().spines['left'].set_color('#808080')

    plt.tight_layout()
    plt.show()

def degree2num(d):
    if (d == "high"):
        return 1
    if(d=="relatively high"):
        return 0.5
    if (d == "low"):
        return -1
    if(d=="relatively low"):
        return -0.5
    if (d == "medium"):
        return 0

data=[]
data1=[]
for i in range(1,51):
    print("Reading step ",i)
    e=Env(None,None,"./env file/auto_save_"+str(i)+".dill",only_read=True)

    space_list0=[]
    vad_list0=[]
    for num in range(len(e.agents.agent_list)):
        pos=e.agents.agent_list[num].pos
        a0=None
        a0_n=10000000
        for a in e.mm.areas.keys():
            if(pos in e.mm.areas[a] and a!=0):
                if(len(e.mm.areas[a])<a0_n):
                    a0_n=len(e.mm.areas[a])
                    a0=a
        n = re.findall(r"Area Name: (.*?)\n", e.mm.description["area"][a0])[0]
        if("House" in n):
            n="Indoor"
        elif("outside" in n):
            n="Street"
        else:
            n="Park"
        space_list0.append(n)

        vad=e.agents.agent_list[num].vad
        v=degree2num(vad["arousal"])+degree2num(vad["valence"])+degree2num(vad["dominance"])
        vad_list0.append(v)
    data.append(space_list0)

    vad_list={}
    for s in ["Indoor","Street","Park"]:
        vad_list[s]=[]
    for v in range(len(vad_list0)):
        vad_list[space_list0[v]].append(vad_list0[v])
    for v in vad_list.keys():
        if(len(vad_list[v])==0):
            vad_list[v]=0
        else:
            vad_list[v]=sum(vad_list[v])/len(vad_list[v])
    data1.append(vad_list)
print(data1)

draw(data,'','')

data={}
for s in ["Indoor","Park","Street"]:
    data[s]=[]
for i in data1:
    for k in data.keys():
        data[k].append(i[k])
draw(data,'','')