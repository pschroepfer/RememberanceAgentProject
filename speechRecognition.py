import speech_recognition as sr


def recognize_speech_from_mic(recognizer, microphone):

    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    response = {
        "success": True,
        "error": None,
        "transcription": None
    }

    try:
        response["transcription"] = recognizer.recognize_google(audio)
    except sr.RequestError:
        # API not reached
        response["success"] = False
        response["error"] = "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        response["error"] = "Unable to recognize speech"

    return response


if __name__ == "__main__":

    var = input("Start Recording? yes or no?")
    print(var)

    if var == 'yes' or var == 'Yes':
        while var == 'yes':
            # create recognizer and mic instances
            recognizer = sr.Recognizer()
            microphone = sr.Microphone()
            print("Speak!")
            language = recognize_speech_from_mic(recognizer, microphone)
            print(language["transcription"])
            var = input("keep recording? yes or no?")
            if var == 'no':
                break
