"""
Certificate Verification Service for KIU Admission Portal

This service provides automated verification of uploaded certificates
against UNEB standards and NCHE requirements.
"""

import os
import re
import json
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
import logging

log = logging.getLogger(__name__)

class CertificateVerificationService:
    """
    Advanced certificate verification system for UNEB certificates
    Supports both old and new curriculum grading systems
    """
    
    def __init__(self):
        # UNEB certificate patterns
        self.uce_certificate_patterns = {
            'index_number': r'^U\d{4}/\d{3}$',
            'school_number': r'^\d{4}/\d{3}$',
            'candidate_number': r'^\d{8}$',
        }
        
        self.uace_certificate_patterns = {
            'index_number': r'^A\d{4}/\d{3}$',
            'school_number': r'^\d{4}/\d{3}$',
            'candidate_number': r'^\d{8}$',
        }
        
        # Grade validation patterns
        self.uce_old_grades = ['D1', 'D2', 'C3', 'C4', 'C5', 'C6', 'P7', 'P8', 'F9']
        self.uce_new_grades = ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7', 'D8', 'F']
        self.uace_grades = ['A', 'B', 'C', 'D', 'E', 'O', 'F']
        
        # Subject lists for validation
        self.valid_uce_subjects = [
            'English Language', 'Mathematics', 'Physics', 'Chemistry', 'Biology',
            'Geography', 'History', 'Christian Religious Education (CRE)',
            'Islamic Religious Education (IRE)', 'Fine Art', 'Music',
            'Entrepreneurship Education', 'Computer Studies', 'Agriculture',
            'Home Economics', 'Commerce', 'French', 'Kiswahili',
            'Literature in English', 'Technical Drawing', 'Physical Education',
            'Additional Mathematics',
        ]
        
        self.valid_uace_principal_subjects = [
            'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Geography',
            'History', 'Literature in English', 'Economics',
            'Entrepreneurship Education', 'Art & Design', 'Technical Drawing',
            'Christian Religious Education (CRE)', 'Islamic Religious Education (IRE)',
            'Divinity', 'Fine Art', 'Music',
        ]
        
        self.valid_uace_subsidiary_subjects = [
            'General Paper', 'Subsidiary ICT', 'Subsidiary Mathematics',
        ]
    
    def verify_uce_certificate(self, certificate_data: Dict) -> Dict:
        """
        Verify UCE certificate against UNEB standards
        
        Args:
            certificate_data: Dictionary containing certificate information
            
        Returns:
            Verification result with status and details
        """
        result = {
            'certificate_type': 'UCE',
            'verification_status': 'pending',
            'verification_score': 0,
            'checks_passed': 0,
            'total_checks': 0,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'verified_at': datetime.utcnow().isoformat(),
        }
        
        # Check index number format
        if 'index_number' in certificate_data:
            result['total_checks'] += 1
            index_num = certificate_data['index_number']
            if re.match(self.uce_certificate_patterns['index_number'], index_num):
                result['checks_passed'] += 1
            else:
                result['errors'].append(f'Invalid UCE index number format: {index_num}')
        
        # Check examination year
        if 'examination_year' in certificate_data:
            result['total_checks'] += 1
            year = certificate_data['examination_year']
            current_year = datetime.now().year
            if isinstance(year, int) and 1990 <= year <= current_year - 1:
                result['checks_passed'] += 1
            else:
                result['errors'].append(f'Invalid examination year: {year}')
        
        # Check grades
        if 'grades' in certificate_data:
            grades = certificate_data['grades']
            if isinstance(grades, list) and len(grades) >= 5:
                result['total_checks'] += 1
                valid_grades_count = 0
                
                for grade_entry in grades:
                    if isinstance(grade_entry, dict):
                        subject = grade_entry.get('subject', '')
                        grade = grade_entry.get('grade', '')
                        
                        # Validate subject
                        if subject in self.valid_uce_subjects:
                            valid_grades_count += 1
                        
                        # Validate grade based on curriculum
                        curriculum = certificate_data.get('curriculum', 'new')
                        if curriculum == 'old':
                            if grade in self.uce_old_grades:
                                valid_grades_count += 1
                            else:
                                result['warnings'].append(f'Invalid grade for old curriculum: {grade} in {subject}')
                        else:
                            if grade in self.uce_new_grades:
                                valid_grades_count += 1
                            else:
                                result['warnings'].append(f'Invalid grade for new curriculum: {grade} in {subject}')
                
                if valid_grades_count == len(grades) * 2:  # subject + grade check
                    result['checks_passed'] += 1
                else:
                    result['errors'].append('Some subjects or grades are invalid')
            else:
                result['errors'].append('UCE certificate must have at least 5 subjects')
        
        # Check school name
        if 'school_name' in certificate_data:
            result['total_checks'] += 1
            school = certificate_data['school_name']
            if isinstance(school, str) and len(school.strip()) >= 3:
                result['checks_passed'] += 1
            else:
                result['errors'].append('Invalid school name')
        
        # Calculate verification score
        if result['total_checks'] > 0:
            result['verification_score'] = (result['checks_passed'] / result['total_checks']) * 100
        
        # Determine overall status
        if result['verification_score'] >= 90:
            result['verification_status'] = 'verified'
        elif result['verification_score'] >= 70:
            result['verification_status'] = 'provisionally_verified'
        elif result['verification_score'] >= 50:
            result['verification_status'] = 'needs_review'
        else:
            result['verification_status'] = 'failed'
        
        # Add recommendations
        if result['verification_status'] in ['needs_review', 'failed']:
            result['recommendations'].extend([
                'Ensure certificate is clearly scanned',
                'Check that all text is readable',
                'Verify index number matches UNEB records',
                'Confirm examination year is correct',
            ])
        
        return result
    
    def verify_uace_certificate(self, certificate_data: Dict) -> Dict:
        """
        Verify UACE certificate against UNEB standards
        
        Args:
            certificate_data: Dictionary containing certificate information
            
        Returns:
            Verification result with status and details
        """
        result = {
            'certificate_type': 'UACE',
            'verification_status': 'pending',
            'verification_score': 0,
            'checks_passed': 0,
            'total_checks': 0,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'verified_at': datetime.utcnow().isoformat(),
        }
        
        # Check index number format
        if 'index_number' in certificate_data:
            result['total_checks'] += 1
            index_num = certificate_data['index_number']
            if re.match(self.uace_certificate_patterns['index_number'], index_num):
                result['checks_passed'] += 1
            else:
                result['errors'].append(f'Invalid UACE index number format: {index_num}')
        
        # Check examination year
        if 'examination_year' in certificate_data:
            result['total_checks'] += 1
            year = certificate_data['examination_year']
            current_year = datetime.now().year
            if isinstance(year, int) and 1990 <= year <= current_year:
                result['checks_passed'] += 1
            else:
                result['errors'].append(f'Invalid examination year: {year}')
        
        # Check grades and subjects
        if 'grades' in certificate_data:
            grades = certificate_data['grades']
            principal_count = 0
            subsidiary_count = 0
            valid_entries = 0
            
            result['total_checks'] += 1
            for grade_entry in grades:
                if isinstance(grade_entry, dict):
                    subject = grade_entry.get('subject', '')
                    grade = grade_entry.get('grade', '')
                    subject_type = grade_entry.get('subject_type', '')
                    
                    # Validate grade
                    if grade in self.uace_grades:
                        valid_entries += 1
                    
                    # Validate subject based on type
                    if subject_type.lower() == 'principal':
                        principal_count += 1
                        if subject in self.valid_uace_principal_subjects:
                            valid_entries += 1
                    elif subject_type.lower() == 'subsidiary':
                        subsidiary_count += 1
                        if subject in self.valid_uace_subsidiary_subjects:
                            valid_entries += 1
                    else:
                        result['warnings'].append(f'Invalid subject type: {subject_type}')
            
            # Check minimum requirements
            if principal_count >= 2 and subsidiary_count >= 1:
                result['checks_passed'] += 1
            else:
                result['errors'].append(f'UACE requires at least 2 principal subjects and 1 subsidiary (found: {principal_count} principal, {subsidiary_count} subsidiary)')
            
            if valid_entries == len(grades) * 2:  # subject + grade validation
                result['checks_passed'] += 1
            else:
                result['warnings'].append('Some subjects or grades may be invalid')
        
        # Calculate total points for eligibility
        if 'grades' in certificate_data:
            grades = certificate_data['grades']
            total_points = 0
            grade_points = {'A': 6, 'B': 5, 'C': 4, 'D': 3, 'E': 2, 'O': 1, 'F': 0}
            
            for grade_entry in grades:
                if isinstance(grade_entry, dict):
                    grade = grade_entry.get('grade', '')
                    subject_type = grade_entry.get('subject_type', '')
                    
                    if subject_type.lower() == 'principal' and grade in grade_points:
                        total_points += grade_points[grade]
            
            result['calculated_points'] = total_points
            result['principal_points'] = total_points
            
            # Add point-based recommendations
            if total_points >= 15:
                result['recommendations'].append('Excellent point total - eligible for competitive programs')
            elif total_points >= 10:
                result['recommendations'].append('Good point total - eligible for most programs')
            elif total_points >= 6:
                result['recommendations'].append('Minimum point total for university entry')
            else:
                result['recommendations'].append('Low point total - may limit program options')
        
        # Calculate verification score
        if result['total_checks'] > 0:
            result['verification_score'] = (result['checks_passed'] / result['total_checks']) * 100
        
        # Determine overall status
        if result['verification_score'] >= 90:
            result['verification_status'] = 'verified'
        elif result['verification_score'] >= 70:
            result['verification_status'] = 'provisionally_verified'
        elif result['verification_score'] >= 50:
            result['verification_status'] = 'needs_review'
        else:
            result['verification_status'] = 'failed'
        
        # Add recommendations
        if result['verification_status'] in ['needs_review', 'failed']:
            result['recommendations'].extend([
                'Ensure certificate is clearly scanned',
                'Verify principal subjects are clearly marked',
                'Check that General Paper is included',
                'Confirm grading is legible',
            ])
        
        return result
    
    def verify_diploma_certificate(self, certificate_data: Dict) -> Dict:
        """
        Verify Diploma certificate against NCHE standards
        
        Args:
            certificate_data: Dictionary containing certificate information
            
        Returns:
            Verification result with status and details
        """
        result = {
            'certificate_type': 'Diploma',
            'verification_status': 'pending',
            'verification_score': 0,
            'checks_passed': 0,
            'total_checks': 0,
            'errors': [],
            'warnings': [],
            'recommendations': [],
            'verified_at': datetime.utcnow().isoformat(),
        }
        
        # Check institution name
        if 'institution_name' in certificate_data:
            result['total_checks'] += 1
            institution = certificate_data['institution_name']
            if isinstance(institution, str) and len(institution.strip()) >= 3:
                result['checks_passed'] += 1
            else:
                result['errors'].append('Invalid institution name')
        
        # Check award date
        if 'award_date' in certificate_data:
            result['total_checks'] += 1
            award_date = certificate_data['award_date']
            try:
                if isinstance(award_date, str):
                    parsed_date = datetime.strptime(award_date, '%Y-%m-%d').date()
                    current_year = datetime.now().year
                    if 1990 <= parsed_date.year <= current_year:
                        result['checks_passed'] += 1
                    else:
                        result['errors'].append(f'Invalid award date: {award_date}')
                elif isinstance(award_date, date):
                    current_year = datetime.now().year
                    if 1990 <= award_date.year <= current_year:
                        result['checks_passed'] += 1
                    else:
                        result['errors'].append(f'Invalid award date year: {award_date.year}')
            except ValueError:
                result['errors'].append(f'Invalid date format: {award_date}')
        
        # Check classification
        if 'classification' in certificate_data:
            result['total_checks'] += 1
            classification = certificate_data['classification']
            valid_classifications = ['First Class', 'Second Class Upper', 'Second Class Lower', 'Pass', 'Credit', 'Distinction']
            
            if classification in valid_classifications:
                result['checks_passed'] += 1
            else:
                result['warnings'].append(f'Unusual classification: {classification}')
        
        # Check program/field of study
        if 'program' in certificate_data:
            result['total_checks'] += 1
            program = certificate_data['program']
            if isinstance(program, str) and len(program.strip()) >= 3:
                result['checks_passed'] += 1
            else:
                result['errors'].append('Invalid program/field of study')
        
        # Calculate verification score
        if result['total_checks'] > 0:
            result['verification_score'] = (result['checks_passed'] / result['total_checks']) * 100
        
        # Determine overall status
        if result['verification_score'] >= 85:
            result['verification_status'] = 'verified'
        elif result['verification_score'] >= 65:
            result['verification_status'] = 'provisionally_verified'
        elif result['verification_score'] >= 45:
            result['verification_status'] = 'needs_review'
        else:
            result['verification_status'] = 'failed'
        
        # Add recommendations
        if result['verification_status'] in ['needs_review', 'failed']:
            result['recommendations'].extend([
                'Ensure institution is NCHE accredited',
                'Verify classification is clearly indicated',
                'Check that award date is correct',
                'Confirm program matches field of study',
            ])
        
        return result
    
    def extract_certificate_data_from_text(self, ocr_text: str, certificate_type: str) -> Dict:
        """
        Extract structured data from OCR text using pattern matching
        
        Args:
            ocr_text: Text extracted from certificate image/PDF
            certificate_type: Type of certificate (UCE, UACE, Diploma)
            
        Returns:
            Structured certificate data
        """
        extracted_data = {
            'certificate_type': certificate_type,
            'raw_text': ocr_text,
            'extracted_fields': {},
            'confidence_score': 0,
        }
        
        lines = ocr_text.split('\n')
        extracted_fields = {}
        
        # Common patterns to extract
        patterns = {
            'index_number': [
                r'Index\s*No[.:]*\s*([A-Z]\d{4}/\d{3})',
                r'Index\s*No[.:]*\s*([U]\d{4}/\d{3})',
                r'Candidate\s*No[.:]*\s*(\d{8})',
            ],
            'examination_year': [
                r'Year\s*of\s*Exam[ination]*[.:]*\s*(\d{4})',
                r'Exam\s*Year[.:]*\s*(\d{4})',
                r'(\d{4})',
            ],
            'school_name': [
                r'School\s*[:]\s*([^\n]+)',
                r'Institution\s*[:]\s*([^\n]+)',
            ],
            'candidate_name': [
                r'Name\s*[:]\s*([^\n]+)',
                r'Candidate\s*[:]\s*([^\n]+)',
            ],
        }
        
        # Extract fields using patterns
        for field_name, field_patterns in patterns.items():
            for pattern in field_patterns:
                for line in lines:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        extracted_fields[field_name] = match.group(1).strip()
                        break
        
        # Extract grades table
        if certificate_type in ['UCE', 'UACE']:
            grades = self._extract_grades_from_text(lines, certificate_type)
            if grades:
                extracted_fields['grades'] = grades
        
        # Calculate confidence score
        total_expected_fields = 4  # index, year, school, name
        extracted_count = len([v for v in extracted_fields.values() if v])
        extracted_data['confidence_score'] = (extracted_count / total_expected_fields) * 100
        extracted_data['extracted_fields'] = extracted_fields
        
        return extracted_data
    
    def _extract_grades_from_text(self, lines: List[str], certificate_type: str) -> List[Dict]:
        """
        Extract grade information from certificate text
        
        Args:
            lines: Text lines from certificate
            certificate_type: Type of certificate
            
        Returns:
            List of grade entries
        """
        grades = []
        
        # Look for grade patterns in certificate text
        grade_patterns = {
            'UCE': [
                r'(\w+(?:\s+\w+)*)\s*[:]\s*([A-Z]\d*)\s*[:]\s*(\d+)',
                r'(\w+(?:\s+\w+)*)\s*-\s*([A-Z]\d*)\s*-\s*(\d+)',
            ],
            'UACE': [
                r'(\w+(?:\s+\w+)*)\s*[:]\s*([A-Z])\s*\((?:Principal|Subsidiary)\)',
                r'(\w+(?:\s+\w+)*)\s*-\s*([A-Z])\s*\((?:Principal|Subsidiary)\)',
            ],
        }
        
        patterns = grade_patterns.get(certificate_type, [])
        
        for line in lines:
            for pattern in patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if len(match) >= 2:
                        subject = match[0].strip()
                        grade = match[1].strip()
                        
                        grade_entry = {
                            'subject': subject,
                            'grade': grade,
                        }
                        
                        # Add subject type for UACE
                        if certificate_type == 'UACE':
                            if 'principal' in line.lower():
                                grade_entry['subject_type'] = 'principal'
                            elif 'subsidiary' in line.lower():
                                grade_entry['subject_type'] = 'subsidiary'
                            else:
                                # Try to infer from common subjects
                                if subject in ['General Paper', 'Subsidiary ICT', 'Subsidiary Mathematics']:
                                    grade_entry['subject_type'] = 'subsidiary'
                                else:
                                    grade_entry['subject_type'] = 'principal'
                        
                        grades.append(grade_entry)
        
        return grades
    
    def verify_certificate_file(self, file_path: str, certificate_type: str) -> Dict:
        """
        Main verification method that coordinates the verification process
        
        Args:
            file_path: Path to uploaded certificate file
            certificate_type: Type of certificate to verify
            
        Returns:
            Comprehensive verification result
        """
        result = {
            'file_path': file_path,
            'certificate_type': certificate_type,
            'verification_status': 'pending',
            'verification_timestamp': datetime.utcnow().isoformat(),
            'file_analysis': {},
            'verification_result': {},
            'recommendations': [],
        }
        
        try:
            # Basic file analysis
            file_info = self._analyze_file(file_path)
            result['file_analysis'] = file_info
            
            if not file_info['is_valid']:
                result['verification_status'] = 'failed'
                result['verification_result'] = {
                    'errors': [file_info['error']],
                    'verification_score': 0,
                }
                return result
            
            # Perform certificate-specific verification
            if certificate_type.upper() == 'UCE':
                # For now, return basic verification
                # In a real implementation, you would integrate with OCR service
                verification_result = {
                    'verification_status': 'needs_manual_review',
                    'verification_score': 50,
                    'errors': [],
                    'warnings': ['OCR verification not yet implemented - manual review required'],
                    'recommendations': ['Manual verification by admissions office required'],
                }
            elif certificate_type.upper() == 'UACE':
                verification_result = {
                    'verification_status': 'needs_manual_review',
                    'verification_score': 50,
                    'errors': [],
                    'warnings': ['OCR verification not yet implemented - manual review required'],
                    'recommendations': ['Manual verification by admissions office required'],
                }
            elif certificate_type.upper() in ['DIPLOMA', 'HEC']:
                verification_result = {
                    'verification_status': 'needs_manual_review',
                    'verification_score': 50,
                    'errors': [],
                    'warnings': ['OCR verification not yet implemented - manual review required'],
                    'recommendations': ['Manual verification by admissions office required'],
                }
            else:
                verification_result = {
                    'verification_status': 'failed',
                    'verification_score': 0,
                    'errors': [f'Unknown certificate type: {certificate_type}'],
                }
            
            result['verification_result'] = verification_result
            result['verification_status'] = verification_result['verification_status']
            
        except Exception as e:
            log.error(f"Certificate verification failed: {str(e)}")
            result['verification_status'] = 'error'
            result['verification_result'] = {
                'errors': [f'Verification error: {str(e)}'],
                'verification_score': 0,
            }
        
        return result
    
    def _analyze_file(self, file_path: str) -> Dict:
        """
        Analyze uploaded file for basic validity
        
        Args:
            file_path: Path to the uploaded file
            
        Returns:
            File analysis result
        """
        if not os.path.exists(file_path):
            return {
                'is_valid': False,
                'error': 'File does not exist',
                'file_size': 0,
                'file_type': 'unknown',
            }
        
        file_size = os.path.getsize(file_path)
        file_ext = os.path.splitext(file_path)[1].lower()
        
        # Check file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB
        if file_size > max_size:
            return {
                'is_valid': False,
                'error': f'File too large: {file_size} bytes (max: {max_size} bytes)',
                'file_size': file_size,
                'file_type': file_ext,
            }
        
        # Check file extension
        allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
        if file_ext not in allowed_extensions:
            return {
                'is_valid': False,
                'error': f'Invalid file type: {file_ext}',
                'file_size': file_size,
                'file_type': file_ext,
            }
        
        return {
            'is_valid': True,
            'error': None,
            'file_size': file_size,
            'file_type': file_ext,
        }

# Global instance
certificate_verifier = CertificateVerificationService()
