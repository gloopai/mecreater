'''
Author: acheqi@126.com acheqi@126.com
Date: 2023-06-13 23:03:42
LastEditors: acheqi@126.com
LastEditTime: 2023-06-14 02:18:58
Description: 
'''



import json
import requests
import random
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
yuanjin_list = [-3,-2,-1,0,1,2,3]
# 随机远近
def params_random_yuanjin():
    return params_yuanjin(random.choice(yuanjin_list))
    

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

                    再次注意:这里的计算结果数量一定要和提示词输入框中的分镜条数对应
                     
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
fenjing_jingxi_tips = """
    ```
    精细分镜是基于开启了快速分镜之后才会生效的配置，如果要进行精细分镜控制，需要先开启快速分镜
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

# 构图
goutu_list = ["captivating",
               "mesmerizing", 
               "spellbinding", 
               "striking", 
               "alluring", 
               "shadowy", 
               "menacing", 
               "eerie", 
               "elusive", 
               "intriguing", 
               "contemplative", 
               "reflective", 
               "evocative", 
               "wistful", 
               "pensive", 
               "calm", 
               "placid", 
               "tumultuous", 
               "frenetic", 
               "bewildering", 
               "dreamlike", 
               "mystical", 
               "ethereal"]

# 随机构图
def params_random_goutu():
    return random.choice(goutu_list)


# 镜头
jingtou_list = ["Close-up,crab shot", 
                "floor level shot", 
                "knee-level shot", 
                "hip-level shot", 
                "kaleidoscope shot", 
                "infrared shot", 
                "thermal imaging shot",
                "Bird's eye view", 
                "High angle shot",  
                "Worm's eye view ",
                "God's eye view",  
                "drone shot", 
                "bullet time shot", 
                "snorricam shot", 
                "tilt-shift shot", 
                "anamorphic shot", 
                "360-degree shot", 
                "aerial shot", 
                "telescopic shot", 
                "microscopic shot",  
                "chest-level shot", 
                "sky-level shot", 
                "under-water shot", 
                "split diopter shot", 
                "low-key shot", 
                "high-key shot", 
                "silhouette shot", 
                "night vision shot", 
                "slow motion shot",  
                "extreme close-up", 
                "medium close-up", 
                "medium shot", 
                "medium long shot", 
                "long shot", 
                "extreme long shot", 
                "full shot", 
                "cowboy shot", 
                "bird's eye view", 
                "worm's eye view", 
                "high angle", 
                "low angle", 
                "Dutch angle", 
                "straight-on angle", 
                "over-the-shoulder shot", 
                "point-of-view shot", 
                "two-shot", 
                "three-shot", 
                "establishing shot", 
                "cutaway shot", 
                "reaction shot", 
                "insert shot", 
                "off-screen shot", 
                "reverse angle" , 
                "bottom shot", 
                "tilt shot", 
                "pan shot", 
                "zoom in shot", 
                "zoom out shot", 
                "dolly in shot", 
                "dolly out shot", 
                "tracking shot", 
                "steadicam shot", 
                "handheld shot", 
                "crane shot", 
                "aerial shot", 
                "split screen shot", 
                "freeze frame shot"]
# 随机构图
def params_random_jingtou():
    return random.choice(jingtou_list)



def params_storyboard_rule(index,rule):
    try:
        ruleJson = json.load(rule)
        print(ruleJson)
    except:
        return "" 
     


yunduan_tips = """
    ```
        云端脚本功能和插件其他功能是互斥的，使用云端脚本时，[AI漫文创作助手]其他功能的配置不会生效
        如果需要使用插件配置功能，点击[卸载云端脚本]即可
    ```
