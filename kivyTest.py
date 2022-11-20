from __future__ import division

import kivy
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from functools import partial
import kivy.uix.floatlayout as floatLayout

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

RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

class FirstKivy(App):

    def disable(self, instance, *args):
        instance.disabled = True

    def update_listen(self, instance, *args):
        instance.text = "Recording Your Voice"

    def update_select(self, instance, *args):
        instance.text = "Selection Chosen"

    def buildEmbeddings(self):
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
            # print(responses)
            # Now, put the transcription responses to use.

            listen_print_loop(responses, embedder, document_embeddings, sentences)

    def start_main(self):
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
            # print(responses)
            # Now, put the transcription responses to use.

            listen_print_loop(responses, embedder, document_embeddings, sentences)

    def build(self):

        layout = floatLayout.FloatLayout()

        thisButton = Button(text="Click to Listen", pos=(50, 340), size_hint = (.25, .18))
        thisButton.bind(on_press = partial(self.disable, thisButton))
        thisButton.bind(on_press = partial(self.update_listen, thisButton))
        thisButton.bind(on_press = lambda x: self.start_main())

        thisButtonA = Button(text="Selection A", pos=(300, 450), size_hint=(.25, .15))
        thisButtonA.bind(on_press=partial(self.disable, thisButtonA))
        thisButtonA.bind(on_press=partial(self.update_select, thisButtonA))

        thisButtonB = Button(text="Selection B", pos=(300, 350), size_hint=(.25, .15))
        thisButtonB.bind(on_press=partial(self.disable, thisButtonB))
        thisButtonB.bind(on_press=partial(self.update_select, thisButtonB))

        thisButtonC = Button(text="Selection C", pos=(300, 250), size_hint=(.25, .15))
        thisButtonC.bind(on_press=partial(self.disable, thisButtonC))
        thisButtonC.bind(on_press=partial(self.update_select, thisButtonC))

        layout.add_widget(thisButton)
        layout.add_widget(thisButtonA)
        layout.add_widget(thisButtonB)
        layout.add_widget(thisButtonC)

        return layout

FirstKivy().run()