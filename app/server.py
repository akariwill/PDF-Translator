import streamlit as st
import yaml, os

from translator.progress import Progress
from translator.doc_parser import DocParser
from utils import ArgumentParser, ConfigLoader, LOG
from model import GLMModel, OpenAIModel

# Gunakan session_state modern
def get_session_state(**kwargs):
    for key, value in kwargs.items():
        if key not in st.session_state:
            st.session_state[key] = value
    return st.session_state

def get_config_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_name = 'GUI-config.yaml'
    config_dir = os.path.join(current_dir, 'config')
    config_file_path = os.path.join(config_dir, config_file_name)
    return config_file_path

def load_config():
    config_file_path = get_config_path()

    # Jika file belum ada, buat dengan default kosong
    if not os.path.exists(config_file_path):
        os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
        default_config = {
            'model_type_name': 'GLMModel',
            'GLMModel': {
                'model_url': 'http://localhost:8000/v1',
                'timeout': 500,
            },
            'OpenAIModel': {
                'model': 'gpt-3.5-turbo',
                'api_key': '',
                'api_base': '',
            },
            'processPageNum': 0,
            'target_language': 'Indonesian',
        }
        with open(config_file_path, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)

    with open(config_file_path, 'r') as infile:
        data = yaml.safe_load(infile)

    return data if data else {}


def store_config(data: dict):
    config_file_path = get_config_path()
    os.makedirs(os.path.dirname(config_file_path), exist_ok=True)
    with open(config_file_path, 'w+') as outfile:
        yaml.dump(data, outfile, default_flow_style=False)
    return config_file_path

def make_sidebar():
    data = load_config()

    model_type = data.get('model_type_name', 'GLMModel')
    model_type = st.sidebar.selectbox('Model Type', ['GLMModel', 'OpenAIModel'], index=['GLMModel', 'OpenAIModel'].index(model_type))

    if model_type == 'GLMModel':
        glm_model_url = data.get(model_type, {}).get('model_url', 'http://localhost:8000/v1')
        glm_model_url = st.sidebar.text_input('GLM Model URL', glm_model_url)
        timeout = data.get(model_type, {}).get('timeout', 500)
        timeout = st.sidebar.number_input('Timeout', min_value=1, max_value=1000, value=timeout)
        data[model_type] = {
            'model_url': glm_model_url,
            'timeout': timeout,
        }
    else:
        openai_model = data.get(model_type, {}).get('model', 'gpt-3.5-turbo')
        openai_model = st.sidebar.text_input('OpenAI Model', openai_model)
        openai_api_key = data.get(model_type, {}).get('api_key', '')
        openai_api_key = st.sidebar.text_input('OpenAI API Key', openai_api_key)
        api_base = data.get(model_type, {}).get('api_base', '')
        api_base = st.sidebar.text_input('OpenAI API base url', api_base)

        data[model_type] = {
            'model': openai_model,
            'api_key': openai_api_key,
            'api_base': api_base,
        }

    data['model_type_name'] = model_type
    processPageNum = data.get('processPageNum', 0)
    processPageNum = st.sidebar.number_input('Halaman maksimum (0 = semua)', processPageNum)
    data['processPageNum'] = processPageNum

    target_language = data.get('target_language', 'Indonesian')
    target_language = st.sidebar.text_input('Target Language', target_language)
    data['target_language'] = target_language

    return data

def getModel(config):
    model_type_name = config.get('model_type_name', '')

    if model_type_name == 'OpenAIModel':
        model_name = config['OpenAIModel']['model']
        api_key = config['OpenAIModel']['api_key']
        api_base = config['OpenAIModel']['api_base']
        model = OpenAIModel(model=model_name, api_key=api_key, api_base=api_base)
    else:
        model_url = config['GLMModel']['model_url']
        model = GLMModel(model_url=model_url)

    return model

def main():
    session_state = get_session_state(processed_files=[])

    config_data = make_sidebar()
    config_file_path = store_config(config_data)
    file_exists = os.path.isfile(config_file_path)

    if not file_exists:
        st.sidebar.warning("Silakan atur konfigurasi terlebih dahulu di sidebar.")
        return

    uploaded_files = st.file_uploader("Pilih PDF untuk diterjemahkan", type="pdf", accept_multiple_files=True, help="Unggah satu atau beberapa file PDF")

    cur_task_text = st.empty()
    progress_text = st.empty()
    progress_bar = st.progress(0)
    progress = Progress(progress_bar, progress_text)

    temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    config_loader = ConfigLoader(config_file_path)
    config = config_loader.load_config()
    LOG.info(config)

    model = getModel(config)
    processPageNum = config['processPageNum']
    target_language = config['target_language']

    if uploaded_files:
        for index, uploaded_file in enumerate(uploaded_files):
            if uploaded_file.name in session_state.processed_files:
                continue

            file_name = uploaded_file.name
            uploaded_file_path = os.path.join(temp_dir, file_name)

            with open(uploaded_file_path, 'wb') as out:
                out.write(uploaded_file.getvalue())

            cur_task_text.text(f'⏳ Sedang memproses file {index + 1}: {file_name}')
            result_docx_file_path = os.path.join(temp_dir, file_name + "_result.docx")

            if not os.path.isfile(result_docx_file_path):
                docParser = DocParser(model, progress, target_language)
                docParser.doTrans(
                    file_name=file_name,
                    pdf_input_path=uploaded_file_path,
                    result_docx_file_path=result_docx_file_path,
                    temp_source_path=temp_dir,
                    endPos=processPageNum
                )

            if os.path.isfile(result_docx_file_path):
                with open(result_docx_file_path, 'rb') as f:
                    st.download_button(
                        label=f"⬇️ Unduh hasil terjemahan: {file_name}",
                        data=f,
                        file_name=os.path.basename(result_docx_file_path),
                        mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    )

                session_state.processed_files.append(uploaded_file.name)

if __name__ == "__main__":
    main()
