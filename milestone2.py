import pandas as pd
from datetime import datetime

class Milestone2Analysis:
    def __init__(self, candidate_data):
        """
        Initializes the analysis module with data for a single candidate.
        :param candidate_data: A dictionary containing all data for one candidate 
                               (personal info, education, experience, etc.).
        """
        self.data = candidate_data
        self.analysis_summary = {}

    def run_all_analyses(self):
        """Runs all analysis modules and returns a consolidated summary."""
        self.analyze_educational_profile()
        self.analyze_professional_experience()
        self.analyze_skill_alignment()
        self.analyze_research_profile_partial()
        self.detect_missing_information()
        self.generate_initial_candidate_summary()
        return self.analysis_summary

    def analyze_educational_profile(self):
        """
        Analyzes the candidate's educational background for consistency, gaps, 
        and institutional quality.
        """
        education_df = pd.DataFrame(self.data.get('education', []))
        if education_df.empty:
            self.analysis_summary['education_analysis'] = "No education data found."
            return

        # Sort by end year to analyze progression
        education_df['passing_year'] = pd.to_numeric(education_df['passing_year'], errors='coerce')
        education_df = education_df.sort_values(by='passing_year').reset_index()

        gaps = []
        for i in range(1, len(education_df)):
            gap = education_df.loc[i, 'passing_year'] - education_df.loc[i-1, 'passing_year']
            if gap > 1:
                gaps.append(f"A {gap}-year gap found between "
                            f"{education_df.loc[i-1, 'degree_name']} and "
                            f"{education_df.loc[i, 'degree_name']}.")

        # Institutional Quality
        ranked_institutions = education_df[education_df['qs_ranking'].notna() | education_df['the_ranking'].notna()]
        
        summary = {
            "educational_gaps": gaps if gaps else "No significant educational gaps detected.",
            "institutional_quality": f"{len(ranked_institutions)} out of {len(education_df)} "
                                     f"degrees are from ranked institutions.",
            "highest_qualification": education_df.iloc[-1]['degree_name'] if not education_df.empty else "N/A"
        }
        self.analysis_summary['education_analysis'] = summary

    def analyze_professional_experience(self):
        """
        Analyzes professional experience for timeline consistency and career progression.
        """
        experience_df = pd.DataFrame(self.data.get('experience', []))
        if experience_df.empty:
            self.analysis_summary['experience_analysis'] = "No professional experience data found."
            return

        # Convert dates and sort
        experience_df['start_date'] = pd.to_datetime(experience_df['start_date'], errors='coerce')
        experience_df['end_date'] = pd.to_datetime(experience_df['end_date'], errors='coerce').fillna(datetime.now())
        experience_df = experience_df.sort_values(by='start_date').reset_index()

        overlaps = []
        gaps = []
        for i in range(1, len(experience_df)):
            # Check for overlap
            if experience_df.loc[i, 'start_date'] < experience_df.loc[i-1, 'end_date']:
                overlaps.append(f"Overlap detected between "
                                f"{experience_df.loc[i-1, 'job_title']} and "
                                f"{experience_df.loc[i, 'job_title']}.")
            # Check for gaps
            gap_days = (experience_df.loc[i, 'start_date'] - experience_df.loc[i-1, 'end_date']).days
            if gap_days > 90: # More than 3 months
                gaps.append(f"A gap of ~{round(gap_days/30)} months found between "
                            f"{experience_df.loc[i-1, 'job_title']} and "
                            f"{experience_df.loc[i, 'job_title']}.")

        progression = "No clear progression pattern identified."
        titles = [str(t).lower() for t in experience_df['job_title'].tolist()]
        if any("senior" in t for t in titles):
            progression = "Progression to senior role detected."
        elif len(titles) > 1:
            progression = "Role transitions detected across the timeline."

        summary = {
            "timeline_overlaps": overlaps if overlaps else "No job overlaps detected.",
            "professional_gaps": gaps if gaps else "No significant professional gaps detected.",
            "career_progression": progression,
            "employment_history_count": len(experience_df)
        }
        self.analysis_summary['experience_analysis'] = summary

    def analyze_research_profile_partial(self):
        """Partial research-profile processing required for milestone demo."""
        outputs = self.data.get('research_outputs', [])
        if not outputs:
            self.analysis_summary['research_profile'] = {
                "status": "No research outputs available.",
                "output_count": 0,
                "recent_publication_year": None
            }
            return

        years = [o.get('year') for o in outputs if o.get('year') is not None]
        self.analysis_summary['research_profile'] = {
            "status": "Partial research profile processed.",
            "output_count": len(outputs),
            "recent_publication_year": max(years) if years else None,
            "sample_titles": [o.get('title', 'Untitled') for o in outputs[:2]]
        }

    def analyze_skill_alignment(self):
        """
        Analyzes alignment between claimed skills and evidence from experience/publications.
        """
        skills = [s['skill_name'].lower() for s in self.data.get('skills', [])]
        if not skills:
            self.analysis_summary['skill_alignment'] = "No skills data found."
            return

        evidence_text = ""
        for exp in self.data.get('experience', []):
            evidence_text += exp.get('job_title', '').lower() + " "
        for pub in self.data.get('research_outputs', []):
            evidence_text += pub.get('title', '').lower() + " "

        aligned_skills = [skill for skill in skills if skill in evidence_text]
        
        summary = {
            "claimed_skills": len(skills),
            "aligned_skills_count": len(aligned_skills),
            "alignment_ratio": f"{(len(aligned_skills) / len(skills) * 100):.2f}%" if skills else "0%",
            "aligned_skills_list": aligned_skills
        }
        self.analysis_summary['skill_alignment'] = summary

    def detect_missing_information(self):
        """
        Detects missing information in the candidate's profile and generates a draft email.
        """
        missing_fields = []
        if not self.data.get('candidates', {}).get('email'):
            missing_fields.append("Candidate Email")
        if not self.data.get('candidates', {}).get('phone_number'):
            missing_fields.append("Candidate Phone Number")
        
        education_df = pd.DataFrame(self.data.get('education', []))
        if not education_df.empty and education_df['grade_value'].isnull().any():
            missing_fields.append("Grade/CGPA for one or more degrees")

        experience_df = pd.DataFrame(self.data.get('experience', []))
        if not experience_df.empty and experience_df['job_description'].isnull().any():
            missing_fields.append("Job description for one or more experience records")

        research_outputs = self.data.get('research_outputs', [])
        for output in research_outputs:
            if not output.get('doi'):
                missing_fields.append("Research DOI for one or more publications")
                break

        if not missing_fields:
            self.analysis_summary['missing_information'] = {"status": "No critical information missing."}
            return

        candidate_name = self.data.get('candidates', {}).get('full_name', 'Candidate')
        email_body = f"Dear {candidate_name},\n\n" \
                     f"Thank you for your interest. We are reviewing your application and noticed " \
                     f"that the following information is missing or incomplete in your CV:\n\n"
        for field in missing_fields:
            email_body += f"- {field}\n"
        email_body += "\nCould you please provide the missing details or upload an updated CV at your earliest convenience?" \
                      "\n\nBest regards,\nHR Team"

        summary = {
            "status": "Missing information detected.",
            "missing_fields": missing_fields,
            "draft_email": email_body
        }
        self.analysis_summary['missing_information'] = summary

    def generate_initial_candidate_summary(self):
        """Generate initial candidate summary for recruiter quick view."""
        candidate = self.data.get('candidates', {})
        education_count = len(self.data.get('education', []))
        experience_count = len(self.data.get('experience', []))
        skills_count = len(self.data.get('skills', []))
        missing = self.analysis_summary.get('missing_information', {})
        missing_count = len(missing.get('missing_fields', [])) if isinstance(missing, dict) else 0

        summary_text = (
            f"{candidate.get('full_name', 'Candidate')} has {education_count} education entries, "
            f"{experience_count} experience roles, and {skills_count} listed skills. "
            f"Missing-information flags: {missing_count}."
        )

        self.analysis_summary['candidate_summary'] = {
            "quick_summary": summary_text,
            "education_entries": education_count,
            "experience_entries": experience_count,
            "skills_entries": skills_count,
            "missing_items": missing_count
        }

if __name__ == '__main__':
    # This is a placeholder for where you would load your candidate data
    # For a real run, you would loop through your candidates from the database
    # and run the analysis on each one.
    
    # Example of how to use the class:
    # candidate_json = load_candidate_from_db(candidate_id) 
    # analyzer = Milestone2Analysis(candidate_json)
    # analysis_results = analyzer.run_all_analyses()
    # print(analysis_results)
    pass
