"""
Sample Data Generator for TALASH Milestone 2 Testing
Creates representative sample CV extraction outputs for demonstration
"""

import json
from datetime import datetime

class SampleCVGenerator:
    """Generate sample candidate data for testing"""
    
    @staticmethod
    def generate_ahmed_khan():
        """Sample candidate 1: Ahmed Khan"""
        return {
            'candidates': {
                'id': 1,
                'full_name': 'Ahmed Khan',
                'email': 'ahmed.khan@example.com',
                'phone_number': '+92-300-1234567',
                'date_of_birth': '1996-05-15',
                'nationality': 'Pakistani'
            },
            'education': [
                {
                    'degree_name': 'BS Computer Science',
                    'institution': 'National University of Science & Technology (NUST)',
                    'city': 'Islamabad',
                    'country': 'Pakistan',
                    'passing_year': 2018,
                    'grade_value': 3.8,
                    'qs_ranking': 200,
                    'the_ranking': None
                },
                {
                    'degree_name': 'MS Computer Science',
                    'institution': 'Massachusetts Institute of Technology (MIT)',
                    'city': 'Boston',
                    'country': 'USA',
                    'passing_year': 2020,
                    'grade_value': 3.9,
                    'qs_ranking': 1,
                    'the_ranking': 2
                }
            ],
            'experience': [
                {
                    'job_title': 'Junior Software Engineer',
                    'company': 'TechCorp Pakistan',
                    'industry': 'Information Technology',
                    'job_description': 'Developed web applications using Python and Django',
                    'start_date': '2020-06-01',
                    'end_date': '2021-12-31',
                    'duration_months': 18,
                    'location': 'Karachi, Pakistan'
                },
                {
                    'job_title': 'Senior Systems Engineer',
                    'company': 'CloudSystems Inc',
                    'industry': 'Cloud Computing',
                    'job_description': 'Architected and maintained cloud infrastructure; led team of 5 engineers',
                    'start_date': '2022-01-15',
                    'end_date': None,
                    'duration_months': 24,
                    'location': 'San Francisco, USA'
                }
            ],
            'skills': [
                {'skill_name': 'Python', 'proficiency': 'Expert'},
                {'skill_name': 'SQL', 'proficiency': 'Advanced'},
                {'skill_name': 'AWS', 'proficiency': 'Advanced'},
                {'skill_name': 'Docker', 'proficiency': 'Intermediate'},
                {'skill_name': 'Research', 'proficiency': 'Advanced'},
                {'skill_name': 'Machine Learning', 'proficiency': 'Intermediate'},
                {'skill_name': 'System Design', 'proficiency': 'Expert'}
            ],
            'certifications': [
                {'name': 'AWS Solutions Architect', 'issuer': 'Amazon', 'year': 2021},
                {'name': 'Google Cloud Professional', 'issuer': 'Google', 'year': 2022}
            ],
            'research_outputs': [
                {
                    'title': 'Machine Learning in Cloud Systems: A Comprehensive Study',
                    'authors': 'Ahmed Khan, Dr. Smith',
                    'publication': 'IEEE Transactions on Cloud Computing',
                    'year': 2021,
                    'doi': '10.1109/TCC.2021.12345'
                },
                {
                    'title': 'Scalability Patterns for Distributed Systems',
                    'authors': 'Ahmed Khan, Dr. Johnson, Prof. Williams',
                    'publication': 'ACM Computing Surveys',
                    'year': 2022,
                    'doi': '10.1145/3523265'
                }
            ],
            'supervision': [
                {'role': 'Mentor', 'mentees': 3, 'focus_area': 'Cloud Architecture', 'duration': '2 years'}
            ]
        }
    
    @staticmethod
    def generate_fatima_zahra():
        """Sample candidate 2: Fatima Zahra"""
        return {
            'candidates': {
                'id': 2,
                'full_name': 'Fatima Zahra',
                'email': 'fatima.z@example.com',
                'phone_number': '+92-300-2345678',
                'date_of_birth': '1997-08-22',
                'nationality': 'Pakistani'
            },
            'education': [
                {
                    'degree_name': 'BS Mathematics',
                    'institution': 'University of the Punjab',
                    'city': 'Lahore',
                    'country': 'Pakistan',
                    'passing_year': 2019,
                    'grade_value': 3.7,
                    'qs_ranking': 500,
                    'the_ranking': None
                },
                {
                    'degree_name': 'MS Data Science',
                    'institution': 'Imperial College London',
                    'city': 'London',
                    'country': 'UK',
                    'passing_year': 2021,
                    'grade_value': 3.85,
                    'qs_ranking': 3,
                    'the_ranking': 11
                }
            ],
            'experience': [
                {
                    'job_title': 'Data Analyst',
                    'company': 'DataInsights Pakistan',
                    'industry': 'Business Analytics',
                    'job_description': 'Analyzed business metrics and provided data-driven insights',
                    'start_date': '2019-08-01',
                    'end_date': '2021-06-30',
                    'duration_months': 22,
                    'location': 'Karachi, Pakistan'
                },
                {
                    'job_title': 'Senior Data Scientist',
                    'company': 'FinTech Solutions UK',
                    'industry': 'Financial Technology',
                    'job_description': 'Built predictive models for credit risk assessment and fraud detection',
                    'start_date': '2021-08-15',
                    'end_date': None,
                    'duration_months': 16,
                    'location': 'London, UK'
                }
            ],
            'skills': [
                {'skill_name': 'Python', 'proficiency': 'Expert'},
                {'skill_name': 'SQL', 'proficiency': 'Expert'},
                {'skill_name': 'R', 'proficiency': 'Advanced'},
                {'skill_name': 'Tableau', 'proficiency': 'Advanced'},
                {'skill_name': 'Machine Learning', 'proficiency': 'Expert'},
                {'skill_name': 'Statistics', 'proficiency': 'Expert'},
                {'skill_name': 'Analytics', 'proficiency': 'Expert'}
            ],
            'certifications': [
                {'name': 'Google Analytics Professional', 'issuer': 'Google', 'year': 2020},
                {'name': 'Microsoft Data Science', 'issuer': 'Microsoft', 'year': 2021}
            ],
            'research_outputs': [
                {
                    'title': 'Predictive Analytics for Financial Risk Assessment',
                    'authors': 'Fatima Zahra, Prof. Anderson',
                    'publication': 'Journal of Financial Analytics',
                    'year': 2021,
                    'doi': '10.1016/j.jfa.2021.05.003'
                }
            ],
            'supervision': []
        }
    
    @staticmethod
    def generate_muhammad_ali():
        """Sample candidate 3: Muhammad Ali"""
        return {
            'candidates': {
                'id': 3,
                'full_name': 'Muhammad Ali',
                'email': 'muhammad.ali@example.com',
                'phone_number': '+92-300-3456789',
                'date_of_birth': '1995-03-10',
                'nationality': 'Pakistani'
            },
            'education': [
                {
                    'degree_name': 'BS Electronics Engineering',
                    'institution': 'Ghulam Ishaq Khan Institute',
                    'city': 'Topi',
                    'country': 'Pakistan',
                    'passing_year': 2017,
                    'grade_value': 3.6,
                    'qs_ranking': None,
                    'the_ranking': None
                }
            ],
            'experience': [
                {
                    'job_title': 'Hardware Engineer',
                    'company': 'embedded Systems Ltd',
                    'industry': 'Electronics',
                    'job_description': 'Designed and tested embedded systems for IoT applications',
                    'start_date': '2017-07-01',
                    'end_date': '2019-12-31',
                    'duration_months': 30,
                    'location': 'Islamabad, Pakistan'
                },
                {
                    'job_title': 'IoT Solutions Architect',
                    'company': 'SmartTech Solutions',
                    'industry': 'Internet of Things',
                    'job_description': 'Led IoT product development for smart home applications',
                    'start_date': '2020-01-15',
                    'end_date': None,
                    'duration_months': 48,
                    'location': 'Dubai, UAE'
                }
            ],
            'skills': [
                {'skill_name': 'Embedded Systems', 'proficiency': 'Expert'},
                {'skill_name': 'C/C++', 'proficiency': 'Advanced'},
                {'skill_name': 'IoT', 'proficiency': 'Expert'},
                {'skill_name': 'FPGA', 'proficiency': 'Intermediate'},
                {'skill_name': 'Python', 'proficiency': 'Intermediate'}
            ],
            'certifications': [],
            'research_outputs': [],
            'supervision': []
        }
    
    @staticmethod
    def generate_aisha_bibi():
        """Sample candidate 4: Aisha Bibi"""
        return {
            'candidates': {
                'id': 4,
                'full_name': 'Aisha Bibi',
                'email': None,  # Missing email
                'phone_number': '+92-321-9876543',
                'date_of_birth': '1998-11-05',
                'nationality': 'Pakistani'
            },
            'education': [
                {
                    'degree_name': 'BS Computer Science',
                    'institution': 'Bahria University',
                    'city': 'Rawalpindi',
                    'country': 'Pakistan',
                    'passing_year': 2020,
                    'grade_value': 3.65,
                    'qs_ranking': None,
                    'the_ranking': None
                }
            ],
            'experience': [
                {
                    'job_title': 'Junior Developer',
                    'company': 'WebDev Startups',
                    'industry': 'Software Development',
                    'job_description': 'Developed web applications using React and Node.js',
                    'start_date': '2020-06-01',
                    'end_date': None,
                    'duration_months': 42,
                    'location': 'Karachi, Pakistan'
                }
            ],
            'skills': [
                {'skill_name': 'JavaScript', 'proficiency': 'Advanced'},
                {'skill_name': 'React', 'proficiency': 'Advanced'},
                {'skill_name': 'Node.js', 'proficiency': 'Intermediate'},
                {'skill_name': 'SQL', 'proficiency': 'Intermediate'}
            ],
            'certifications': [],
            'research_outputs': [],
            'supervision': []
        }
    
    @staticmethod
    def save_all_samples(output_file='sample_cv_data.json'):
        """Save all sample candidates to JSON file"""
        samples = {
            'extraction_metadata': {
                'generated_date': datetime.now().isoformat(),
                'total_candidates': 4,
                'extraction_method': 'Manual structured data for testing',
                'note': 'These are representative samples for Milestone 2 demonstration'
            },
            'candidates': [
                SampleCVGenerator.generate_ahmed_khan(),
                SampleCVGenerator.generate_fatima_zahra(),
                SampleCVGenerator.generate_muhammad_ali(),
                SampleCVGenerator.generate_aisha_bibi()
            ]
        }
        
        with open(output_file, 'w') as f:
            json.dump(samples, f, indent=2)
        
        print(f"✓ Sample data saved to {output_file}")
        return output_file

if __name__ == '__main__':
    SampleCVGenerator.save_all_samples()
