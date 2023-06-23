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
     




panel_fenjing_tips = """

#### 使用「批量出图」功能

🎊 第一步:打开下方的 【脚本(Script)】

🎊 第二步:在脚本中选择【AI漫文创作助手-批量出图】

🎊 根据打开的界面提示进行批量出图的操作

#### TIPS

批量出图功能支持

🎊 WebUI正向提示词分行自动出图

🎊 云端脚本批量出图

⛳ 云端脚本需要 进入 https://ai.quwuxian.com 进行脚本创作

#### 使用帮助

⛳ 使用过程中有任何问题，都可以添加 QQ群：173787712 交流

"""

class ExtensionTemplateScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
                return "MeCreatePanel"

        def show(self, is_img2img):
                return scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
                with gr.Accordion('AI漫文创作助手[画质增强]', open=False):
                    with gr.Tab("画面"):
                        with gr.Row():
                            with gr.Column(scale=2):
                                bl = gr.Radio(["横版", "竖版","自定义"],value="自定义", label="比例", info="横版450x300,竖版300x450，自定义使用默认设置")
                            with gr.Column(scale=2):
                                qxd = gr.Radio(qxd_data,value="默认", label="清晰度", info="生成画面的清晰度")
                        with gr.Row():
                            with gr.Column(scale=2):
                                ht = gr.CheckboxGroup(["选择"], label="减少坏图", info="会添加一些常用的坏图反向词")
                            with gr.Column(scale=2):
                                yuanjin = gr.Slider(minimum=-6,maximum=6 , value=0, label="画面远近", info="数值越小，人像越大,数值越大人像越大，但是越容易崩脸，所有图片生效,另外如果配置了随机远近，这项配置不生效")
                        with gr.Row():
                            with gr.Column(scale=2):
                                fg = gr.Dropdown(fg_data, label="风格", info="选择画风",value="随机")
                        with gr.Row():
                            yuanjin_suiji = gr.CheckboxGroup(["选择"],  label="远近随机", info="开启后人物远近随机")
                            goutu_suiji = gr.CheckboxGroup(["选择"], label="构图随机", info="开启后人物和构图随机")
                            jintou_suiji =  gr.CheckboxGroup(["选择"], label="镜头随机", info="开启后出图镜头角度随机")

                    with gr.Tab("批量出图"):
                        gr.Markdown(panel_fenjing_tips)
                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return [bl,ht,fg,qxd,yuanjin,yuanjin_suiji,goutu_suiji,jintou_suiji]

        def process(self, p, bl,ht,fg,qxd,yuanjin,yuanjin_suiji,goutu_suiji,jintou_suiji):
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
            if yuanjin_suiji==["选择"]:
                newprompt.append(f'${params_random_yuanjin()}')
            else:
                newprompt.append(params_yuanjin(yuanjin))

            # 构图随机
            if goutu_suiji == ["选择"]:
                newprompt.append( f'{params_random_goutu()}')

            if jintou_suiji == ["选择"]:
                newprompt.append(f'{params_random_jingtou()}') 

            # 生成新的正向词
            promptstr = ",".join(newprompt)
            p.prompt = f'{promptstr},{p.prompt}'

            oldPromptArr = p.all_prompts
            newpromptarr = []
            for i in oldPromptArr:
                item = ""
                item = f'{promptstr},{i}'
                newpromptarr.append(item)
            p.all_prompts = newpromptarr

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




# script
# 分镜使用帮助
fenjing_tips = """
                #### 使用方法

             

                """
prompts_split_tip = """

### 🪄 恭喜，您现在可以开始批量出图了

### 🪄 你可以尝试一下，在提示词中输入下面这段内容

```
gril, car,short hair,red hair, sports bra , 
boy, sea,short hair,black hair,  
```

这段提示词通过换行进行分段

###  🪄 提示词输入好之后，就可以试一下点击【生成图片】按钮

💡 如果已经顺利生成图片，那么恭喜，你可以愉快的玩耍了

💡 如果没有出图，那请加 QQ群：173787712 我们一起看下是什么问题

```
在这个模式下，提供了最灵活的提示词分段批量出图提高效率的方法，具备更高的灵活性，但是出图效果方面需要下一些功夫
```

### 🎸 同时，我们也提供了更方便的云端脚本编辑模式

💡 有更精准的分镜内容控制

💡 更丰富的提示词资源

💡 不断迭代的出图效果

如果你需要，可以切换到云端脚本面板进行尝试


💡 云端脚本，需要 打开 https://ai.quwuxian.com 进行脚本编辑和获取脚本Guid
"""

