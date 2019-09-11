#!/usr/bin/python 
# -*- coding: utf-8 -*- 
import os
import re
import json
import requests
import subprocess
import sys 
import importlib 
importlib.reload(sys) 
  
from pdfminer.pdfparser import PDFParser,PDFDocument 
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter 
from pdfminer.converter import PDFPageAggregator 
from pdfminer.layout import *
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed 
  
''''' 
解析pdf文件，获取文件中包含的各种对象 
'''
  
# 解析pdf文件函数 
def parse(pdf_path): 
  fp = open(pdf_path, 'rb') # 以二进制读模式打开 
  # 用文件对象来创建一个pdf文档分析器 
  parser = PDFParser(fp) 
  # 创建一个PDF文档 
  doc = PDFDocument() 
  # 连接分析器 与文档对象 
  parser.set_document(doc) 
  doc.set_parser(parser) 
  
  # 提供初始化密码 
  # 如果没有密码 就创建一个空的字符串 
  doc.initialize() 
  
  # 检测文档是否提供txt转换，不提供就忽略 
  if not doc.is_extractable: 
    raise PDFTextExtractionNotAllowed 
  else: 
    # 创建PDf 资源管理器 来管理共享资源 
    rsrcmgr = PDFResourceManager() 
    # 创建一个PDF设备对象 
    laparams = LAParams() 
    device = PDFPageAggregator(rsrcmgr, laparams=laparams) 
    # 创建一个PDF解释器对象 
    interpreter = PDFPageInterpreter(rsrcmgr, device) 
  
    # 用来计数页面，图片，曲线，figure，水平文本框等对象的数量 
    num_page, num_image, num_curve, num_figure, num_TextBoxHorizontal = 0, 0, 0, 0, 0

    result=""
    # 循环遍历列表，每次处理一个page的内容 
    for page in doc.get_pages(): # doc.get_pages() 获取page列表 
      num_page += 1 # 页面增一 
      interpreter.process_page(page) 
      # 接受该页面的LTPage对象 
      layout = device.get_result() 
      for x in layout: 
        if isinstance(x,LTImage): # 图片对象 
          num_image += 1
        if isinstance(x,LTCurve): # 曲线对象 
          num_curve += 1
        if isinstance(x,LTFigure): # figure对象 
          num_figure += 1
        if isinstance(x, LTTextBoxHorizontal): # 获取文本内容 
          num_TextBoxHorizontal += 1 # 水平文本框对象增一 
          # 保存文本内容 
          results = x.get_text()
          result=result+results
    print('对象数量：\n','页面数：%s\n'%num_page,'图片数：%s\n'%num_image,'曲线数：%s\n'%num_curve,'水平文本框：%s\n'
       %num_TextBoxHorizontal)
    return result
  
  

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
    else:
        file_pdf_name=file_name
    #pdf_path = r'C:/Users/admin/Desktop/Jianli.pdf' #pdf文件路径及文件名 
    txt=parse(file_pdf_name)
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

