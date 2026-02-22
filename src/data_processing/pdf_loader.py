import pdfplumber
from pathlib import Path
from typing import List, Dict
import argparse


class PDFLoader:
    def __init__(self):
        pass
    
    def load_pdf(self, pdf_path: str) -> Dict:
        """Load and extract text from a single PDF"""
        text_content = []
        metadata = {
            'source': pdf_path,
            'pages': 0
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            metadata['pages'] = len(pdf.pages)
            
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append({
                        'page': page_num,
                        'text': text.strip()
                    })
        
        return {
            'content': text_content,
            'metadata': metadata
        }
    
    def process_pdf_directory(self, input_dir: str, output_dir: str):
        """Process all PDFs in a directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(input_path.glob("*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {input_dir}")
            return
        
        for pdf_file in pdf_files:
            print(f"Processing: {pdf_file.name}")
            
            try:
                result = self.load_pdf(str(pdf_file))
                
                # Save extracted text
                output_file = output_path / f"{pdf_file.stem}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    for page_data in result['content']:
                        f.write(f"=== Page {page_data['page']} ===\n")
                        f.write(page_data['text'])
                        f.write("\n\n")
                
                print(f"✓ Extracted {result['metadata']['pages']} pages to: {output_file}")
                
            except Exception as e:
                print(f"✗ Error processing {pdf_file.name}: {e}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract text from PDF files')
    parser.add_argument('--input', default='./resources', help='Input directory containing PDFs')
    parser.add_argument('--output', default='./data/processed/pdf_text', help='Output directory for extracted text')
    
    args = parser.parse_args()
    
    loader = PDFLoader()
    loader.process_pdf_directory(args.input, args.output)
