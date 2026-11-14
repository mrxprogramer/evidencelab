# Example system architecture

EvidenceLab is a document retrieval service. The HTTP layer is implemented with FastAPI. Uploaded text is normalized and split into overlapping chunks. SQLite stores document metadata and chunk text. The baseline retrieval method is a transparent BM25-style lexical ranker. Query responses include the source document, chunk identifier, optional page number, score, and excerpt.

The baseline deliberately uses extractive evidence snippets rather than generating unsupported prose. It can run on a CPU and does not require a hosted model API. PDF text extraction is available through the optional pypdf dependency. Scanned PDFs require OCR, which is outside the baseline scope.

Retrieval evaluation reports Recall at K and Mean Reciprocal Rank at K. These metrics measure whether relevant chunks are retrieved; they do not establish answer correctness, factuality, or clinical validity.
