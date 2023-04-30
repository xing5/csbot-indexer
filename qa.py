from langchain.vectorstores import Weaviate
import weaviate
import logging
import os
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI

client = weaviate.Client(url=os.environ['WEAVIATE_URL'])
vectorstore = Weaviate(client, "DocumentChunk", "chunk")

def answer_question(question: str) -> str:
    docs = vectorstore.similarity_search(question)
    logging.info(f"Found {len(docs)} documents: {docs}")
    chain = load_qa_chain(OpenAI(temperature=0.2), chain_type="stuff")
    return chain.run(input_documents=docs, question=question)
