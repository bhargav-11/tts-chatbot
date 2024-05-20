from chat_utils import openai_client


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
