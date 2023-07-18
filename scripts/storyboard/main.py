import requests


MECREATER_YUNDUAN_STATUS = False 
MECREATER_PROMPTS_LIST =  []


# 加载数据  
def main_yunyuan_load(guid,yunduan_only_reply,page):
    global MECREATER_PROMPTS_LIST,MECREATER_YUNDUAN_STATUS
    if guid== '':
        return "请先输入云端脚本 GUID"
    if page==1:
        MECREATER_PROMPTS_LIST = []
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
            MECREATER_PROMPTS_LIST.append(item)

        if resjson['code']!=20001:
            return main_yunyuan_load(guid,yunduan_only_reply,page+1)
        else:
            MECREATER_YUNDUAN_STATUS = True
            resmsg = f'云端脚本 {guid} 加载完成，共计 {len(MECREATER_PROMPTS_LIST)} 个分镜'
            print(resmsg)
            return  resmsg#resjson['message']
    except Exception as err:
        return f"{err}"
    


# 清理云端脚本
def main_yunduan_clear_action():
    # print(yunduan_task)
    global MECREATER_PROMPTS_LIST,MECREATER_YUNDUAN_STATUS
    MECREATER_PROMPTS_LIST = []
    MECREATER_YUNDUAN_STATUS = False
    return "",[],"云端脚本卸载完成"