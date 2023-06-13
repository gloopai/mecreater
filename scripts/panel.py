'''
Author: acheqi@126.com acheqi@126.com
Date: 2023-06-13 23:03:42
LastEditors: acheqi@126.com
LastEditTime: 2023-06-14 02:18:58
Description: 
'''



import modules.scripts as scripts
import gradio as gr
import os

from modules import images, script_callbacks
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state


 # 比例计算
def params_bl(t):
    if t =='横版':
        return 960,540
    if t =='竖版':
        return 540,960
    return 0,0

# 常用坏图反向词
ht_fx_ci= 'lowres,bad anatomy,bad hands,text,error, missing fingers, extra digit,fewer digits,cropped,worst quality,low quality,normal quality,jpeg artifacts,signature,watermark,username,blurry'

# 风格
fg_data = ["随机","artbook/原画", "game_cg/游戏CG", "comic/漫画"]
fg_map = {
     "artbook/原画":"artbook",
     "game_cg/游戏CG":"game_cg",
     "comic/漫画":"comic"
}
# 清晰度
qxd_data = ["默认", "清晰","4k","8k"]
qxd_map = {
     "清晰":"best quality",
     "4k":"masterpiece,best quality,official art,extremely detailed CG unity 4k wallpaper",
     "8k":"masterpiece,best quality,official art,extremely detailed CG unity 8k wallpaper"
}


class ExtensionTemplateScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
                return "MeCreatePanel"

        def show(self, is_img2img):
                return scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
                with gr.Accordion('MeCreater(AI网文助手)', open=False):
                        with gr.Row():
                            with gr.Column(scale=2):
                                bl = gr.Radio(["横版", "竖版","自定义"],value="自定义", label="比例", info="横版960x540,竖版540x960，自定义使用默认设置")
                            with gr.Column(scale=2):
                                ht = gr.CheckboxGroup(["选择"], label="减少坏图", info="会添加一些常用的坏图反向词")
                        # with gr.Row():
                        #     content = gr.TextArea(label="分镜脚本", info="输入分镜脚本(英文),每一段之间用 一个空行 隔开")
                        with gr.Row():
                            with gr.Column(scale=2):
                                fg = gr.Dropdown(fg_data, label="风格", info="选择画风",value="随机")
                            with gr.Column(scale=2):
                                qxd = gr.Radio(qxd_data,value="默认", label="清晰度", info="生成画面的清晰度")

                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return [bl,ht,fg,qxd]

        def process(self, p, bl,ht,fg,qxd):
            # 设置比例
            if bl !='自定义':
                w,h = params_bl(bl)
                p.width = w
                p.height= h
            
            newprompt = []
            # 清晰度
            if qxd in qxd_map:
                 newprompt.append(qxd_map[qxd])
            # 风格
            if fg in fg_map:
                 newprompt.append(fg_map[fg])

            # 生成新的正向词
            newprompt.append(p.prompt)
            promptstr = ",".join(newprompt)
            p.prompt =promptstr
            newpromptarr = []
            for item in p.all_prompts:
                 newpromptarr.append(p.prompt) 

            p.all_prompts = newpromptarr


            # 生成新的反向词
            if ht == ['选择']:
                htnewprompt = []
                htnewprompt.append(ht_fx_ci)
                htnewprompt.append(p.negative_prompt)
                htfxstr = ",".join(htnewprompt)
                p.negative_prompt = htfxstr
                newhtfxarr = []
                for item in p.all_negative_prompts:
                    newhtfxarr.append(p.negative_prompt)
                p.all_negative_prompts =  newhtfxarr