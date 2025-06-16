import openai
import requests
import simplejson
import time
from model import Model
from utils import LOG

class GLMModel(Model):
    def __init__(self, model_url: str):
        self.model = "chatglm2-6b"
        openai.api_base = model_url
        openai.api_key = "none"

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                if self.model == "chatglm2-6b":
                    response = openai.ChatCompletion.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": Model.MODEL_ROLE_TRANSLATE_PROMPT},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    translation = response.choices[0].message['content'].strip()
                else:
                    response = openai.Completion.create(
                        model=self.model,
                        prompt=prompt,
                        max_tokens=150,
                        temperature=0
                    )
                    translation = response.choices[0].text.strip()

                return translation, True
            except openai.error.RateLimitError:
                attempts += 1
                if attempts < 3:
                    LOG.warning("Batas permintaan tercapai. Menunggu 60 detik sebelum mencoba lagi.")
                    time.sleep(60)
                else:
                    raise Exception("Batas permintaan tercapai. Upaya maksimal terlampaui.")
            except requests.exceptions.RequestException as e:
                raise Exception(f"Kesalahan request: {e}")
            except requests.exceptions.Timeout as e:
                raise Exception(f"Request timeout: {e}")
            except simplejson.errors.JSONDecodeError:
                raise Exception("Respon tidak berformat JSON yang valid.")
            except Exception as e:
                raise Exception(f"Terjadi kesalahan tidak dikenal: {e}")
        return "", False
