from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import ListProperty
import pickle

from googSpeech import MicrophoneStream #, listen_print_loop
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

TOP_K = 3


kv = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        Button:
            text: 'Click to Listen'
            on_press: app.buildEmbeddings()
        Button:
            text: 'Selection A'
            on_press: app.showFirstSelection()
        Button:
            text: 'Selection B'
            on_press: app.showSecondSelection()
        Button:
            text: 'Selection C'
            on_press: app.showThirdSelection()
        Button:
            text: 'Clear Data'
            on_press: target.clear_widgets()
    ScrollView:
        GridLayout:
            cols: 1
            id: target
            size_hint_y: None
            text_size: self.width, None
            height: self.minimum_height
<MyLabel@Label>:
    size_hint_y: None
    height: self.texture_size[1]
    text_size: self.width, None
'''

def listen_print_loop(top_results, responses, embedder, document_embeddings, sentences, query):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    print("in listen print")
    num_chars_printed = 0
    for index, response in enumerate(responses):
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript
        # print(transcript[:-10])
        # all_chars = ""
        # for word in transcript:
        #     all_chars += word
        # print(len(all_chars))

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result

        overwrite_chars = " " * (num_chars_printed - len(transcript))

        if not result.is_final:
            # sys.stdout.write(transcript + overwrite_chars + "\r")
            # sys.stdout.flush()

            num_chars_printed = len(transcript)

        else:
            query_words = transcript + overwrite_chars
            q_embedding = embedder.doc_encode(query_words)
            # print(index)
            query.append(query_words)
            print(query_words)
            # print(q_embedding)

            cosine_scores = util.cos_sim(q_embedding, document_embeddings)
            # print(cosine_scores[0])

            sentence_indices = np.argpartition(np.asarray(cosine_scores[0]), -TOP_K)[-TOP_K:].astype(int)
            # indices in reverse order i.e. increasing similarity scores
            # print(sentence_indices.astype(int))

            for sentence_index in sentence_indices:
                top_results.append(sentences[sentence_index])
                # print(sentences[sentence_index])

            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            break
            if re.search(r"\b(exit|quit)\b", transcript, re.I):
                print("Exiting..")
                break

            num_chars_printed = 0

class RemembranceAgent(App):



    print("loading embedder")
    embedder = ProjectTransformer('all-mpnet-base-v2')
    docDict = pickle.load(open('test.pkl', 'rb'))

    # print(docDict)
    document_embeddings = []
    sentences = []
    for key in docDict:
        # print(docDict[key][0])
        document_embeddings.append(embedder.doc_encode(docDict[key][0]))
        sentences.append(docDict[key][0])
    print("embedder loaded")
    top_results = ListProperty()
    queryWords = []

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


    def build(self):
        return Builder.load_string(kv)

    def buildEmbeddings(self):

        # docDict = pickle.load(open('test.pkl', 'rb'))
        #
        # # print(docDict)
        # document_embeddings = []
        # sentences = []
        # for key in docDict:
        #     # print(docDict[key][0])
        #     document_embeddings.append(RemembranceAgent.embedder.doc_encode(docDict[key][0]))
        #     sentences.append(docDict[key][0])

        # sentences = [
        #     "hello my name is Gregory a bowed and in this first lesson we're going to talk about the history of interactive Computing but before we get into any of the details I want an outline for you a framework they were going to use to tell the difference or distinguish between the various generations of change over time the way this Frameworks going to go is that for each generation I'll point out what the relevant technology was and the trends that led to a an embodiment of what at that time was a computer then I'll step back and talk about The Visionaries whose ideas lead to that canonical technology and then we'll talk a little bit about the default or assumed or even some cases emergent interaction Style by which I mean the relationship between the humans and the Computing technology and in some ways this is indicated by a ratio between how many humans in Iraq act with how many examples are instances of the Computing technology and then I'll talk about initial applications that drove the adoption of this canonical technology and then we're going to see all the way to a supposed future of computational material we're going to do these one at a time",
        #     "speaking of rapid prototyping I think the next slide actually shows where you're starting to use the phone or the Computing and the networking receiving Wi-Fi and Bluetooth but also starting to play with the actual shape of the touchpad by marking off areas of the phone so you can only use certain parts for touching his stuff precisely right what what size should be on the phone into different shapes and sizes to see where we can still do text where it is a small thing you take with you for meetings that the project on the wall and so this is this display really is a projector with the brightness turn down way down so that you can see it but the I bought the area where you could see the display was very very small",
        #     "welcome back in this next series of lectures I'm going to I'm Gregory about I'm going to talk about Generation 4 and my partners will help with this discussion about a generation of technology that moves Beyond Wiser's Vision just to remind you we've already at this point talk about three different generations of Technologies the Mainframe the personal computer and why is there's no should have the inch foot in yard scales of Technology we talked about them and gave an idea of the human computer relationship and the applications that drove adoption and then were took advantage of the widely adopted Technologies in this series of lectures pretty good job of predicting what the technology Trends would be into the 2,000 don't you guys think good job and allowed Technologies the next series of lectures are going to go into detail on each of these four Technologies",
        #     "my name is India Irish program at Georgia Tech and today it's important to consider how your system affect users workload",
        #     "hello again I'm Gregory about and in this lecture when talk to you about the foot scale of the Generation 3 Technologies again to remind you mark Weiser introduced the notion of three conical Technologies in the UB count generation the inch the foot in the yard scale and will focus on the foot scaling this little lecture so by the 1st or electronic readers or e-readers like the Amazon Kindle that would allow people to carry around a library of books and some of them up and read them in a rather comfortable setting while you're walking but mostly while you were sitting at down in a comfortable setting you could carry it around with you or speaking to a device and in the project called the mpad they tried to explore how this portable pen-based and touch base could allow this form of interaction so that's the difference between the foot notebook",
        #     "arsenal soccer premier league champions",
        #     "machine learning principal component analysis k fold validation variance ",
        #     "hidden markov model speech recognition expectation grammars stochastic beam search"
        # ]
        # document_embeddings = []
        # for sentence in sentences:
        #     document_embeddings.append(RemembranceAgent.embedder.doc_encode(sentence))

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = RemembranceAgent.client.streaming_recognize(RemembranceAgent.streaming_config, requests)
            label = Factory.MyLabel(text='%s' % "Listening...")
            self.root.ids.target.add_widget(label)
            listen_print_loop(self.top_results, responses, RemembranceAgent.embedder,
                              RemembranceAgent.document_embeddings, RemembranceAgent.sentences, self.queryWords) ###UNCOMMENT FOR IMPLEMENT


    def showFirstSelection(self):
        # print("TOP RESULTS")
        # print(self.top_results[2])
        labelResult = Factory.MyLabel(text='%s : %s' % ("Processed Words: ", self.queryWords.pop()))
        self.root.ids.target.add_widget(labelResult)
        label = Factory.MyLabel(text='%s : %s' % ("First Result\n", self.top_results[TOP_K - 1]))
        self.root.ids.target.add_widget(label)

    def showSecondSelection(self):
        # print("TOP RESULTS")
        # for result in self.top_results:
        #     print(result)
        #
        # print(self.top_results[1])
        label = Factory.MyLabel(text='%s : %s' % ("Second Result\n", self.top_results[TOP_K - 2]))
        self.root.ids.target.add_widget(label)

    def showThirdSelection(self):
        # print("TOP RESULTS")
        # print(self.top_results[0])
        label = Factory.MyLabel(text='%s : %s' % ("Third Result\n", self.top_results[TOP_K - 3]))
        self.root.ids.target.add_widget(label)



if __name__ == '__main__':
    RemembranceAgent().run()