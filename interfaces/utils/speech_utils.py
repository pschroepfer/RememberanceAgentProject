import os
import pyaudio
import numpy as np

from google.cloud import speech
from sentence_transformers import util
from six.moves import queue

import asynckivy as ak


# import re
# import sys



RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self):
        self._rate = RATE
        self._chunk = CHUNK

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





def listen_print_loop(TOP_K, top_results, responses, embedder, document_embeddings, sentences, query):
    """
    Stores the most closely related documents in top_results.
    
    """
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

        transcript = result.alternatives[0].transcript
        overwrite_chars = " " * (num_chars_printed - len(transcript))
        if not result.is_final:
            num_chars_printed = len(transcript)
        else:
            query_words = transcript + overwrite_chars
            q_embedding = embedder.doc_encode(query_words)
            query.append(query_words)
            cosine_scores = util.cos_sim(q_embedding, document_embeddings)
            sentence_indices = np.argpartition(np.asarray(cosine_scores[0]), -TOP_K)[-TOP_K:].astype(int)
            # indices in reverse order i.e. increasing similarity scores
            for sentence_index in sentence_indices:
                top_results.append(sentences[sentence_index])
            break

def transcribe():
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
    with MicrophoneStream() as stream:
        audio_generator = stream.generator()
        requests = (
            speech.StreamingRecognizeRequest(audio_content=content)
            for content in audio_generator
        )
        responses = client.streaming_recognize(streaming_config, requests)
    return responses


from google.cloud import speech_v1
async def testtrans():

    # Create a client
    client = speech_v1.SpeechAsyncClient()

    # Initialize request argument(s)
    config = speech_v1.RecognitionConfig()
    config.language_code = "language_code_value"

    audio = speech_v1.RecognitionAudio()
    audio.content = b'content_blob'

    request = speech_v1.LongRunningRecognizeRequest(
        config=config,
        audio=audio,
    )

    # Make the request
    operation = client.long_running_recognize(request=request)

    print("Waiting for operation to complete...")

    response = ak.operation.result()

    # Handle the response
    print(response)