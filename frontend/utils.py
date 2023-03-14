from pypdf import PdfReader
import base64
import io
import os
import openai
from qdrant_client import QdrantClient
from qdrant_client.http.models import models
import cohere
from config import config
from uuid import uuid4
from langdetect import detect
from iso639 import Lang


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
    sentences = sentences_from_full_text(full_text=full_text, max_length=1000)
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
        if len(combined_sentence) > max_length:
            sentences_list.append(last_sentence.strip())
            last_sentence = s
        else:
            last_sentence = combined_sentence
            if i == len(sentences) - 2:
                sentences_list.append(last_sentence.strip())
    return sentences_list


def get_cohere_embeddings(texts: list, model: str = None) -> list:
    cohere_client = cohere.Client(config.COHERE_API_KEY)
    if model is None:
        model = 'multilingual-22-12'

    response = cohere_client.embed(
        texts=texts,
        model=model,
    )
    return response


def add_sentences_to_db(sentences: list, title: str, author: str, year: str) -> None:
    collection_name = "hackathon_collection"
    texts = []
    for sentence in sentences:
        texts.append(f'{title} {author} {year}: {sentence}')
    
    embeddings = get_cohere_embeddings(texts=texts)

    db_client = QdrantClient(
        host=config.QDRANT_HOST,
        api_key=config.QDRANT_API_KEY,
    )

    batch_data = {
        "ids": [],
        "payloads": [],
        "vectors": [],
    }
    for embedding, sentence in zip(embeddings, sentences):
        batch_data['ids'].append(str(uuid4()))
        payload = {
            "author": author,
            "title": title,
            "year": year,
            "text": sentence,
        }
        batch_data['payloads'].append(payload)
        batch_data['vectors'].append([float(e) for e in embedding])

    db_client.upsert(
        collection_name=f"{collection_name}",
        points=models.Batch(
            ids=batch_data['ids'],
            payloads=batch_data['payloads'],
            vectors=batch_data['vectors']
        ),
    )

    return "success"


def get_qdrant_response(question, limit: int = 5):
    embeddings = get_cohere_embeddings(texts=[question])
    embedding = [float(e) for e in embeddings.embeddings[0]]

    db_client = QdrantClient(
        host=config.QDRANT_HOST,
        api_key=config.QDRANT_API_KEY,
    )

    response = db_client.search(
        collection_name="hackathon_collection",
        query_vector=embedding,
        limit=limit,
    )
    return response


def get_openai_response(prompt):
    messages = [{"role": "user", "content": prompt}]
    
    openai_model = 'gpt-3.5-turbo'
    response = openai.ChatCompletion.create(
        model=openai_model,
        messages=messages,
        temperature=0.1,
        max_tokens=1000,
        # frequency_penalty=0.0,
        # presence_penalty=0.0,
        # stop=["\n"]
    )
    return response


def detect_language(text: str, module: str="python"):
    if module == "python":
        return Lang(detect(text)).name
    elif module == "cohere":
        co = cohere.Client(config.COHERE_API_KEY)
        r = co.detect_language(texts=[text])
        return r.results[0].language_name