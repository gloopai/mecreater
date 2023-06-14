import copy
import random
import re

import modules.scripts as scripts
import gradio as gr

from modules.processing import Processed, process_images
from modules.shared import  state


promps = [
   "gril, car,short hair,red hair, sports bra , "
   "gril, tree,short hair,red hair, sports bra ,  "
   "boy, sea,short hair,black hair,  "
   "gril, mountain,short hair,red hair, sports bra ,  "
   "boy, city,short hair,black hair ,  "
   "gril, cafe shop,short hair,red hair, sports bra ,  "
   "gril, shoping mall,short red,black hair, sports bra ,  "
   "gril, train,short hair,red hair, sports bra ,  "
]

class Script(scripts.Script):
    def title(self):    
        return "MeCreate(AI网文助手批量出图插件)"


    def ui(self, is_img2img):
        with gr.Row():
            content = gr.Textbox(label="分镜剧本",info="每一行作为一段")

        return [content] 
        
       
    def run(self, p,content):
        # i=0
        # while  i < len(promps):
        #     p.prompt = promps[i]
        proc = process_images(p)
        
        return proc
    
   
