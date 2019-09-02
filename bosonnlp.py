# -*- encoding: utf-8 -*-

from __future__ import print_function, unicode_literals
import json
import requests
from aip import AipOcr
import re
from wand.image import Image
import os
from win32com import client

""" 你的 APPID AK SK """
APP_ID = '17147620'
API_KEY = 'I5gojys3VQehDuoEYXpMGMdV'
SECRET_KEY = 'keP8WqRSRzDZhsBDBnv0GioCa42oUbQ5'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)


""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
    
def file_extension(path): 
  return os.path.splitext(path)[1] 

def doc2pdf(doc_name, pdf_name):
    try:
        word = client.DispatchEx("Word.Application")
        if os.path.exists(pdf_name):
            os.remove(pdf_name)
        worddoc = word.Documents.Open(doc_name,ReadOnly = 1)
        worddoc.SaveAs(pdf_name, FileFormat = 17)
        worddoc.Close()
        return pdf_name
    except:
        return 1

#convert pdf or docx to jpg
if __name__=='__main__':
    file_name=input("Please input file path:")
    file_extension=file_extension(file_name)
    if((file_extension==".docx")|(file_extension==".doc")):
        file_front_name=file_name.replace(file_extension,"")
        file_pdf_name=file_front_name+".pdf"
        doc2pdf(file_name, file_pdf_name)
        file_new_name=file_front_name+".jpg"
        with Image(filename=file_pdf_name,resolution=300) as img:
            print(file_new_name)
            img.format = 'jpeg'
            img.save(filename=file_new_name)
    elif(file_extension==".pdf"):
        file_front_name=file_name.replace(file_extension,"")
        file_new_name=file_front_name+".jpg"
        with Image(filename=file_name,resolution=300) as img:
            print(file_new_name)
            img.format = 'jpeg'
            img.save(filename=file_new_name)
    #with Image(filename=r'C:\Users\admin\Desktop\杂七杂八\din.pdf',resolution=300) as img:
    
    image = get_file_content(file_new_name)
    """ 调用通用文字识别（高精度版） """
    client.basicAccurate(image);
    """ 如果有可选参数 """
    options = {}
    options["detect_direction"] = "true"
    options["probability"] = "true"
    """ 带参数调用通用文字识别（高精度版） """
    res=client.basicAccurate(image, options)
    txt=""
    for item in res['words_result']:
        txt=txt+item['words']
        
    NER_URL = 'http://api.bosonnlp.com/ner/analysis'
    s = [txt]
    data = json.dumps(s)
    headers = {
        'X-Token': 'GL_Oid70.36196.LUKOU-IIInuw',
        'Content-Type': 'application/json'
        }
    resp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
    regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-])"
    email = re.findall(regex, txt)#获取emial
    print("email:",email)
    regex = "1[34578]\d{9}"
    phoneNumber = re.findall(regex, txt)
    print("phone:",phoneNumber[0])#获取电话
    
    regex="((期望|理想|目标)(职业|职位|岗位))|((职业|职位|求职|岗位)目标)"#获取目标职位
    re_regx=re.compile(regex)
    location=re_regx.search(txt).span()
    if(location):
        length=len(txt)-location[1]
        maxlen=max(length,15)
        temp=str(txt[location[1]:location[1]+maxlen])
        data=json.dumps([temp])
        resp_temp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
        for item in resp_temp.json():
            for entity in item['entity']:
                if (entity[2]=="job_title"):
                    exp_job=''.join(item['word'][entity[0]:entity[1]])
                    print("exp_job:",exp_job)
                    
    count_name=0
    count_school=0
    for item in resp.json():
        for entity in item['entity']:
            if((entity[2]=="person_name")&(count_name==0)):
                count_name=1
                print("name:",''.join(item['word'][entity[0]:entity[1]]))
            elif((entity[2]=="org_name")&(count_school==0)):
                count_school=1
                print("school:",''.join(item['word'][entity[0]:entity[1]]))
            if(count_name==1&count_school):
                break


