from importlib import reload
import gradio as gr

import modules.ui
import modules # SBM Apparently, basedir only works when accessed directly.
from modules import paths, scripts, shared, extra_networks
import scripts.rp.attention
import scripts.rp.regions
reload(scripts.rp.regions) # update without restarting web-ui.bat
reload(scripts.rp.attention)
from scripts.rp.attention import (TOKENS, hook_forwards)
from scripts.rp.regions import ( KEYBRK, KEYBASE, KEYCOMM, KEYPROMPT,
                             floatdef, makeimgtmp, matrixdealer)



def lange(l):
    return range(len(l))

def commondealer(self, p, usecom, usencom):
    all_prompts = []
    all_negative_prompts = []
    def comadder(prompt):
        ppl = prompt.split(KEYBRK)
        for i in range(len(ppl)):
            if i == 0:
                continue
            ppl[i] = ppl[0] + ", " + ppl[i]
        ppl = ppl[1:]
        prompt = f"{KEYBRK} ".join(ppl)
        return prompt

    if usecom:
        self.prompt = p.prompt = comadder(p.prompt)
        for pr in p.all_prompts:
            all_prompts.append(comadder(pr))
        p.all_prompts = all_prompts

    if usencom:
        self.negative_prompt = p.negative_prompt = comadder(p.negative_prompt)
        for pr in p.all_negative_prompts:
            all_negative_prompts.append(comadder(pr))
        p.all_negative_prompts = all_negative_prompts
        
    return self, p

def hrdealer(p):
    p.hr_prompt = p.prompt
    p.hr_negative_prompt = p.negative_prompt
    p.all_hr_prompts = p.all_prompts
    p.all_hr_negative_prompts = p.all_negative_prompts
    return p


def anddealer(self, p, calcmode):
    self.divide = p.prompt.count(KEYBRK)
    if calcmode != "Latent" : return self, p

    p.prompt = p.prompt.replace(KEYBRK, "AND")
    for i in lange(p.all_prompts):
        p.all_prompts[i] = p.all_prompts[i].replace(KEYBRK, "AND")
    p.negative_prompt = p.negative_prompt.replace(KEYBRK, "AND")
    for i in lange(p.all_negative_prompts):
        p.all_negative_prompts[i] = p.all_negative_prompts[i].replace(KEYBRK, "AND")
    self.divide = p.prompt.count("AND") + 1
    return self, p



def tokendealer(self, p, seps):
    text, _ = extra_networks.parse_prompt(p.all_prompts[0]) # SBM From update_token_counter.
    ppl = text.split(seps)
    npl = p.all_negative_prompts[0].split(seps)
    targets =[p.split(",")[-1] for p in ppl[1:]]
    pt, nt, ppt, pnt, tt = [], [], [], [], []

    padd = 0
    for pp in ppl:
        tokens, tokensnum = shared.sd_model.cond_stage_model.tokenize_line(pp)
        pt.append([padd, tokensnum // TOKENS + 1 + padd])
        ppt.append(tokensnum)
        padd = tokensnum // TOKENS + 1 + padd

    if self.modep:
        for target in targets:
            ptokens, tokensnum = shared.sd_model.cond_stage_model.tokenize_line(ppl[0])
            ttokens, _ = shared.sd_model.cond_stage_model.tokenize_line(target)

            i = 1
            tlist = []
            while ttokens[0].tokens[i] != 49407:
                for (j, maintok) in enumerate(ptokens): # SBM Long prompt.
                    if ttokens[0].tokens[i] in maintok.tokens:
                        tlist.append(maintok.tokens.index(ttokens[0].tokens[i]) + 75 * j)
                i += 1
            if tlist != [] : tt.append(tlist)

    paddp = padd
    padd = 0
    for np in npl:
        _, tokensnum = shared.sd_model.cond_stage_model.tokenize_line(np)
        nt.append([padd, tokensnum // TOKENS + 1 + padd])
        pnt.append(tokensnum)
        padd = tokensnum // TOKENS + 1 + padd

    self.eq = paddp == padd

    self.pt = pt
    self.nt = nt
    self.pe = tt
    self.ppt = ppt
    self.pnt = pnt

    return self


def thresholddealer(self, p ,threshold):
    if self.modep:
        threshold = threshold.split(",")
        while len(self.pe) >= len(threshold) + 1:
            threshold.append(threshold[0])
        self.th = [floatdef(t, 0.4) for t in threshold] * self.batch_size
        if self.debug :print ("threshold", self.th)
    return self, p

def bratioprompt(self, bratios):
    if not self.modep: return self
    bratios = bratios.split(",")
    bratios = [floatdef(b, 0) for b in bratios]
    while len(self.pe) >= len(bratios) + 1:
        bratios.append(bratios[0])
    self.bratios = bratios
    return self


def flagfromkeys(self, p):
    '''
    detect COMM/BASE keys and set flags
    '''
    if KEYCOMM in p.prompt:
        self.usecom = True
    
    if KEYCOMM in p.negative_prompt:
        self.usencom = True
    
    if KEYBASE in p.prompt:
        self.usebase = True

        
    if KEYPROMPT in p.prompt.upper():
        self.mode = "Prompt"
        p.replace(KEYPROMPT,KEYBRK)

    return self, p


def keyconverter(aratios,mode,usecom,usebase,p):
    '''convert BREAKS to ADDCOMM/ADDBASE/ADDCOL/ADDROW'''
    keychanger = makeimgtmp(aratios,mode,usecom,usebase,inprocess = True)
    keychanger = keychanger[:-1]
    #print(keychanger,p.prompt)
    for change in keychanger:
        if change == KEYCOMM and KEYCOMM in p.prompt: continue
        if change == KEYBASE and KEYBASE in p.prompt: continue
        p.prompt= p.prompt.replace(KEYBRK,change,1)

    return p

