"""
TALASH - CV Batch Processing Pipeline
Processes CVs from a folder and stores results
"""

import json
import os
import re
import time
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

UNIVERSITY_MAP = {
    'nust': 'National University of Sciences and Technology',
    'lums': 'Lahore University of Management Sciences',
    'giki': 'Ghulam Ishaq Khan Institute',
    'fast': 'National University of Computer and Emerging Sciences',
    'pu': 'University of the Punjab',
    'uet': 'University of Engineering and Technology',
    'qau': 'Quaid-i-Azam University',
    'comsats': 'COMSATS University',
}

SYSTEM_PROMPT = """
You are an expert HR AI for the TALASH academic recruitment system.
Extract CV information into STRICT JSON only.

CRITICAL RULES:
1. grade_metric must be exactly one of: GPA, CGPA, Percentage, Unknown.
2. is_sse_hssc must be true only for Matric/O-Levels/FSc/HSSC/SSC.
3. output_type must be exactly one of: Journal, Conference, Book, Patent, Unknown.
4. degree_level must be exactly one of: BS, MS, PhD, Unknown.
5. supervision status must be exactly one of: Completed, Ongoing, Unknown.
6. skill_category must be exactly one of: Technical, Research, Soft, Tool, Unknown.
7. If unsure about numeric fields, use null.
8. Use empty arrays for missing sections.
9. Return valid JSON only. No markdown and no code fences.

OUTPUT SCHEMA:
{
  "personal_info": {
    "full_name": "string",
    "email": "string",
    "phone_number": "string",
    "research_summary": "string",
    "dob": "string",
    "marital_status": "string",
    "fathers_name": "string"
  },
  "education": [{
    "degree_name": "string",
    "specialization": "string",
    "institution_name": "string",
    "grade_value": null,
    "grade_metric": "Unknown",
    "passing_year": null,
    "is_sse_hssc": false,
    "qs_ranking": null,
    "the_ranking": null
  }],
  "experience": [{
    "job_title": "string",
    "organization": "string",
    "location": "string",
    "start_date": "string",
    "end_date": "string",
    "is_current": false,
    "job_description": "string",
    "industry": "string",
    "duration_months": null
  }],
  "certifications": [{
    "qualification_name": "string",
    "institution_name": "string",
    "passing_year": null
  }],
  "awards": [{
    "award_type": "string",
    "detail": "string"
  }],
  "references": [{
    "reference_name": "string",
    "designation": "string",
    "address": "string",
    "phone": "string",
    "email": "string"
  }],
  "research_outputs": [{
    "title": "string",
    "venue_name": "string",
    "output_type": "Unknown",
    "publication_year": null,
    "impact_factor": null,
    "author_names": "string",
    "research_topics": []
  }],
  "supervision": [{
    "student_name": "string",
    "degree_level": "Unknown",
    "status": "Unknown"
  }],
  "skills": [{
    "skill_name": "string",
    "skill_category": "Unknown"
  }]
}
"""


def extract_float(value):
    if value is None or str(value).strip() == '':
        return None
    match = re.search(r'\d+(\.\d+)?', str(value))
    return float(match.group()) if match else None


def extract_int(value):
    if value is None or str(value).strip() == '':
        return None
    match = re.search(r'\d+', str(value))
    return int(match.group()) if match else None


def clean_string(value):
    if not value:
        return None
    cleaned = str(value).strip()
    if cleaned.lower() in {'null', 'none', 'unknown', 'n/a', ''}:
        return None
    return cleaned


def validate_enum(value, valid_options, default='Unknown'):
    cleaned = clean_string(value)
    if not cleaned:
        return default

    for option in valid_options:
        if cleaned.lower() == option.lower():
            return option
    return default


def normalize_university(raw_name):
    cleaned = clean_string(raw_name)
    if not cleaned:
        return None

    key = cleaned.lower()
    if key in UNIVERSITY_MAP:
        return UNIVERSITY_MAP[key]

    words = set(key.replace('(', ' ').replace(')', ' ').split())
    for short_name, full_name in UNIVERSITY_MAP.items():
        if short_name in words:
            return full_name

    return cleaned.title()


