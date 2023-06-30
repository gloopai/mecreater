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
from PIL import Image as im, ImageDraw
from modules import images, script_callbacks
from modules.processing import process_images, Processed
from modules.processing import Processed
from modules.shared import opts, cmd_opts, state

build_ver = "2023063001"


pannel_tips = """
### 两种分镜切割的方法

#### 💡 WebUi 提示词换行快速切割

直接在SD WebUi 中利用提示词换行，有多少行，就出多少张图

#### 💡 云端分镜脚本批量生成

通过使用 https://ai.quwuxian.com 云端分镜脚本编辑器完成分镜脚本的编辑，在SD WebUi 中一键批量出图

#### 🎸 这两种方法，都需要打开下方 脚本(Script) 中的 【AI漫文创作助手-批量出图】 根据提示完成出图操作

#### 🎸 【AI漫文创作助手】完全兼容WebUi的各项设置，在不改变原生配置的前提下，进行了更灵活的扩充

"""

class ExtensionTemplateScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
                return "MeCreatePanel"

        def show(self, is_img2img):
                return scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
                with gr.Accordion(f'AI漫文创作助手(ver {build_ver})', open=False):
                    with gr.Tab("使用帮助"):
                        with gr.Row():
                            gr.Markdown(pannel_tips)

                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return []
        




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
🎃 每次在云端修改完脚本之后，都需要在这里重新加载一次，替换到原来的
🎃 云端脚本使用完成后，需要点击【卸载云端脚本】 才会恢复到 提示词切割 的模式
```
"""




yunduan_status = False 
prompts_list =  []


# 加载数据  
def yunyuan_load(guid,yunduan_only_reply,page):
    global prompts_list,yunduan_status
    onlyReply = False
    if yunduan_only_reply==['选择']:
        onlyReply  = True

    params = {"app_key":"bc01b43c-a0e2-4007-ad09-033b95cf1d6e", "method":"ai.center","data":{"command":"storyboard.task.get.by.webui","data":{"page":page,"task_guid":guid,"reply":onlyReply}}}
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
            return yunyuan_load(guid,yunduan_only_reply,page+1)
        else:
            yunduan_status = True
            resmsg = f'云端脚本 {guid} 加载完成，共计 {len(prompts_list)} 个分镜'
            print(resmsg)
            return  resmsg#resjson['message']
    except Exception as err:
        return f"{err}"

# 读取远程脚本
def yunduan_read_action(_p_yunduan_id,_p_yunduan_only_reply):
    if  _p_yunduan_id== '':
        return "请先输入云端脚本 GUID"
    global prompts_list
    prompts_list = []
    return yunyuan_load(_p_yunduan_id,_p_yunduan_only_reply,1)
    
# 清理云端脚本
def yunduan_clear_action():
    # print(yunduan_task)
    global prompts_list,yunduan_status
    prompts_list = []
    yunduan_status = False
    return "",[],"云端脚本卸载完成"


def piliang_model_change():
    return ""

import copy
class Script(scripts.Script):
    def title(self):    
        return f"AI漫文创作助手-批量出图({build_ver})"

    def ui(self, is_img2img):
        with gr.Tab("提示词切割"):
            with gr.Row():
                gr.Markdown(prompts_split_tip)
        with gr.Tab("云端脚本"):
            with gr.Row():
                gr.Markdown(yunduan_tips)
            with gr.Row():
                with gr.Column(scale=2):
                    yunduan_id = gr.Text(label="输入云端脚本Guid",info="输入云端脚本Guid后,点击[加载云端脚本],配置才会生效")
                with gr.Column(scale=1):
                    yunduan_only_reply = gr.CheckboxGroup(["选择"],  label="重绘", info="勾选后只会加载云端设置了重绘的分镜")
            with gr.Row():
                    yunduan_status = gr.Textbox(label="加载状态",value="未读取",info="请在这里显示加载成功后再进行图片生成")
            with gr.Row():
                with gr.Column(scale=1):
                    yunduan_read= gr.Button(value="加载云端脚本",)
                    yunduan_read.click(yunduan_read_action,inputs=[yunduan_id,yunduan_only_reply], outputs=yunduan_status)
                with gr.Column(scale=1):
                    yunduan_clear = gr.Button(value="卸载云端脚本")
                    yunduan_clear.click(yunduan_clear_action,outputs=[yunduan_id,yunduan_only_reply,yunduan_status])
        return [] 
    
    def run(self, p):
        p.do_not_save_grid = True # 关闭网格图保存
        p.do_not_save_samples = True # 关闭webui 保存图片
        global prompts_list,yunduan_status

        # 如果云端加载在关闭状态，就进行webui的提示词分割
        if yunduan_status==False:
            prompts_list = []
            oldPromptArr = []
            oldPromptArr = p.prompt.split("\n")
            oldIndex = 0
            while oldIndex < len(oldPromptArr):
                item = oldPromptArr[oldIndex]
                prompts_list.append({
                    "prompts":item,
                    "negative_prompts":p.negative_prompt,
                    "lens_number":'173787712',
                    "title":"default"
                })
                oldIndex = oldIndex + 1

        # 处理prompts
        allPrompts = []
        allNegativePrompt = []
        for item in prompts_list:
            allPrompts.append(item['prompts'])
            allNegativePrompt.append(item['negative_prompts'])


        p.all_prompts = allPrompts
        p.all_negative_prompts = allNegativePrompt

        print(f"\r\n ==| AI漫文创作助手 QQ群:173787712 批数:{p.n_iter}  单批:{p.batch_size}  分镜:{len(prompts_list)} |== \r\n")
        
        tmpPromptsList = []
        # 批次，次数处理，填充临时数据
        niterIndex = 0
        while niterIndex < p.n_iter:
            batchSizeIndex = 0
            while batchSizeIndex < p.batch_size:
                promptsIndex = 0
                while promptsIndex < len(prompts_list):
                    promptsTmpItem = prompts_list[promptsIndex]
                    tmpPromptsList.append(promptsTmpItem)
                    promptsIndex = promptsIndex + 1
                batchSizeIndex = batchSizeIndex + 1
            niterIndex = niterIndex +1
        p.n_iter = 1
        p.batch_size = 1
        # 生图任务
        job_count = len(tmpPromptsList)
        state.job_count = job_count


        all_prompts = []
        buildImageList = []
        infotexts = []
        i = 0
        # 开始循环任务生成图片
        while i <job_count: 
            state.job = f"{state.job_no + 1} out of {state.job_count}"
            promptItem = tmpPromptsList[i]
            buildItem = copy.copy(p)
            buildItem.prompt = promptItem['prompts'] #p.all_prompts [i]
            buildItem.negative_prompt = promptItem['negative_prompts'] #p.all_negative_prompts [i]
            if 'width' in promptItem and promptItem['width']!=0:
                buildItem.width= promptItem['width']
            if 'height' in promptItem and promptItem['height'] !=0:
                buildItem.height= promptItem['height']

            proc = process_images(buildItem)
            sIndex = len(proc.images)-1
            imgItem = proc.images[sIndex]

            saveForder = f'{p.outpath_samples}/mecreate'
            if "title" in promptItem:
                if promptItem["title"] != "":
                    saveForder = f'{saveForder}/{promptItem["title"]}'
            images.save_image(
                        image=imgItem,
                        path= saveForder,
                        basename=f'{promptItem["lens_number"]}',
                        info=proc.info, 
                        p=p,short_filename=True)
            buildImageList += proc.images
            i = i+1
        
        print(f"\r\n==| AI漫文创作助手 出图完成 合计出图:{job_count} 张\r\n")
        
        return Processed(p, buildImageList, p.seed, "", all_prompts=all_prompts, infotexts=infotexts) 
   
