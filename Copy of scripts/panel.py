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
        return 450,300
    if t =='竖版':
        return 300,450
    return 0,0

# 景深
def params_yuanjin(t):
    t = int(t)
    if t == 0:
        return ""
    elif t < 0:
        return '(' * abs(t) + 'close-up,' + ')' * abs(t)
    else:
        return '(' * t + 'Full body panoramic view,' + ')' * t
    

# 分镜使用帮助
fenjing_tips = """
                #### 使用方法

                ##### 第一步:在提示词中每行一个分镜输入英文提示词

                ```
                    注意:每个分镜脚本放一行，会根据每行进行自动分割
                    
                    如：
                    gril, car,short hair,red hair, sports bra , 
                    boy, sea,short hair,black hair,  
                ```
                ##### 第二步:根据分镜数量设置 生成批次(Batch count)和单批数量(Batch size)
                ```
                    注意: 这一步一定不能漏，否则会出现生成索引溢出的错误
                    设置计算公式为: 分镜数量 = Batch count * Batch size
                    如：分镜数量 2
                    设置 生成批次(Batch count) 为 1
                    设置 单批数量(Batch size) 为 2
                     
                ```
                ##### 第三步:打开分镜切割开关
                ```
                    确认分镜切割已经勾选
                ```
                ##### 第四步:点击生成图片
                ```
                    等待图片生成完成
                ```

                """

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
                with gr.Accordion('AI漫文老司机', open=False):
                    with gr.Tab("分镜"):
                        with gr.Row():
                            with gr.Column(scale=2):
                                auto_split = gr.CheckboxGroup(["开启"], label="分镜切割", info="会根据提示词换行分割分镜，注意: 分镜数量(提示词行数) = (批次)Batch count * (单批数量)Batch size 需手动设置")
                        with gr.Row():
                             gr.Markdown(fenjing_tips)
                    with gr.Tab("画面"):
                        with gr.Row():
                            with gr.Column(scale=2):
                                bl = gr.Radio(["横版", "竖版","自定义"],value="自定义", label="比例", info="横版450x300,竖版300x450，自定义使用默认设置")
                            with gr.Column(scale=2):
                                ht = gr.CheckboxGroup(["选择"], label="减少坏图", info="会添加一些常用的坏图反向词")
                        with gr.Row():
                            with gr.Column(scale=2):
                                qxd = gr.Radio(qxd_data,value="默认", label="清晰度", info="生成画面的清晰度")
                            with gr.Column(scale=2):
                                yuanjin = gr.Slider(minimum=-6,maximum=6 , value=0, label="画面远近", info="数值越小，人像越大,数值越大人像越大，但是越容易崩脸，所有图片生效")
                    with gr.Tab("风格"):
                         with gr.Row():
                              with gr.Column(scale=2):
                                fg = gr.Dropdown(fg_data, label="风格", info="选择画风",value="随机")
                    with gr.Tab("其他"):
                         gr.Label("开发中")
                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return [auto_split,bl,ht,fg,qxd,yuanjin]

        def process(self, p,auto_split, bl,ht,fg,qxd,yuanjin):
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

            # 画面远近
            newprompt.append(params_yuanjin(yuanjin))


            # 生成新的正向词
            promptstr = ",".join(newprompt)

            if auto_split!=["开启"]:
                p.prompt = f'{promptstr},{p.prompt}'
            else:
                 # 处理脚本分段
                oldPromptArr = []
                oldPromptArr = p.prompt.split("\n")
                newpromptarr = []
                for i in oldPromptArr:
                    item = ""
                    item = f'{promptstr},{i}'
                    newpromptarr.append(item)

                p.all_prompts = newpromptarr
                p.prompt = ""
                

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