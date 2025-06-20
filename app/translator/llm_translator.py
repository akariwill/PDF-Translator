from model import Model
from utils import LOG

class LlmTranslator:
    def __init__(self, model: Model, target_language: str):
        self.model = model
        self.contentN = []
        self.target_language = target_language

    def translate_content(self, content: str):
        prompt = self.model.translate_prompt(content, self.target_language)
        LOG.debug(f"Prompt saat ini = {prompt}")
        translation, status = self.model.make_request(prompt)
        LOG.debug(f"Hasil terjemahan = {translation}")
        return translation
