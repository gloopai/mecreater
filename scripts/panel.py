


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


class ExtensionTemplateScript(scripts.Script):
        # Extension title in menu UI
        def title(self):
                return "MeCreatePanel"

        # Decide to show menu in txt2img or img2img
        # - in "txt2img" -> is_img2img is `False`
        # - in "img2img" -> is_img2img is `True`
        #
        # below code always show extension menu
        def show(self, is_img2img):
                return scripts.AlwaysVisible

        # Setup menu ui detail
        def ui(self, is_img2img):
                with gr.Accordion('MeCreater(AI网文助手)', open=False):
                        with gr.Row():
                            with gr.Column(scale=2):
                                bl = gr.Radio(["横版", "竖版","自定义"],value="自定义", label="比例", info="横版960x540,竖版540x960，自定义使用默认设置")
                            # with gr.Column():
                            #     
                               
                # TODO: add more UI components (cf. https://gradio.app/docs/#components)
                return [bl]

        # Extension main process
        # Type: (StableDiffusionProcessing, List<UI>) -> (Processed)
        # args is [StableDiffusionProcessing, UI1, UI2, ...]
        def process(self, p, bl):
            # 设置比例
            if bl !='自定义':
                w,h = params_bl(bl)
                p.width = w
                p.height= h
