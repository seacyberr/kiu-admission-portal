"""
Opportunity Matching Service
Matches finalists to opportunities based on skills and program alignment.
Uses only existing database models - no external APIs.
"""
from typing import List, Dict, Tuple
from models import db, FinalistProfile, Opportunity, OpportunityApplication, User


class OpportunityMatchingService:
    """
    Simple matching algorithm using existing skills and program data.
    No external APIs, no complex ML - just efficient database queries.
    """
    
    @staticmethod
    def calculate_match_score(finalist: FinalistProfile, opportunity: Opportunity) -> Tuple[int, List[str]]:
        """
        Calculate match score (0-100) and return matching factors.
        """
        score = 0
        factors = []
        
        # Get finalist skills (lowercase for comparison)
        finalist_skills = set(s.lower().strip() for s in (finalist.skills or []))
        required_skills = set(s.lower().strip() for s in (opportunity.required_skills or []))
        
        # Skills match (max 50 points)
        if required_skills:
            matched_skills = finalist_skills & required_skills
            skill_score = (len(matched_skills) / len(required_skills)) * 50
            score += skill_score
            if matched_skills:
                factors.append(f"Skills: {', '.join(matched_skills)}")
        else:
            score += 25  # No specific skills required, partial credit
        
        # Program match (max 30 points)
        if opportunity.required_programs and finalist.program_id in opportunity.required_programs:
            score += 30
            factors.append("Program match")
        elif not opportunity.required_programs:
            score += 15  # No specific program required
        
        # Year of study match (max 20 points)
        # Finalists in final year get full points
        if finalist.year_of_study >= 3:
            score += 20
            factors.append("Final year finalist")
        else:
            score += 10
        
        return int(score), factors
    
    @classmethod
    def find_matches_for_finalist(cls, finalist_id: int, min_score: int = 50, limit: int = 10) -> List[Dict]:
        """
        Find best matching opportunities for a finalist.
        """
        finalist = FinalistProfile.query.get(finalist_id)
        if not finalist:
            return []
        
        # Get active opportunities
        opportunities = Opportunity.query.filter_by(is_active=True).all()
        
        # Calculate scores
        scored_opportunities = []
        for opp in opportunities:
            score, factors = cls.calculate_match_score(finalist, opp)
            if score >= min_score:
                # Check if already applied
                already_applied = OpportunityApplication.query.filter_by(
                    opportunity_id=opp.id,
                    user_id=finalist.user_id
                ).first() is not None
                
                scored_opportunities.append({
                    "opportunity": opp,
                    "score": score,
                    "factors": factors,
                    "alreadyApplied": already_applied
                })
        
        # Sort by score descending
        scored_opportunities.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top matches with serialized data
        return [
            {
                **opp["opportunity"].to_dict(),
                "matchScore": opp["score"],
                "matchFactors": opp["factors"],
                "alreadyApplied": opp["alreadyApplied"]
            }
            for opp in scored_opportunities[:limit]
        ]
    
    @classmethod
    def find_matches_for_opportunity(cls, opportunity_id: int, min_score: int = 50) -> List[Dict]:
        """
        Find best matching finalists for an opportunity.
        Useful for admin dashboard.
        """
        opportunity = Opportunity.query.get(opportunity_id)
        if not opportunity:
            return []
        
        # Get all finalists
        finalists = FinalistProfile.query.filter_by(is_finalist=True).all()
        
        scored_finalists = []
        for finalist in finalists:
            score, factors = cls.calculate_match_score(finalist, opportunity)
            if score >= min_score:
                scored_finalists.append({
                    "finalist": finalist,
                    "score": score,
                    "factors": factors
                })
        
        scored_finalists.sort(key=lambda x: x["score"], reverse=True)
        
        return [
            {
                **opp["finalist"].to_dict(),
                "matchScore": opp["score"],
                "matchFactors": opp["factors"]
            }
            for opp in scored_finalists
        ]
