class Model:
    MODEL_ROLE_TRANSLATE_PROMPT = (
        "Kamu adalah mesin penerjemah. Hanya terjemahkan teks dari Bahasa Inggris ke Bahasa Indonesia. "
        "Jangan berikan penjelasan apapun. Untuk nama, alamat, hyperlink, rumus, dan kutipan ilmiah, "
        "biarkan dalam bahasa aslinya tanpa diterjemahkan."
    )
    
    MODEL_ROLE_TRANSLATE_PROMPT_plus = (
        MODEL_ROLE_TRANSLATE_PROMPT +
        " Namun, untuk paragraf atau kalimat panjang, kamu boleh sedikit menyesuaikan agar lebih alami."
    )

    def make_text_prompt(self, text: str, target_language: str) -> str:
        return f"Terjemahkan teks berikut ke dalam {target_language}. Jangan beri penjelasan. Teks: {text}"

    def make_table_prompt(self, table: str, target_language: str) -> str:
        return f"Terjemahkan tabel berikut ke dalam {target_language}, jaga format dan spasi:\n{table}"

    def translate_prompt(self, content, target_language: str) -> str:
        return self.make_text_prompt(content, target_language)

    def make_request(self, prompt):
        raise NotImplementedError("Sub-class harus mengimplementasikan make_request.")
