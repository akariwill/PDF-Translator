import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel
from translator import PDFTranslator

if __name__ == "__main__":
    argument_parser = ArgumentParser()
    args = argument_parser.parse_arguments()
    config_loader = ConfigLoader(args.config)

    config = config_loader.load_config()

    model_type = args.model_type

    if model_type == 'OpenAIModel':
        model_name = args.openai_model if args.openai_model else config['OpenAIModel']['model']
        api_key = args.openai_api_key if args.openai_api_key else config['OpenAIModel']['api_key']
        model = OpenAIModel(model=model_name, api_key=api_key)  
    else:
        model_url = args.glm_model_url if args.glm_model_url else config['GLMModel']['model_url']
        # timeout = args.timeout if args.timeout else config['GLMModel']['timeout']
        model = GLMModel(model_url=model_url)

    pdf_file_path = args.book if args.book else config['common']['book']
    file_format = args.file_format if args.file_format else config['common']['file_format']

    # Inisialisasi PDFTranslator dan mulai proses translate PDF
    translator = PDFTranslator(model)
    translator.translate_pdf(pdf_file_path, file_format)
