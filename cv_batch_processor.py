"""
TALASH - CV Batch Processing Pipeline
Processes CVs from a folder and stores results
"""

import os
import json
from pathlib import Path
import pdfplumber
from datetime import datetime
import pandas as pd

class CVBatchProcessor:
    """Process multiple CVs from a folder"""
    
    def __init__(self, input_folder='uploads', output_folder='outputs'):
        self.input_folder = input_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        self.results = []
    
    def extract_text_from_pdf(self, filepath):
        """Extract text from PDF"""
        try:
            text = ""
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
            return f"Error extracting PDF: {str(e)}"
    
    def process_folder(self):
        """Process all PDFs in input folder"""
        pdf_files = list(Path(self.input_folder).glob('*.pdf'))
        print(f"Found {len(pdf_files)} PDF files to process")
        
        for pdf_file in pdf_files:
            print(f"\nProcessing: {pdf_file.name}")
            self.process_single_cv(pdf_file)
        
        return self.results
    
    def process_single_cv(self, filepath):
        """Process a single CV file"""
        try:
            extracted_text = self.extract_text_from_pdf(str(filepath))
            
            # In production, would use Google Gemini LLM here for structured extraction
            # For now, save raw extraction
            result = {
                'filename': filepath.name,
                'extraction_date': datetime.now().isoformat(),
                'raw_text': extracted_text[:1000],  # First 1000 chars
                'status': 'extracted'
                # Gemini would fill in:
                # 'name': '...',
                # 'education': [...],
                # 'experience': [...],
                # 'skills': [...],
                # 'contact_info': {...}
            }
            
            self.results.append(result)
            print(f"  ✓ Extracted successfully")
            return result
            
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            return None
    
    def save_results(self, filename='cv_extraction_results.json'):
        """Save extraction results"""
        output_path = os.path.join(self.output_folder, filename)
        with open(output_path, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\nResults saved to: {output_path}")
        return output_path
    
    def generate_report(self):
        """Generate processing report"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.get('status') == 'extracted')
        
        report = {
            'processing_date': datetime.now().isoformat(),
            'total_files': total,
            'successful': successful,
            'failed': total - successful,
            'success_rate': f"{(successful/total*100):.1f}%" if total > 0 else "0%"
        }
        
        print("\n" + "="*50)
        print("PROCESSING REPORT")
        print("="*50)
        print(f"Total CVs: {report['total_files']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {report['success_rate']}")
        print("="*50)
        
        return report

if __name__ == '__main__':
    processor = CVBatchProcessor('uploads', 'outputs')
    processor.process_folder()
    processor.save_results()
    report = processor.generate_report()
