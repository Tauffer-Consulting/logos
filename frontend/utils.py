from pypdf import PdfReader
import base64
import io
import os
import openai


def pre_parse_pdf(base64_pdf_bytestring: str, use_openai: bool = False) -> dict:
    # Extract the base64 encoded data from the string
    base64_data = base64_pdf_bytestring.split(",")[1]

    # Decode the base64 data to a byte stream
    pdf_bytes = base64.b64decode(base64_data)

    # Create a PdfReader object using the byte stream
    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages_list = [p for p in reader.pages]
    first_pages_content = " ".join([p.extract_text().replace("\n", " ").replace("..", "") for p in pages_list[0:5]])[0:2000]
    if use_openai:
        return extract_metadata_openai(text_content=first_pages_content)
    else:
        return {"title": "something", "author": "someone", "year": "2000"}


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


def add_pdf_to_db(base64_pdf_bytestring: str, title: str, author: str, year: str) -> None:
    full_text = parse_full_pdf(base64_pdf_bytestring=base64_pdf_bytestring)
    sentences = sentences_from_full_text(full_text=full_text, max_length=2000)
    result = add_sentences_to_db(sentences=sentences, title=title, author=author, year=year)
    return result


def parse_full_pdf(base64_pdf_bytestring: str) -> dict:
    # Extract the base64 encoded data from the string
    base64_data = base64_pdf_bytestring.split(",")[1]

    # Decode the base64 data to a byte stream
    pdf_bytes = base64.b64decode(base64_data)

    # Create a PdfReader object using the byte stream
    reader = PdfReader(io.BytesIO(pdf_bytes))

    pages_list = [p for p in reader.pages]
    full_text = " ".join([p.extract_text().replace("\n", " ").replace("..", "") for p in pages_list])
    return full_text


def sentences_from_full_text(full_text: str, max_length: int=2000) -> list:
    sentences = full_text.split(". ")
    sentences_list = list()
    last_sentence = sentences[0]
    for i, s in enumerate(sentences[1:]):
        combined_sentence = last_sentence + ". " + s
        if len(combined_sentence) > 2000:
            sentences_list.append(last_sentence)
            last_sentence = s
        else:
            last_sentence = combined_sentence
            if i == len(sentences) - 2:
                sentences_list.append(last_sentence)
    return sentences_list


def add_sentences_to_db(sentences: list, title: str, author: str, year: str) -> None:
    # TODO: vectorize and add sentences to db
    return "success"