from kivy.app import App
from kivy.lang import Builder
from kivy.factory import Factory
from kivy.properties import ListProperty
import pickle

from utils.speech_utils import listen_print_loop, transcribe
from embedders.Transformer import Transformer


TOP_K = 3


kivy_ui_config = '''
BoxLayout:
    BoxLayout:
        orientation: 'vertical'
        Button:
            text: 'Click to Listen'
            on_press: app.buildEmbeddings()
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
    docDict = pickle.load(open('test.pkl', 'rb'))
    document_embeddings = []
    sentences = []
    for key in docDict:
        document_embeddings.append(embedder.doc_encode(docDict[key][0]))
        sentences.append(docDict[key][0])
    print("docs loaded")
    top_results = ListProperty()
    queryWords = []



    def build(self):
        return Builder.load_string(kivy_ui_config)

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


        label = Factory.MyLabel(text='%s' % "Listening...\n")
        self.root.ids.target.add_widget(label)
        google_transcription_results = transcribe()
        listen_print_loop(TOP_K, self.top_results, google_transcription_results, RemembranceAgent.embedder,
                    RemembranceAgent.document_embeddings, RemembranceAgent.sentences, self.queryWords) ###UNCOMMENT FOR IMPLEMENT
        
        labelResult = Factory.MyLabel(text='%s%s' % ("Processed Words: ", self.queryWords.pop() + "\n"))
        self.root.ids.target.add_widget(labelResult)

    def showFirstSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("First Result\n", self.top_results[TOP_K - 1] + "\n"))
        self.root.ids.target.add_widget(label)

    def showSecondSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("Second Result\n", self.top_results[TOP_K - 2] + "\n"))
        self.root.ids.target.add_widget(label)

    def showThirdSelection(self):
        label = Factory.MyLabel(text='%s%s' % ("Third Result\n", self.top_results[TOP_K - 3] + "\n"))
        self.root.ids.target.add_widget(label)

if __name__ == '__main__':
    RemembranceAgent().run()
