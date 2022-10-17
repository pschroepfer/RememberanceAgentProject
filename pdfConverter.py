import PyPDF2
import os

# wiki - https://www.askpython.com/python/examples/convert-pdf-to-txt
# wiki - https://stackoverflow.com/questions/55461041/how-to-convert-whole-pdf-to-text-in-python
 

pdfList = []
for file in os.listdir("./pdfList"):
    if file.endswith('.pdf'):
    	pdfList.append(file)

print(pdfList)
for pdf in pdfList:
	#create file object variable
	#opening method will be rb
	pdfFilePath = './pdfList/' + pdf
	pdffileobj=open(pdfFilePath,'rb')
	 
	#create reader variable that will read the pdffileobj
	pdfreader=PyPDF2.PdfFileReader(pdffileobj)

	text = ""
	for page_num in range(pdfreader.getNumPages()):
	    page = pdfreader.getPage(page_num)
	    text += page.extractText() + " "
	 
	size = len(pdf)
	txtFilePath = pdf[:size - 4]
	txtFilePath = './txtList/' + txtFilePath + '.txt'
	print(txtFilePath)
	with open(txtFilePath,"w+") as f:
		f.writelines(text)
