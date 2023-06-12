import torch


import gradio as gr
import psutil

from modules import paths, script_callbacks, sd_hijack, sd_models, sd_samplers, shared, extensions, devices


### ui definition

def on_ui_tabs():
    # get_full_data()
    with gr.Blocks(analytics_enabled = False) as weming_creater_view:
        with gr.Row(elem_id = 'system_info'):
            with gr.Column(scale = 9):
               gr.HTML("ssss")
    return (weming_creater_view, 'MeCreater', 'weming-mecreater'),


script_callbacks.on_ui_tabs(on_ui_tabs)