"""

yunduan_tips_status = False 
yunduan_task =  []

# 加载数据  
def yunyuan_load(guid,page):
    global yunduan_task
    params = {"app_key":"bc01b43c-a0e2-4007-ad09-033b95cf1d6e", "method":"ai.center","data":{"command":"storyboard.task.get.by.webui","data":{"page":page,"task_guid":guid}}}
    header = {"x-token":""}
    try:
        res = requests.post(url="https://api.xiweiapp.com/v2/client",json=params,headers=header)
        if res.status_code!=200:
            return "云端脚本加载失败"
        resjson = res.json()
        if resjson['code']==50000:
            return resjson['message']
        if resjson['code'] == 20002:
            return resjson['message']
        data = resjson['data']
        for item in data:
            yunduan_task.append(item)
        if resjson['code']!=20001:
            yunyuan_load(guid,page+1)
        else:
            resmsg = f'云端脚本 {guid} 加载完成，共计 {len(yunduan_task)} 个分镜'
            print(resmsg)
            return  resmsg#resjson['message']
    except Exception as err:
        return f"{err}"

# 读取远程脚本
def yunduan_read_action(_p_yunduan_id):
    if  _p_yunduan_id== '':
        return "请先输入云端脚本 GUID"
    global yunduan_task
    yunduan_task = []
    return yunyuan_load(_p_yunduan_id,1)
    
# 清理云端脚本
def yunduan_clear_action():
    # print(yunduan_task)
    global yunduan_task
    yunduan_task = []
    return "","云端脚本卸载完成"

class ExtensionTemplateScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
                return "MeCreatePanel"

        def show(self, is_img2img):
                return scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
                with gr.Accordion('AI漫文创作助手', open=False):
                    with gr.Tab("快速分镜"):
                        with gr.Row():
                            with gr.Column(scale=2):
                                auto_split = gr.CheckboxGroup(["开启"], label="分镜切割", info="会根据提示词换行分割分镜，注意: 分镜数量(提示词行数) = (批次)Batch count * (单批数量)Batch size 需手动设置")
                        with gr.Row():
                             gr.Markdown(fenjing_tips)
                    with gr.Tab("精细分镜"):
                        with gr.Row():
                            gr.Markdown(fenjing_jingxi_tips)
                        with gr.Row():
                                yuanjin_suiji = gr.Checkbox(value=False, label="远近随机", info="开启后人物远近随机")
                                goutu_suiji = gr.Checkbox(value=False, label="构图随机", info="开启后人物和构图随机")
                                jintou_suiji =  gr.Checkbox(value=False, label="镜头随机", info="开启后出图镜头角度随机")
                       
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
                                yuanjin = gr.Slider(minimum=-6,maximum=6 , value=0, label="画面远近", info="数值越小，人像越大,数值越大人像越大，但是越容易崩脸，所有图片生效,另外如果配置了随机远近，这项配置不生效")
                    with gr.Tab("风格"):
                         with gr.Row():
                              with gr.Column(scale=2):
                                fg = gr.Dropdown(fg_data, label="风格", info="选择画风",value="随机")

                    with gr.Tab("云端脚本"):
                        with gr.Row():
                            gr.Markdown(yunduan_tips)
                        with gr.Row():
                            with gr.Column(scale=1):
                                yunduan_id = gr.Text(label="输入云端脚本ID",info="输入云端脚本ID后,点击[加载云端脚本],配置才会生效")
                        with gr.Row():
                                yunduan_status = gr.Textbox(label="加载状态",value="未读取",info="请在这里显示加载成功后再进行图片生成")
                        with gr.Row():
                            with gr.Column(scale=1):
                                yunduan_read= gr.Button(value="加载云端脚本",)
                                yunduan_read.click(yunduan_read_action,inputs=[yunduan_id], outputs=yunduan_status)
                            with gr.Column(scale=1):
                                yunduan_clear = gr.Button(value="卸载云端脚本")
                                yunduan_clear.click(yunduan_clear_action,outputs=[yunduan_id,yunduan_status])
                        
                        with gr.Row():
                            gr.Markdown(
                                """
                                ### 云端脚本使用帮助
                                """)
                        with gr.Row():
                            gr.Markdown(
                                """
                                # Hello World!
                                Start typing below to see the output.
                                """,visible=yunduan_tips_status)
                    # with gr.Tab("其他"):
                    #      gr.Label("开发中")
                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return [auto_split,bl,ht,fg,qxd,yuanjin,yuanjin_suiji,goutu_suiji,jintou_suiji,yunduan_id]



        def process(self, p,auto_split, bl,ht,fg,qxd,yuanjin,yuanjin_suiji,goutu_suiji,jintou_suiji,yunduan_id):
            global yunduan_task
            if len(yunduan_task)>0:
                print(f'执行云端脚本 共计 {len(yunduan_task)} 个分镜')
                allPrompts = []
                allNegativePrompt = []
                for item in yunduan_task:
                    allPrompts.append(item['prompts'])
                    allNegativePrompt.append(item['negative_prompts'])
                p.all_prompts = allPrompts
                p.all_negative_prompts = allNegativePrompt

                return

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

            # 画面远近，如果设置了随机远近，这个配置不生效
            if yuanjin_suiji==False:
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
                    if goutu_suiji == True:
                        item = f'{params_random_goutu()},{item}'
                    if jintou_suiji == True:
                        item = f'{params_random_jingtou()},{item}'
                    if yuanjin_suiji ==True:
                        item = f'{params_random_yuanjin()},{item}'
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

 