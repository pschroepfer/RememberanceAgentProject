from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.properties import ListProperty
import pickle
import threading

from utils.speech_utils import listen_print_loop, transcribe, testtrans, MicrophoneStream
from embedders.Transformer import Transformer
import asynckivy as ak

import os
from google.cloud import speech


TOP_K = 3
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


kivy_ui_config = '''
BoxLayout:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Click to Listen'
            on_press: app.clear_selection()
            on_press: app.buildEmbeddings()
            on_release: app.pasteContent()
        Button:
            text: 'Choice 1'
            on_press: app.showFirstSelection()
        Button:
            text: 'Choice 2'
            on_press: app.showSecondSelection()
        Button:
            text: 'Choice 3'
            on_press: app.showThirdSelection()
        Button:
            text: 'Clear'
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


RATE = 16000

class RemembranceAgent(App):
    print("loading embedder")
    embedder = Transformer('all-mpnet-base-v2')
    print("embedder loaded")

    print("loading docs")
    docDict = pickle.load(open('documents.pkl', 'rb'))
    sentences = []
    document_embeddings = pickle.load(open('embeddings.pkl', 'rb'))
    for key in docDict:
        sentences.append(docDict[key][0])
    print("docs loaded")


    # embedding_dict = {}
    # document_embeddings = []
    # for key in docDict:
    #     print(key)
    #     document_embedding = embedder.doc_encode(docDict[key][0])
    #     print(document_embedding)
    #     document_embeddings.append(document_embedding)
    #     embedding_dict.update({key: document_embedding})
    #     sentences.append(docDict[key][0])
    # pickle.dump(document_embeddings, open('embeddings.pkl', 'wb'))




    top_results = ListProperty()
    queryWords = []


    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = \
    "ubicomp-367400-21c3fbefedbb.json"
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
        return Builder.load_string(kivy_ui_config)

    def buildEmbeddings(self):
        label = Factory.MyLabel(text='%s' % "Listening...\n")
        self.root.ids.target.add_widget(label)
        threading.Thread(target=self.test).start()

    def pasteContent(self):
        Clock.schedule_once(self.pasteContentDelayed, 1.5)

    def pasteContentDelayed(self, dt):
        if self.queryWords:
            processed_words = self.queryWords.pop() + "\n"
            labelResult = Factory.MyLabel(text='%s%s' % ("Processed Words: ", processed_words))
            self.root.ids.target.add_widget(labelResult)
        else:
            Clock.schedule_once(self.pasteContentDelayed, 1.5)

    def test(self):
        with MicrophoneStream() as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            responses = RemembranceAgent.client.streaming_recognize(RemembranceAgent.streaming_config, requests)
            listen_print_loop(TOP_K, self.top_results, responses, RemembranceAgent.embedder,
                              RemembranceAgent.document_embeddings, RemembranceAgent.sentences, self.queryWords) ###UNCOMMENT FOR IMPLEMENT

    def showFirstSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("First Result\n", self.top_results[TOP_K - 1] + "\n"))
        self.root.ids.target.add_widget(label)

    def showSecondSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("Second Result\n", self.top_results[TOP_K - 2] + "\n"))
        self.root.ids.target.add_widget(label)

    def showThirdSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("Third Result\n", self.top_results[TOP_K - 3] + "\n"))
        self.root.ids.target.add_widget(label)

    def clear_selection(self):
        self.top_results = []



if __name__ == '__main__':
    RemembranceAgent().run()
