import logging
from financial_agent.embeddings import load_and_split, build_index

logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(levelname)s — %(message)s")
logger = logging.getLogger(__name__)


def main():
    logger.info("Iniciando ingestão da base de conhecimento...")
    chunks = load_and_split()
    build_index(chunks)
    logger.info("Setup concluído. Base indexada com %d chunks.", len(chunks))


if __name__ == "__main__":
    main()
