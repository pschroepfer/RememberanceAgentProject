from kivy.app import App
from kivy.clock import Clock, _default_time as time  # ok, no better way to use the same clock as kivy, hmm
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import ListProperty

from googSpeech import MicrophoneStream, listen_print_loop
from ProjectSentenceTransformer import *
from sentence_transformers import util
import numpy as np

import re
import sys
import os

from google.cloud import speech

import pyaudio
from six.moves import queue

MAX_TIME = 1/60.

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

kv = '''
BoxLayout:
    
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Click to Listen'
            on_press: app.buildEmbeddings()
        Button:
            text: 'Selection A'
            on_press: app.consommables.extend(range(100))
        Button:
            text: 'Selection B'
            on_press: app.consommables.extend(range(1000))
        Button:
            text: 'Selection C'
            on_press: target.clear_widgets()   
    ScrollView:
        GridLayout:
            cols: 1
            id: target
            size_hint: 1, None
            height: self.minimum_height
<MyLabel@Label>:
    size_hint_y: None
    height: self.texture_size[1]
'''


class ProdConApp(App):
    consommables = ListProperty([])

    def build(self):
        Clock.schedule_interval(self.consume, 0)
        return Builder.load_string(kv)

    def buildEmbeddings(self):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
            "ubicomp-367400-9ac3dff60117.json"
        language_code = "en-US"  # a BCP-47 language tag

        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        print("loading embedder")
        embedder = ProjectTransformer('all-mpnet-base-v2')
        print("embedder loaded")

        sentences = [
            "hello my name is Gregory a bowed and in this first lesson we're going to talk about the history of interactive Computing but before we get into any of the details I want an outline for you a framework they were going to use to tell the difference or distinguish between the various generations of change over time the way this Frameworks going to go is that for each generation I'll point out what the relevant technology was and the trends that led to a an embodiment of what at that time was a computer then I'll step back and talk about The Visionaries whose ideas lead to that canonical technology and then we'll talk a little bit about the default or assumed or even some cases emergent interaction Style by which I mean the relationship between the humans and the Computing technology and in some ways this is indicated by a ratio between how many humans in Iraq act with how many examples are instances of the Computing technology and then I'll talk about initial applications that drove the adoption of this canonical technology and then we're going to see all the way to a supposed future of computational material we're going to do these one at a time",
            "speaking of rapid prototyping I think the next slide actually shows where you're starting to use the phone or the Computing and the networking receiving Wi-Fi and Bluetooth but also starting to play with the actual shape of the touchpad by marking off areas of the phone so you can only use certain parts for touching his stuff precisely right what what size should be on the phone into different shapes and sizes to see where we can still do text where it is a small thing you take with you for meetings that the project on the wall and so this is this display really is a projector with the brightness turn down way down so that you can see it but the I bought the area where you could see the display was very very small",
            "welcome back in this next series of lectures I'm going to I'm Gregory about I'm going to talk about Generation 4 and my partners will help with this discussion about a generation of technology that moves Beyond Wiser's Vision just to remind you we've already at this point talk about three different generations of Technologies the Mainframe the personal computer and why is there's no should have the inch foot in yard scales of Technology we talked about them and gave an idea of the human computer relationship and the applications that drove adoption and then were took advantage of the widely adopted Technologies in this series of lectures pretty good job of predicting what the technology Trends would be into the 2,000 don't you guys think good job and allowed Technologies the next series of lectures are going to go into detail on each of these four Technologies",
            "my name is India Irish program at Georgia Tech and today it's important to consider how your system affect users workload",
            "hello again I'm Gregory about and in this lecture when talk to you about the foot scale of the Generation 3 Technologies again to remind you mark Weiser introduced the notion of three conical Technologies in the UB count generation the inch the foot in the yard scale and will focus on the foot scaling this little lecture so by the 1st or electronic readers or e-readers like the Amazon Kindle that would allow people to carry around a library of books and some of them up and read them in a rather comfortable setting while you're walking but mostly while you were sitting at down in a comfortable setting you could carry it around with you or speaking to a device and in the project called the mpad they tried to explore how this portable pen-based and touch base could allow this form of interaction so that's the difference between the foot notebook",
            "arsenal soccer premier league champions",
            "machine learning principal component analysis k fold validation variance ",
            "hidden markov model speech recognition expectation grammars stochastic beam search"
        ]
        document_embeddings = []
        for sentence in sentences:
            document_embeddings.append(embedder.doc_encode(sentence))

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = client.streaming_recognize(streaming_config, requests)
            # label = Factory.MyLabel(
            #     text='%s : %s' % ("Google Heard", responses[0]))
            # self.root.ids.target.add_widget(label)
            # print(responses)
            # Now, put the transcription responses to use.

            listen_print_loop(responses, embedder, document_embeddings, sentences) ###UNCOMMENT FOR IMPLEMENT
            stream.__exit__(None, None, None)


    def consume(self, *args):
        while self.consommables and time() < (Clock.get_time() + MAX_TIME):
            item = self.consommables.pop(0)  # i want the first one
            label = Factory.MyLabel(
                text='%s : %s : %s' % (item, Clock.get_time(), time()))
            self.root.ids.target.add_widget(label)


if __name__ == '__main__':
    ProdConApp().run()