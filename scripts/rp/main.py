from importlib import reload
import gradio as gr

import modules.ui
import modules # SBM Apparently, basedir only works when accessed directly.
from modules import paths, scripts, shared, extra_networks
import scripts.rp.attention
import scripts.rp.regions
reload(scripts.rp.regions) # update without restarting web-ui.bat
reload(scripts.rp.attention)

from scripts.rp.attention import ( hook_forwards)
from scripts.rp.regions import ( KEYBRK, matrixdealer)
from scripts.rp.build import(lange,commondealer,hrdealer,anddealer,tokendealer,
                             thresholddealer,bratioprompt,flagfromkeys,keyconverter
                             )



orig_batch_cond_uncond = shared.batch_cond_uncond


def aaaaaa():
    print("ssssss")
def regions_init(self):
    from scripts.storyboard.main import(MECREATER_YUNDUAN_STATUS)
    if MECREATER_YUNDUAN_STATUS==False:
        return self
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
    #for prompt region
    self.pe = []
    self.modep =False
    self.calced = False
    self.step = 0
    self.lpactive = False
    return self

def regions_run(self,p):
    from scripts.storyboard.main import(MECREATER_YUNDUAN_STATUS)
    if MECREATER_YUNDUAN_STATUS==False:
        return self,p
    aratios = '1,1'
    bratios = '0.2'
    threshold= '0.4'
    calcmode = 'Attention'
    model = 'Horizontal'
    
    prompt = p.prompt
    if type(prompt) == list:
        prompt = prompt[0]
    p.prompt = prompt
    self.__init__()
    
    usecom = False
    usebase = False
    usencom = False

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
    print("====================")
    print(p.prompt)
    print("------------------")
    print(p.all_prompts)
    return self,p
