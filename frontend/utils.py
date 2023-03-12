from pypdf import PdfReader
import base64
import io
import os
import openai


def parse_pdf(base64_pdf_bytestring: str) -> dict:
    # Extract the base64 encoded data from the string
    base64_data = base64_pdf_bytestring.split(",")[1]

    # Decode the base64 data to a byte stream
    pdf_bytes = base64.b64decode(base64_data)

    # Create a PdfReader object using the byte stream
    reader = PdfReader(io.BytesIO(pdf_bytes))

    first_page = reader.pages[0]

    pages_list = [p for p in reader.pages]
    first_pages_content = " ".join([p.extract_text().replace("\n", " ").replace("..", "") for p in pages_list[0:4]])[0:3000]
    return extract_metadata_openai(text_content=first_pages_content)


def extract_metadata_openai(text_content: str) -> dict:

    openai.api_key = os.environ["OPENAI_API_KEY"]

    prompt = f"""Given the text below, extract these three pieces of information: 
1) title: 
2) author: 
3) publication year: (should be just a number)

Text:
{text_content}

Information:"""

    messages = [{"role": "user", "content": prompt}]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1,
        max_tokens=100,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["\n"]
    )
    response_string = response["choices"][0]["message"]["content"].lower()
    metadata = {
        "title": response_string.split("title:")[1].split("2")[0].split("\n:")[0].strip(),
        "author": response_string.split("author:")[1].split("3")[0].split("\n")[0].strip(),
        "year": response_string.split("year:")[1].split("\n")[0].strip(),
    }
    return metadata