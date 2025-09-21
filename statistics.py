import re

import numpy as np
import pygame
from PIL import Image, ImageDraw, ImageFont

def statistics(env):
    area_set = set(np.unique(env.mm.map_list[-1]))
    if(0 in area_set):
        area_set.remove(0)
    area_agent_num={}
    for i in area_set:
        area_agent_num[i]=[]


    for agent in env.agents.agent_list:
        area = env.mm.map_list[-1, agent.pos[0], agent.pos[1]]
        area_agent_num[area].append(agent)

    draw_dict={}
    for i in area_agent_num.keys():
        try:
            i0=re.findall(r"Area Name: (.*?)\n", env.mm.description["area"][i])[0]
        except:
            i0=str(i)
        draw_dict[i0]=len(area_agent_num[i])

    img=create_bar_chart(draw_dict,(env.msg_x,env.msg_x))

    pygame_img = pygame.image.fromstring(img.tobytes(), img.size, img.mode)

    return pygame_img


def create_bar_chart(data,size=(600,600)):
    width, height = size
    width=int(width)
    height=int(height)
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    label_len = 7

    margins = {
        "left": int(width*0.15),
        "right": int(width*0.08),
        "top": int(height*0.08),
        "bottom": int(height*0.15)
    }
    plot_area = {
        "width": width - margins["left"] - margins["right"],
        "height": height - margins["top"] - margins["bottom"]
    }

    max_value = max(data.values()) if data else 1
    num_bars = len(data)
    if num_bars == 0:
        return

    bar_width = (plot_area["width"] * 0.8) / num_bars
    spacing = (plot_area["width"] * 0.2) / (num_bars + 1)

    axes = {
        "y_start": (margins["left"], height - margins["bottom"]),
        "y_end": (margins["left"], margins["top"]),
        "x_start": (margins["left"], height - margins["bottom"]),
        "x_end": (width - margins["right"], height - margins["bottom"])
    }
    draw.line([axes["y_start"], axes["y_end"]], fill="black", width=2)
    draw.line([axes["x_start"], axes["x_end"]], fill="black", width=2)

    try:
        font = ImageFont.truetype("times.ttf", 8)
    except:
        font = ImageFont.load_default()

    scale_show_num=6
    for i in range(scale_show_num):
        y_pos = height - margins["bottom"] - int((i / (scale_show_num-1)) * plot_area["height"])
        value = max_value * (i / (scale_show_num-1))

        draw.line([(margins["left"] - (scale_show_num-1), y_pos), (margins["left"], y_pos)], fill="black")

        text = f"{value:.1f}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        draw.text(
            xy=(margins["left"] - text_w - 10, y_pos - text_h // 2),
            text=text,
            fill="black",
            font=font
        )

    for idx, (label, value) in enumerate(data.items()):
        x_start = margins["left"] + spacing + idx * (bar_width + spacing)
        y_start = height - margins["bottom"] - int((value / max_value) * plot_area["height"])
        x_end = x_start + bar_width
        y_end = height - margins["bottom"] - 1

        try:
            draw.rectangle([x_start, y_start, x_end, y_end], fill="blue")
        except:
            pass

        bbox = draw.textbbox((0, 0), label, font=font)
        label_w = bbox[2] - bbox[0]
        label_h = bbox[3] - bbox[1]

        if(len(label)>label_len):
            label0=[]
            for i in range(int(len(label)/label_len)):
                label0.append(label[i*label_len:(i+1)*label_len])
            if(int(len(label)/label_len)!=len(label)/label_len):
                label0.append(label[(int(len(label)/label_len)) * label_len:])
            label="\n".join(label0)
        draw.text(
            xy=(x_start, height - margins["bottom"] + 10),
            text=label,
            fill="black",
            font=font
        )

    #img.save("chart.png")
    return img


