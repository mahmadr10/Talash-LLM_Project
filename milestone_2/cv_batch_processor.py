"""
TALASH - CV Batch Processing Pipeline
Processes CVs from a folder and stores results
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

import pdfplumber

try:
    import google.generativeai as genai
except ImportError:
    genai = None


GEMINI_MODEL_NAME = os.getenv('GEMINI_MODEL_NAME', 'gemini-1.5-flash')
GEMINI_ENABLED = os.getenv('TALASH_DISABLE_GEMINI', '').strip().lower() not in {'1', 'true', 'yes'}
_GEMINI_CONFIGURED = False


def _configure_gemini():
    """Configure Gemini once if the package and API key are available."""
    global _GEMINI_CONFIGURED

    if not GEMINI_ENABLED or genai is None:
        return False

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        return False

    if not _GEMINI_CONFIGURED:
        genai.configure(api_key=api_key)
        _GEMINI_CONFIGURED = True

    return True


def _parse_json_payload(raw_text):
    """Extract JSON from a Gemini response that may contain code fences or extra text."""
    cleaned = (raw_text or '').strip()

    if cleaned.startswith('```'):
        cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\s*```$', '', cleaned)

    start = cleaned.find('{')
    end = cleaned.rfind('}')
    if start != -1 and end != -1 and end > start:
        cleaned = cleaned[start:end + 1]

    return json.loads(cleaned)


def _normalize_structured_extraction(payload, fallback_name):
    """Fill the schema expected by the Milestone 2 app."""
    payload = payload if isinstance(payload, dict) else {}
    personal_info = payload.get('personal_info', {}) if isinstance(payload.get('personal_info', {}), dict) else {}

    return {
        'name': payload.get('name') or personal_info.get('full_name') or fallback_name,
        'email': payload.get('email') or personal_info.get('email') or '',
        'phone_number': payload.get('phone_number') or personal_info.get('phone_number') or '',
        'research_summary': personal_info.get('research_summary', ''),
        'dob': personal_info.get('dob', ''),
        'marital_status': personal_info.get('marital_status', ''),
        'fathers_name': personal_info.get('fathers_name', ''),
        'education': payload.get('education') or [],
        'experience': payload.get('experience') or [],
        'skills': payload.get('skills') or [],
        'research_outputs': payload.get('research_outputs') or [],
        'certifications': payload.get('certifications') or [],
        'awards': payload.get('awards') or [],
        'references': payload.get('references') or payload.get('references_table') or [],
        'supervision': payload.get('supervision') or [],
        'extraction_method': payload.get('extraction_method', 'gemini' if payload.get('gemini_used') else 'rule-based')
    }


def _extract_with_gemini(raw_text, fallback_name):
    """Use Gemini to convert CV text into structured JSON."""
    if not _configure_gemini():
        return None

    prompt = f"""
You are an extraction engine for TALASH, a smart HR recruitment system.
Convert the CV text into STRICT JSON only.

Output schema:
{{
  "personal_info": {{
    "full_name": "string",
    "email": "string",
    "phone_number": "string",
    "research_summary": "string",
    "dob": "string",
    "marital_status": "string",
    "fathers_name": "string"
  }},
  "education": [{{
    "degree_name": "string",
    "specialization": "string",
    "institution_name": "string",
    "grade_value": 0,
    "grade_metric": "string",
    "passing_year": 0,
    "is_sse_hssc": false,
    "qs_ranking": 0,
    "the_ranking": 0
  }}],
  "experience": [{{
    "job_title": "string",
    "organization": "string",
    "location": "string",
    "start_date": "string",
    "end_date": "string",
    "is_current": false,
    "job_description": "string",
    "industry": "string",
    "duration_months": 0
  }}],
  "certifications": [{{
    "qualification_name": "string",
    "institution_name": "string",
    "passing_year": 0
  }}],
  "awards": [{{
    "award_type": "string",
    "detail": "string"
  }}],
  "references": [{{
    "reference_name": "string",
    "designation": "string",
    "address": "string",
    "phone": "string",
    "email": "string"
  }}],
  "research_outputs": [{{
    "title": "string",
    "venue_name": "string",
    "output_type": "Journal",
    "publication_year": 0,
    "impact_factor": 0,
    "author_names": "string",
    "research_topics": []
  }}],
  "supervision": [{{
    "student_name": "string",
    "degree_level": "BS",
    "status": "Completed"
  }}],
  "skills": [{{
    "skill_name": "string",
    "skill_category": "Technical"
  }}]
}}

Rules:
- Return JSON only.
- Use empty arrays for unknown sections.
- If a field is missing, use an empty string or null-like empty value.
- Prefer the candidate name: {fallback_name}

CV TEXT:
{(raw_text or '')[:12000]}
"""

    try:
        model = genai.GenerativeModel(GEMINI_MODEL_NAME)
        response = model.generate_content(prompt)
        response_text = getattr(response, 'text', '') or ''
        if not response_text and getattr(response, 'candidates', None):
            response_text = str(response.candidates[0])

        parsed = _parse_json_payload(response_text)
        if isinstance(parsed, dict):
            parsed['gemini_used'] = True
            return _normalize_structured_extraction(parsed, fallback_name)
    except Exception:
        return None

    return None


def parse_cv_text_to_structured(raw_text, fallback_name):
    """Parse CV text into structured data using Gemini first, then fallback rules."""
    gemini_result = _extract_with_gemini(raw_text, fallback_name)
    if gemini_result is not None:
        return gemini_result

    text = raw_text or ''
    email_match = re.search(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)
    phone_match = re.search(r'(\+?\d[\d\s\-]{8,}\d)', text)

    skill_tokens = [
        'python', 'sql', 'aws', 'docker', 'machine learning', 'research', 'statistics',
        'tableau', 'r', 'data analysis', 'system design', 'flask', 'django'
    ]
    found_skills = []
    lower_text = text.lower()
    for token in skill_tokens:
        if token in lower_text:
            found_skills.append({'skill_name': token.title()})

    return {
        'name': fallback_name,
        'email': email_match.group(0) if email_match else '',
        'phone_number': phone_match.group(0).strip() if phone_match else '',
        'skills': found_skills,
        'education': [],
        'experience': [],
        'research_outputs': [],
        'extraction_method': 'rule-based'
    }


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
            text = ''
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    text += (page.extract_text() or '') + '\n'
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
            structured = parse_cv_text_to_structured(extracted_text, filepath.stem)

            result = {
                'filename': filepath.name,
                'extraction_date': datetime.now().isoformat(),
                'raw_text': extracted_text[:1000],
                'status': 'extracted',
                'structured_extraction': structured
            }

            self.results.append(result)
            print('  ✓ Extracted successfully')
            return result

        except Exception as e:
            print(f'  ✗ Error: {str(e)}')
            return None

    def save_results(self, filename='cv_extraction_results.json'):
        """Save extraction results"""
        output_path = os.path.join(self.output_folder, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
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
            'success_rate': f"{(successful / total * 100):.1f}%" if total > 0 else '0%'
        }

        print('\n' + '=' * 50)
        print('PROCESSING REPORT')
        print('=' * 50)
        print(f"Total CVs: {report['total_files']}")
        print(f"Successful: {report['successful']}")
        print(f"Failed: {report['failed']}")
        print(f"Success Rate: {report['success_rate']}")
        print('=' * 50)

        return report


if __name__ == '__main__':
    processor = CVBatchProcessor('uploads', 'outputs')
    processor.process_folder()
    processor.save_results()
    report = processor.generate_report()