def _as_list(payload, key):
    value = payload.get(key, []) if isinstance(payload, dict) else []
    return value if isinstance(value, list) else []


def _normalize_education(items):
    output = []
    for e in items:
        if not isinstance(e, dict):
            continue
        degree_name = clean_string(e.get('degree_name'))
        institution_name = normalize_university(e.get('institution_name'))
        if not degree_name and not institution_name:
            continue

        output.append({
            'degree_name': degree_name or '',
            'specialization': clean_string(e.get('specialization')) or '',
            'institution_name': institution_name or '',
            'grade_value': extract_float(e.get('grade_value')),
            'grade_metric': validate_enum(e.get('grade_metric'), ['GPA', 'CGPA', 'Percentage'], 'Unknown'),
            'passing_year': extract_int(e.get('passing_year')),
            'is_sse_hssc': bool(e.get('is_sse_hssc')),
            'qs_ranking': extract_int(e.get('qs_ranking')),
            'the_ranking': extract_int(e.get('the_ranking')),
        })
    return output


def _normalize_experience(items):
    output = []
    for ex in items:
        if not isinstance(ex, dict):
            continue

        output.append({
            'job_title': clean_string(ex.get('job_title')) or '',
            'organization': clean_string(ex.get('organization')) or '',
            'location': clean_string(ex.get('location')) or '',
            'start_date': clean_string(ex.get('start_date')) or '',
            'end_date': clean_string(ex.get('end_date')) or '',
            'is_current': bool(ex.get('is_current')),
            'job_description': clean_string(ex.get('job_description')) or '',
            'industry': clean_string(ex.get('industry')) or '',
            'duration_months': extract_int(ex.get('duration_months')),
        })
    return output


def _normalize_research_outputs(items):
    output = []
    for r in items:
        if not isinstance(r, dict):
            continue
        output.append({
            'title': clean_string(r.get('title')) or '',
            'venue_name': clean_string(r.get('venue_name')) or '',
            'output_type': validate_enum(r.get('output_type'), ['Journal', 'Conference', 'Book', 'Patent'], 'Unknown'),
            'publication_year': extract_int(r.get('publication_year')),
            'impact_factor': extract_float(r.get('impact_factor')),
            'author_names': clean_string(r.get('author_names')) or '',
            'research_topics': r.get('research_topics', []) if isinstance(r.get('research_topics'), list) else [],
        })
    return output


def _normalize_supervision(items):
    output = []
    for s in items:
        if not isinstance(s, dict):
            continue
        output.append({
            'student_name': clean_string(s.get('student_name')) or '',
            'degree_level': validate_enum(s.get('degree_level'), ['BS', 'MS', 'PhD'], 'Unknown'),
            'status': validate_enum(s.get('status'), ['Completed', 'Ongoing'], 'Unknown'),
        })
    return output


def _normalize_skills(items):
    output = []
    seen = set()
    for sk in items:
        if not isinstance(sk, dict):
            continue
        skill_name = clean_string(sk.get('skill_name'))
        if not skill_name:
            continue

        key = skill_name.lower()
        if key in seen:
            continue
        seen.add(key)

        output.append({
            'skill_name': skill_name,
            'skill_category': validate_enum(sk.get('skill_category'), ['Technical', 'Research', 'Soft', 'Tool'], 'Unknown'),
        })
    return output


def _normalize_certifications(items):
    output = []
    for c in items:
        if not isinstance(c, dict):
            continue
        qualification_name = clean_string(c.get('qualification_name'))
        if not qualification_name:
            continue
        output.append({
            'qualification_name': qualification_name,
            'institution_name': clean_string(c.get('institution_name')) or '',
            'passing_year': extract_int(c.get('passing_year')),
        })
    return output


def _normalize_awards(items):
    output = []
    for a in items:
        if not isinstance(a, dict):
            continue
        detail = clean_string(a.get('detail'))
        if not detail and not clean_string(a.get('award_type')):
            continue
        output.append({
            'award_type': clean_string(a.get('award_type')) or '',
            'detail': detail or '',
        })
    return output


