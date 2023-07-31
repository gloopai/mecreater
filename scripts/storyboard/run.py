from modules.shared import opts, cmd_opts, state
import random


def build_prompts(self,p):
    from scripts.storyboard.main import (MECREATER_PROMPTS_LIST,MECREATER_YUNDUAN_STATUS)
    p.do_not_save_grid = True # 关闭网格图保存
    p.do_not_save_samples = True # 关闭webui 保存图片

    # 如果云端加载在关闭状态，就进行webui的提示词分割
    if MECREATER_YUNDUAN_STATUS==False:
        MECREATER_PROMPTS_LIST = []
        oldPromptArr = []
        oldPromptArr = p.prompt.split("\n")
        oldIndex = 0
        while oldIndex < len(oldPromptArr):
            item = oldPromptArr[oldIndex]
            MECREATER_PROMPTS_LIST.append({
                "prompts":item,
                "negative_prompts":p.negative_prompt,
                "lens_number":'173787712',
                "title":"default",
                "extra":"{}"
            })
            oldIndex = oldIndex + 1

    # 处理prompts
    allPrompts = []
    allNegativePrompt = []
    for item in MECREATER_PROMPTS_LIST:
        allPrompts.append(item['prompts'])
        allNegativePrompt.append(item['negative_prompts'])


    p.all_prompts = allPrompts
    p.all_negative_prompts = allNegativePrompt

    print(f"\r\n ==| AI漫文创作助手 QQ群:173787712 批数:{p.n_iter}  单批:{p.batch_size}  分镜:{len(MECREATER_PROMPTS_LIST)} |== \r\n")
    
    tmpPromptsList = build_prompts_with_batch(MECREATER_PROMPTS_LIST,p)
    # 批次，次数处理，填充临时数据，停用原来的，所有图出完再出下一批的模式
    # tmpPromptsList = []
    # niterIndex = 0
    # while niterIndex < p.n_iter:
    #     batchSizeIndex = 0
    #     while batchSizeIndex < p.batch_size:
    #         promptsIndex = 0
    #         while promptsIndex < len(MECREATER_PROMPTS_LIST):
    #             promptsTmpItem = MECREATER_PROMPTS_LIST[promptsIndex]
    #             tmpPromptsList.append(promptsTmpItem)
    #             promptsIndex = promptsIndex + 1
    #         batchSizeIndex = batchSizeIndex + 1
    #     niterIndex = niterIndex +1
    p.n_iter = 1
    p.batch_size = 1
    # 生图任务
    job_count = len(tmpPromptsList)
    state.job_count = job_count
    return self,p,tmpPromptsList

import copy
shijiao_list = ["full body",
                "upper body",
                "cowboy shot",
                "from the left",
                "from the right",
                "from behind",
                "panoramic view",
                "wide-angle view"]
def trigger_prompts(item):
    # print(item)
    itemPrompts= item['prompts']
    # 随机镜头触发词
    if "[mecreater:rand_screen_lens]" in itemPrompts:
        rand_screen_lens = random.choice(shijiao_list)
        # print(rand_screen_lens)
        itemPrompts = itemPrompts.replace("[mecreater:rand_screen_lens]",rand_screen_lens,1)
        
    # if "[mecreater:clear_no_humans]" in itemPrompts:
    #     if ",no humans" in itemPrompts:
    #         itemPrompts = itemPrompts.replace(",no humans","",1)
    item['prompts'] = itemPrompts
    # print(itemPrompts)
    return item

# 根据批次和数量创建prompt队列
def build_prompts_with_batch(prompts_list,p):
    tmpPromptsList = []
    promptsIndex = 0
    while promptsIndex < len(prompts_list):
        promptsTmpItem = prompts_list[promptsIndex]
        promptsIndex = promptsIndex + 1
        niterIndex = 0
        while niterIndex < p.n_iter:
            niterIndex = niterIndex +1
            batchSizeIndex = 0
            while batchSizeIndex < p.batch_size:
                promptsTmpItemCopy = trigger_prompts(copy.copy(promptsTmpItem))
                tmpPromptsList.append(promptsTmpItemCopy)
                batchSizeIndex = batchSizeIndex + 1
    return tmpPromptsList




# 生成图片

from modules.processing import process_images, Processed
from modules import images, script_callbacks
def build_images(self,p):
    self,p,prompts_list = build_prompts(self,p)
    all_prompts = []
    buildImageList = []
    infotexts = []
    i = 0
    # 开始循环任务生成图片
    job_count = len(prompts_list)
    while i <job_count: 
        state.job = f"{state.job_no + 1} out of {state.job_count}"
        promptItem = prompts_list[i]
        # print(promptItem)
        buildItem = copy.copy(p)
        buildItem.prompt = promptItem['prompts'] #p.all_prompts [i]
        buildItem.negative_prompt = promptItem['negative_prompts'] #p.all_negative_prompts [i]
        if 'width' in promptItem and promptItem['width']!=0:
            buildItem.width= promptItem['width']
        if 'height' in promptItem and promptItem['height'] !=0:
            buildItem.height= promptItem['height']
        if "extra" in promptItem:
            buildItem.extra_generation_params.update({
                'mecreate':promptItem['extra']
            })

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
    
    print(f"\r\n==| AI漫文创作助手 出图完成 合计出图:{state.job_count} 张\r\n")
    return self,p,buildImageList,all_prompts,infotexts