yunduan_tips = """
```
💡 云端脚本需要进入  https://ai.quwuxian.com  进行编辑
💡 脚本编辑完成后，会生成 脚本Guid ，复制后，黏贴到 这个界面的云端脚本Guid 中
💡 黏贴好之后，点击【加载云端脚本】，将脚本内容加载到WebUi中
💡 提示加载完成之后，就可以点击【生成图片】 按钮生成试一下了
💡 有什么问题，那请加 QQ群：173787712 我们一起看下是什么问题
🎃 每次在云端修改完脚本之后，都需要在这里重新加载一次，替换到原来的
🎃 云端脚本使用完成后，需要点击【卸载云端脚本】 才会恢复到 提示词切割 的模式
```
"""




yunduan_status = False 
prompts_list =  []


# 加载数据  
def yunyuan_load(guid,page):
    global prompts_list,yunduan_status
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
            prompts_list.append(item)
        if resjson['code']!=20001:
            return yunyuan_load(guid,page+1)
        else:
            yunduan_status = True
            resmsg = f'云端脚本 {guid} 加载完成，共计 {len(prompts_list)} 个分镜'
            print(resmsg)
            return  resmsg#resjson['message']
    except Exception as err:
        return f"{err}"

# 读取远程脚本
def yunduan_read_action(_p_yunduan_id):
    if  _p_yunduan_id== '':
        return "请先输入云端脚本 GUID"
    global prompts_list
    prompts_list = []
    return yunyuan_load(_p_yunduan_id,1)
    
# 清理云端脚本
def yunduan_clear_action():
    # print(yunduan_task)
    global prompts_list,yunduan_status
    prompts_list = []
    yunduan_status = False
    return "","云端脚本卸载完成"


def piliang_model_change():
    return ""

import copy
class Script(scripts.Script):
    def title(self):    
        return "AI漫文创作助手-批量出图"

    def ui(self, is_img2img):
        with gr.Tab("提示词切割"):
            with gr.Row():
                gr.Markdown(prompts_split_tip)
        with gr.Tab("云端脚本"):
            with gr.Row():
                gr.Markdown(yunduan_tips)
            with gr.Row():
                with gr.Column(scale=1):
                    yunduan_id = gr.Text(label="输入云端脚本Guid",info="输入云端脚本Guid后,点击[加载云端脚本],配置才会生效")
            with gr.Row():
                    yunduan_status = gr.Textbox(label="加载状态",value="未读取",info="请在这里显示加载成功后再进行图片生成")
            with gr.Row():
                with gr.Column(scale=1):
                    yunduan_read= gr.Button(value="加载云端脚本",)
                    yunduan_read.click(yunduan_read_action,inputs=[yunduan_id], outputs=yunduan_status)
                with gr.Column(scale=1):
                    yunduan_clear = gr.Button(value="卸载云端脚本")
                    yunduan_clear.click(yunduan_clear_action,outputs=[yunduan_id,yunduan_status])
        return [] 
    
    def run(self, p):
        p.do_not_save_grid = True 
        global prompts_list,yunduan_status

        # 如果云端加载在关闭状态，就进行webui的提示词分割
        if yunduan_status==False:
            prompts_list = []
            oldPromptArr = []
            oldPromptArr = p.prompt.split("\n")
            for item in oldPromptArr:
                prompts_list.append({
                    "prompts":item,
                    "negative_prompts":p.negative_prompt
                })


        # 处理prompts
        allPrompts = []
        allNegativePrompt = []
        for item in prompts_list:
            allPrompts.append(item['prompts'])
            allNegativePrompt.append(item['negative_prompts'])
        p.all_prompts = allPrompts
        p.all_negative_prompts = allNegativePrompt

        job_count = len(prompts_list)
        state.job_count = job_count

        images = []
        all_prompts = []
        infotexts = []
        i = 0
        while i <job_count: 
            state.job = f"{state.job_no + 1} out of {state.job_count}"
            buildItem = copy.copy(p)
            buildItem.prompt = p.all_prompts [i]
            buildItem.negative_prompt = p.all_negative_prompts [i]
            proc = process_images(buildItem)
            images += proc.images
            i = i+1
        
        return Processed(p, images, p.seed, "", all_prompts=all_prompts, infotexts=infotexts) 
   