def _normalize_references(items):
    output = []
    for r in items:
        if not isinstance(r, dict):
            continue
        output.append({
            'reference_name': clean_string(r.get('reference_name')) or '',
            'designation': clean_string(r.get('designation')) or '',
            'address': clean_string(r.get('address')) or '',
            'phone': clean_string(r.get('phone')) or '',
            'email': clean_string(r.get('email')) or '',
        })
    return output


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

    name = clean_string(payload.get('name')) or clean_string(personal_info.get('full_name')) or fallback_name
    email = clean_string(payload.get('email')) or clean_string(personal_info.get('email')) or ''
    phone = clean_string(payload.get('phone_number')) or clean_string(personal_info.get('phone_number')) or ''

    return {
        'name': name,
        'email': email,
        'phone_number': phone,
        'research_summary': clean_string(personal_info.get('research_summary')) or '',
        'dob': clean_string(personal_info.get('dob')) or '',
        'marital_status': clean_string(personal_info.get('marital_status')) or '',
        'fathers_name': clean_string(personal_info.get('fathers_name')) or '',
        'education': _normalize_education(_as_list(payload, 'education')),
        'experience': _normalize_experience(_as_list(payload, 'experience')),
        'skills': _normalize_skills(_as_list(payload, 'skills')),
        'research_outputs': _normalize_research_outputs(_as_list(payload, 'research_outputs')),
        'certifications': _normalize_certifications(_as_list(payload, 'certifications')),
        'awards': _normalize_awards(_as_list(payload, 'awards')),
        'references': _normalize_references(_as_list(payload, 'references') or _as_list(payload, 'references_table')),
        'supervision': _normalize_supervision(_as_list(payload, 'supervision')),
        'extraction_method': payload.get('extraction_method', 'gemini' if payload.get('gemini_used') else 'rule-based')
    }


def _candidate_text_chunk(raw_text):
    """Mirror notebook behavior for noisy PDFs while still supporting single-CV files."""
    text = (raw_text or '').replace('\x00', ' ')
    text = re.sub(r'\s+', ' ', text).strip()

    raw_chunks = re.split(r'(?i)candidate for the post of', text)
    chunks = ['Candidate for the post of ' + c.strip() for c in raw_chunks if len(c.strip()) > 500]
    if chunks:
        return chunks[0][:10000]

    return text[:10000]


def _extract_with_gemini(raw_text, fallback_name):
    """Use Gemini to convert CV text into structured JSON."""
    if not _configure_gemini():
        return None

    cv_chunk = _candidate_text_chunk(raw_text)
    prompt = f"{SYSTEM_PROMPT}\n\nPreferred candidate name: {fallback_name}\n\nCV TEXT:\n{cv_chunk}"

    model = genai.GenerativeModel(GEMINI_MODEL_NAME)
    max_attempts = 4
    for attempt in range(max_attempts):
        try:
            response = model.generate_content(
                prompt,
                generation_config={'response_mime_type': 'application/json'}
            )
            response_text = getattr(response, 'text', '') or ''
            if not response_text and getattr(response, 'candidates', None):
                response_text = str(response.candidates[0])

            parsed = _parse_json_payload(response_text)
            if isinstance(parsed, dict):
                parsed['gemini_used'] = True
                return _normalize_structured_extraction(parsed, fallback_name)
        except json.JSONDecodeError:
            time.sleep(2 + attempt)
            continue
        except Exception:
            # Retry transient API/model issues with a small backoff.
            time.sleep(2 + attempt)
            continue

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
    seen = set()
    lower_text = text.lower()
    for token in skill_tokens:
        if token in lower_text:
            normalized = token.title()
            if normalized.lower() not in seen:
                found_skills.append({'skill_name': normalized, 'skill_category': 'Technical'})
                seen.add(normalized.lower())

    return {
        'name': fallback_name,
        'email': email_match.group(0) if email_match else '',
        'phone_number': phone_match.group(0).strip() if phone_match else '',
        'skills': found_skills,
        'education': [],
        'experience': [],
        'research_outputs': [],
        'certifications': [],
        'awards': [],
        'references': [],
        'supervision': [],
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
