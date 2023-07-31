'''
Author: acheqi@126.com acheqi@126.com
Date: 2023-06-13 23:03:42
LastEditors: acheqi@126.com
LastEditTime: 2023-06-14 02:18:58
Description: 
'''
import json
from importlib import reload
import modules # SBM Apparently, basedir only works when accessed directly.
from modules import paths, scripts, shared, extra_networks
import gradio as gr
import os
from modules.processing import Processed
from modules.processing import Processed

from scripts.storyboard.tips import(pannel_tips,prompts_split_tip,yunduan_tips)
from scripts.storyboard.main import(MECREATER_YUNDUAN_STATUS,MECREATER_PROMPTS_LIST,
                                    main_yunyuan_load,main_yunduan_clear_action)
from scripts.storyboard.run import (build_images)


# 分区绘制
import scripts.rp.attention
import scripts.rp.regions
reload(scripts.rp.regions) # update without restarting web-ui.bat
reload(scripts.rp.attention)

from scripts.rp.attention import ( hook_forwards)
from scripts.rp.regions import ( KEYBRK, matrixdealer)
from scripts.rp.build import(lange,commondealer,hrdealer,anddealer,tokendealer,
                             thresholddealer,bratioprompt,flagfromkeys,keyconverter
                             )
# 分区绘制结束


orig_batch_cond_uncond = shared.batch_cond_uncond

build_ver = "2023073101"


# 面板
class ExtensionTemplateScript(modules.scripts.Script):
        def __init__(self):
            self.active = False
            self.mode = ""
            self.calcmode = ""
            self.w = 0
            self.h = 0
            self.debug = False
            self.usebase = False
            self.usecom = False
            self.usencom = False
            self.batch_size = 0

            self.cells = False
            self.aratios = []
            self.bratios = []
            self.divide = 0
            self.count = 0
            self.pn = True
            self.hr = False
            self.hr_scale = 0
            self.hr_w = 0
            self.hr_h = 0
            self.all_prompts = []
            self.all_negative_prompts = []
            self.imgcount = 0
            # for latent mode
            self.filters = []
            self.neg_filters = []
            self.anded = False
            self.lora_applied = False
            self.lactive = False
            # for inpaintmask
            self.indmaskmode = False
            self.regmasks = None
            self.regbase = None
            #for prompt region
            self.pe = []
            self.modep =False
            self.calced = False
            self.step = 0
            self.lpactive = False
        # Extension title in menu UI
        def title(self):
            return "MeCreatePanel"

        def show(self, is_img2img):
            return modules.scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
            with gr.Accordion(f'AI漫文创作助手(ver {build_ver})', open=False):
                with gr.Tab("使用帮助"):
                    with gr.Row():
                        gr.Markdown(pannel_tips)
                   
                               
            # TODO: add more UI components (cf. https://gradio.app/docs/#components)
            return []
        

        def process(self, p,):
            self,p = build_regions(self,p)

        def before_process_batch(self, p, *args, **kwargs):
            self.current_prompts = kwargs["prompts"].copy()
            p.disable_extra_networks = False
                


def regional_params(extraConfig):
    regionalConfig = extraConfig['regional']
    if regionalConfig['divide_ratio'] == "":
        regionalConfig['divide_ratio'] = '1,1'
    if regionalConfig['base_ratio']=="":
        regionalConfig['base_ratio'] = '0.2'
    if regionalConfig['threshold'] == "":
        regionalConfig['threshold'] = '0.4'
    if regionalConfig['calc_model']=="":
        regionalConfig['calc_model'] = "Attention"
    if regionalConfig['model']=="":
        regionalConfig['model'] = 'Horizontal'
    return regionalConfig


# 分区处理
def build_regions(self,p):
    regionalConfig ={
            "active":False
    }
    try:
        extraConfig = json.loads(p.extra_generation_params['mecreate'])
        regionalConfig = regional_params(extraConfig)
        del p.extra_generation_params['mecreate']
    except:
        pass

    prompt = p.prompt
    if type(prompt) == list:
        prompt = prompt[0]
    p.prompt = prompt
    if hasattr(self,"handle"):
        hook_forwards(self, p.sd_model.model.diffusion_model, remove=True)
        del self.handle
        shared.batch_cond_uncond = orig_batch_cond_uncond
        self.__init__()

    if regionalConfig['active']:
        aratios = regionalConfig['divide_ratio']
        bratios = regionalConfig['base_ratio']
        threshold= regionalConfig['threshold']
        calcmode = regionalConfig['calc_model']
        model = regionalConfig['model']
        usecom = regionalConfig['use_comm']
        usebase = regionalConfig['use_base']
        usencom = regionalConfig['use_comm_nagative']
        self.__init__()

        self.active = True
        self.mode = model #"Horizontal","Vertical"
        self.calcmode = calcmode #"Attention", "Latent"

        self.debug = False
        self.usebase = usebase
        self.usecom = usecom
        self.usencom = usencom
        self.w = p.width
        self.h = p.height
        self.batch_size = p.batch_size
        self.prompt = p.prompt
        self.all_prompts = p.all_prompts.copy()
        self.all_negative_prompts = p.all_negative_prompts.copy()
        comprompt = comnegprompt = None

        # SBM ddim / plms detection.
        self.isvanilla = p.sampler_name in ["DDIM", "PLMS", "UniPC"]


        self, p = flagfromkeys(self, p)

        self.indmaskmode = (self.mode == "Mask")

        p.prompt = p.prompt.replace("AND",KEYBRK)
        for i in lange(p.all_prompts):
            p.all_prompts[i] = p.all_prompts[i].replace("AND",KEYBRK)
        self.anded = True

        self.cells = not "Mask" in self.mode

        #convert BREAK to ADDCOL/ADDROW
        if KEYBRK in p.prompt:
            p = keyconverter(aratios, self.mode, usecom, usebase, p)

        self, p = matrixdealer(self, p, aratios, bratios, self.mode, usebase, comprompt,comnegprompt)
        self.handle = hook_forwards(self, p.sd_model.model.diffusion_model)
        shared.batch_cond_uncond = orig_batch_cond_uncond
        seps = KEYBRK 

        self, p = commondealer(self, p, self.usecom, self.usencom)   #add commom prompt to all region
        self, p = anddealer(self, p , calcmode)                                 #replace BREAK to AND
        self = tokendealer(self, p, seps)                             #count tokens and calcrate target tokens
        self, p = thresholddealer(self, p, threshold)                          #set threshold
        self = bratioprompt(self, bratios)
        p = hrdealer(p)
        print(f"pos tokens : {self.ppt}, neg tokens : {self.pnt}")

    return self,p


# 读取远程脚本
def yunduan_read_action(_p_yunduan_id,_p_yunduan_only_reply):
    if _p_yunduan_id== '':
        return "请先输入云端脚本 GUID"
    msg = main_yunyuan_load(_p_yunduan_id,_p_yunduan_only_reply,1)
    return msg
    
# 清理云端脚本
def yunduan_clear_action():
    return main_yunduan_clear_action()

# 执行脚本
class Script(modules.scripts.Script):
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
        extraMsg = {
            "Build":f'MeCreater {build_ver}',
        }
        p.extra_generation_params.update(extraMsg)

        self,p,buildImageList,all_prompts,infotexts= build_images(self,p)
        return Processed(p, buildImageList, p.seed, "", all_prompts=all_prompts, infotexts=infotexts) 
   
