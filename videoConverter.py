import speech_recognition as sr
import os


videoList = []
for file in os.listdir("./videoList"):
    print(file)
    if file.endswith('.wav'):
    	videoList.append(file)




for filePath in videoList:

	r = sr.Recognizer()
	videoFilePath = './videoList/' + filePath
	print(videoFilePath)
	harvard = sr.AudioFile(videoFilePath)
	with harvard as source:
		r.adjust_for_ambient_noise(source, duration=0.5)
		audio = r.record(source)

	# result = r.recognize_google(audio, show_all=True)

	result = r.recognize_google(audio)


	size = len(filePath)
	txtFilePath = filePath[:size - 4]
	txtFilePath = './txtList/' + txtFilePath + '.txt'
	print(txtFilePath)
	with open(txtFilePath,"w+") as f:
		f.writelines(result)