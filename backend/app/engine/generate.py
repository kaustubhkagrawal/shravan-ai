import logging

from dotenv import load_dotenv

from app.engine.constants import DATA_DIR, STORAGE_DIR
from app.engine.context import create_service_context

from llama_index.readers.file.tabular_reader import CSVReader
from llama_index.readers.file.docs_reader import PDFReader

load_dotenv()

from llama_index import (
    SimpleDirectoryReader,
    VectorStoreIndex,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def generate_datasource(service_context):
    logger.info("Creating new index")
    # load the documents and create the index
    documents = SimpleDirectoryReader(
        DATA_DIR, file_extractor={".csv": CSVReader, ".pdf": PDFReader}
    ).load_data()
    index = VectorStoreIndex.from_documents(documents, service_context=service_context)
    # store it for later
    index.storage_context.persist(STORAGE_DIR)
    logger.info(f"Finished creating new index. Stored in {STORAGE_DIR}")


if __name__ == "__main__":
    service_context = create_service_context()
    generate_datasource(service_context)
