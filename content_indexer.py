from langchain.text_splitter import TokenTextSplitter
import logging
from urllib.parse import urlparse
import weaviate
import os

_client = weaviate.Client(
    url=os.environ['WEAVIATE_URL'],
)


def create_schema_if_not_exists(client: weaviate.Client):
    """Create schema if not exists."""
    try:
        schema = client.schema.get(class_name="DocumentChunk")
        logging.debug(f"Schema exists: {schema}")
    except weaviate.exceptions.UnexpectedStatusCodeException as e:
        if e.status_code != 404:
            logging.error(f"Unexpected status code: {e}")
            raise e
        class_obj = {
            "class": "DocumentChunk",
            "description": "Chunks of documents crawled from given websites.",
            "properties": [
                {
                    "name": "domain",
                    "dataType": ["string"],
                    "description": "The domain of the crawled website",
                    "moduleConfig": {
                        "text2vec-transformers": {
                            "skip": True
                        }
                    }
                },
                {
                    "name": "url",
                    "dataType": ["string"],
                    "description": "The url where the chunk was found",
                    "moduleConfig": {
                        "text2vec-transformers": {
                            "skip": True
                        }
                    }
                },
                {

                    "name": "chunk",
                    "dataType": ["text"],
                    "description": "content of the chunk"
                }
            ],
            "vectorizer": "text2vec-transformers",
        }

        client.schema.create_class(class_obj)


def cleanup(domain: str) -> None:
    # remove existing chunks for this domain
    _client.batch.delete_objects(
        where={
            'operator': 'Equal',
            'path': ['domain'],
            'valueString': domain
        },
        class_name="DocumentChunk"
    )
    _client.schema.delete_class(class_name="DocumentChunk")


def index(url: str, content: str) -> None:
    """Index the content"""

    # use langchain to chunk the content
    text_splitter = TokenTextSplitter(chunk_size=250, chunk_overlap=30)
    texts = text_splitter.split_text(content)
    domain = urlparse(url).netloc

    logging.info(
        f"Given url {url} - Found {len(texts)} chunks to index: {texts}")

    create_schema_if_not_exists(_client)

    # cleanup(domain)

    # remove existing chunks for this url
    _client.batch.delete_objects(
        where={
            'operator': 'Equal',
            'path': ['url'],
            'valueString': url 
        },
        class_name="DocumentChunk"
    )

    for text in texts:
        _client.data_object.create(
            {
                "domain": domain,
                "url": url,
                "chunk": text
            },
            class_name="DocumentChunk"
        )

    logging.info(f"Indexed {len(texts)} chunks for url {url}")
