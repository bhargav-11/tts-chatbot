from chat_utils import openai_client
import os

def convert_audio_to_text(audio_file_path):
  """
    Convert audio file to text using OpenAI's Whisper API.

    Args:
        audio_file_path (str): Path to the audio file.

    Returns:
        str: Text extracted from the audio file.
    """
  try:
    with open(audio_file_path, "rb") as audio_file:
      response = openai_client.audio.transcriptions.create(
          model="whisper-1", file=audio_file, response_format="json")
      return response.text
  except Exception as e:
    print("Error converting audio to text:", e)
    return None
  finally:
     if audio_file_path:
        os.remove(audio_file_path)

def convert_text_to_audio(text, output_file_path):
    """ 
    COnvert text to audio using OpenAI's Whisper API.

    Args:
        text (str): Text to be converted to audio.
        output_file_path (str): Path to save the audio file.
    Returns:
        None
    """
    try:
        response = openai_client.audio.speech.create(model="tts-1",
                                                     voice="onyx",
                                                         input=text)
        response.write_to_file(output_file_path)
    except Exception as e:
        print("Error converting text to audio:", e)