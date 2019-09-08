
#coding:utf-8
import io
import os
import glob
from wand.image import Image
from wand.color import Color
from PyPDF2 import PdfFileReader, PdfFileWriter
 
memo = {}
 
def getPdfReader(filename):
	reader = memo.get(filename, None)
	if reader is None:
		reader = PdfFileReader(filename, strict=False)
		memo[filename] = reader
	return reader
 
def _run_convert(pdfile, savedfilename, page_index, index, res=120):
	pageObj = pdfile.getPage(page_index)#获取pdf的第page_index页
	dst_pdf = PdfFileWriter()
	dst_pdf.addPage(pageObj)
	pdf_bytes = io.BytesIO()
	dst_pdf.write(pdf_bytes)
	pdf_bytes.seek(0)
	img = Image(file=pdf_bytes, resolution=res)
 
	img.format = 'png'
 
	img.compression_quality = 90
	img.background_color = Color("white")
 
	img_path = '%s%04d.jpg' % (savedfilename, index)
	img.save(filename=img_path)
	print(img_path)
	img.destroy()
 
def dealPerPdf(path, file, index):
	savedfilename = path.split('/')[-1].split('-')[0] + '_'
	savedfilename = path + '/2_' + savedfilename#要保存的图片文件名
 
	new_path = os.path.join(path, file)
	pdfile = getPdfReader(new_path)  # 打开pdf文件句柄
	page_nums = pdfile.getNumPages()  # 获取pdf总页数
 
	for page_index in range(page_nums):
		# print(index)
		_run_convert(pdfile, savedfilename, page_index, index)
		index = index + 1
	return index
 
def getAllfiles(path):
	files = os.listdir(path)
	files.sort()
	index = 0
	for file in files:
		new_path = path + '/' + file;
		if os.path.isdir(new_path):
			getAllfiles(new_path)
		elif os.path.isfile(new_path):
			is_pdf = file.split('.')[-1]
			if is_pdf != 'pdf':
				continue
			index = dealPerPdf(path, file, index)
			index = index+1
 
def DealBatchPdf(path):
	getAllfiles(path)
 
 
if __name__ == '__main__':
	# path = os.getcwd()
	path = './'
	is_batch_deal = True
	if is_batch_deal:
		DealBatchPdf(path)
	else:
		filename = './1.pdf' #要处理的pdf文件名
		dealPerPdf(path, filename, 0)