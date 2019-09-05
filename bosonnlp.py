# -*- encoding: utf-8 -*-

from __future__ import print_function, unicode_literals
import json
import requests
from aip import AipOcr
import re
from wand.image import Image
import os
import subprocess
#from win32com import client

""" 你的 APPID AK SK """
APP_ID = '17147620'
API_KEY = 'I5gojys3VQehDuoEYXpMGMdV'
SECRET_KEY = 'keP8WqRSRzDZhsBDBnv0GioCa42oUbQ5'

client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

def doc2pdf_linux(doc):
    """
    convert a doc/docx document to pdf format (linux only, requires libreoffice)
    :param doc: path to document
    """
    cmd = 'libreoffice6.2 --headless --convert-to pdf'.split() + [doc]
    p = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    p.wait(timeout=10)
    stdout, stderr = p.communicate()
    if stderr:
        raise subprocess.SubprocessError(stderr)

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()
    
def file_extension(path): 
  return os.path.splitext(path)[1] 


#convert pdf or docx to jpg
if __name__=='__main__':
    file_name=input("Please input file path:")
    file_extension=file_extension(file_name)
    if((file_extension==".docx")|(file_extension==".doc")):
        file_front_name=file_name.replace(file_extension,"")
        file_pdf_name=file_front_name+".pdf"
        doc2pdf_linux(file_name)
        file_new_name=file_front_name+".jpg"
        with Image(filename=file_pdf_name,resolution=250) as img:
            print(file_new_name)
            img.format = 'jpeg'
            img.save(filename=file_new_name)
    elif(file_extension==".pdf"):
        file_front_name=file_name.replace(file_extension,"")
        file_new_name=file_front_name+".jpg"
        with Image(filename=file_name,resolution=500) as img:
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
    print(txt)
    data = json.dumps(s)
    headers = {
        'X-Token': 'GL_Oid70.36196.LUKOU-IIInuw',
        'Content-Type': 'application/json'
        }
    resp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
    regex = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-]+)"
    email = re.findall(regex, txt)#获取emial
    if(email==[]):
        email=""
    else:
        email=email[0]
    regex = "1[34578]\d{9}"
    phoneNumber = re.findall(regex, txt)
    if(phoneNumber==[]):
        phoneNumber=""
    else:
        phoneNumber=phoneNumber[0]

    flag=0
    regex=r"((期望|理想|目标|意向)(职业|职位|岗位))|((职业|职位|求职|岗位)(目标|期望|意向|理想))"#获取目标职位
    re_regx=re.compile(regex)
    ret=re_regx.search(txt)
    if(ret!=None):
        location=re_regx.search(txt).span()
        length=len(txt)-location[1]
        temp=str(txt[location[1]:location[1]+length])
        data=json.dumps([temp])
        resp_temp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
        for item in resp_temp.json():
            for entity in item['entity']:
                if (entity[2]=="job_title"):
                    exp_job=''.join(item['word'][entity[0]:entity[1]])
                    flag=1
                    break
    if(flag==0):
        exp_job=""

    flag=0
    regex=r"((期望|理想|目标|意向)(工作地点|工作地址|工作城市|地点|地址|城市))"#获取目标地点
    re_regx=re.compile(regex)
    ret=re_regx.search(txt)
    if(ret!=None):
        location=re_regx.search(txt).span()
        length=len(txt)-location[1]
        temp=str(txt[location[1]:location[1]+length])
        data=json.dumps([temp])
        resp_temp = requests.post(NER_URL, headers=headers, data=data.encode('utf-8'))
        for item in resp_temp.json():
            for entity in item['entity']:
                if (entity[2]=="location"):
                    exp_job=''.join(item['word'][entity[0]:entity[1]])
                    flag=1
                    break
    if(flag==0):
        exp_location=""
                    
    count_name=0
    count_school=0
    name=""
    school=""
    for item in resp.json():
        for entity in item['entity']:
            if((entity[2]=="person_name")&(count_name==0)):
                count_name=1
                name=''.join(item['word'][entity[0]:entity[1]])
                #print("name:",''.join(item['word'][entity[0]:entity[1]]))
            elif((entity[2]=="org_name")&(count_school==0)):
                count_school=1
                school=''.join(item['word'][entity[0]:entity[1]])
                #print("school:",''.join(item['word'][entity[0]:entity[1]]))
            if(count_name==1&count_school):
                break
    dic={"name":name,"school":school,"email":email,"phoneNumber":phoneNumber,"exp_job":exp_job,"exp_location":exp_location}
    print(dic)

