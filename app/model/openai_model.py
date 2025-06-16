from openai import OpenAI
from model import Model
from utils import LOG
import time
import requests

class OpenAIModel(Model):
    def __init__(self, model: str, api_key: str, api_base: str = 'https://api.openai.com/v1'):
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )

    def make_request(self, prompt):
        attempts = 0
        while attempts < 3:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": Model.MODEL_ROLE_TRANSLATE_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                translation = response.choices[0].message.content.strip()
                return translation, True

            except Exception as e:
                if "Rate limit" in str(e):
                    attempts += 1
                    if attempts < 3:
                        LOG.warning("Rate limit tercapai. Tunggu 60 detik sebelum mencoba lagi.")
                        time.sleep(60)
                        continue
                    else:
                        raise Exception("Rate limit tercapai. Upaya maksimal terlampaui.")
                elif isinstance(e, requests.exceptions.RequestException):
                    raise Exception(f"Terjadi kesalahan request: {e}")
                elif isinstance(e, requests.exceptions.Timeout):
                    raise Exception(f"Request timeout: {e}")
                elif isinstance(e, simplejson.errors.JSONDecodeError):
                    raise Exception("Respon tidak berformat JSON valid.")
                else:
                    raise Exception(f"Kesalahan tidak dikenal: {e}")

        return "", False
