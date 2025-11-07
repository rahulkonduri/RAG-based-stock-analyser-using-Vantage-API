"""
Document processing for financial reports and filings
"""
import os
from typing import List, Dict
from pathlib import Path
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter
from rag_chatbot.src.config import Config


class DocumentProcessor:
    """Process financial documents for RAG system"""
     
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=Config.CHUNK_SIZE,
            chunk_overlap=Config.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        # Create directories if they don't exist
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.PROCESSED_DIR, exist_ok=True)
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text content from PDF file
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Extracted text content
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            print(f"Error extracting PDF text: {e}")
            return ""
    
    def read_text_file(self, file_path: str) -> str:
        """
        Read text from .txt file
        
        Args:
            file_path: Path to text file
        
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            print(f"Error reading text file: {e}")
            return ""
    
    def process_document(self, file_path: str) -> List[Dict]:
        """
        Process a document and split into chunks
        
        Args:
            file_path: Path to document
        
        Returns:
            List of dictionaries containing chunks and metadata
        """
        file_extension = Path(file_path).suffix.lower()
        filename = Path(file_path).name
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
        elif file_extension == '.txt':
            text = self.read_text_file(file_path)
        else:
            print(f"Unsupported file type: {file_extension}")
            return []
        
        if not text:
            return []
        
        # Split into chunks
        chunks = self.text_splitter.split_text(text)
        
        # Create documents with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "content": chunk,
                "metadata": {
                    "source": filename,
                    "chunk_id": i,
                    "total_chunks": len(chunks),
                    "file_path": file_path
                }
            })
        
        return documents
    
    def process_directory(self, directory: str = None) -> List[Dict]:
        """
        Process all documents in a directory
        
        Args:
            directory: Directory path (defaults to Config.DATA_DIR)
        
        Returns:
            List of all processed document chunks
        """
        if directory is None:
            directory = Config.DATA_DIR
        
        all_documents = []
        
        for file_path in Path(directory).glob('**/*'):
            if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.txt']:
                print(f"Processing: {file_path.name}")
                docs = self.process_document(str(file_path))
                all_documents.extend(docs)
        
        print(f"Processed {len(all_documents)} chunks from {directory}")
        return all_documents


# Example usage
# if __name__ == "__main__":
#     processor = DocumentProcessor()
    
#     # Process all documents in the data directory
#     documents = processor.process_directory()
    
#     if documents:
#         print(f"\nSample chunk:")
#         print(documents[0]["content"][:300])
#         print(f"\nMetadata: {documents[0]['metadata']}")