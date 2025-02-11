from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc
from typing import List, Optional, Dict, Any
from app.models.insurance_plan import InsurancePlan
from app.schemas.insurance_plan import InsurancePlanCreate, InsurancePlanUpdate
from app.exceptions import PlanNotFoundException, ComparisonError

class InsurancePlanService:
    """
    Service for managing insurance plan operations and comparisons.
    
    This service handles:
    1. CRUD operations for insurance plans
    2. Plan comparison logic
    3. Benefit analysis
    4. Popularity tracking
    5. Suitability scoring
    
    Future AI Implementation Guide:
    -----------------------------
    To implement AI-powered comparisons in the future:
    
    1. Suitability Scoring:
        - Use machine learning to analyze historical policy data
        - Consider factors like:
            * Vehicle type and age
            * Route characteristics
            * Driver history
            * Claim history
            * Payment patterns
        - Implement A/B testing for scoring algorithms
    
    2. Recommendation Engine:
        - Build a collaborative filtering system
        - Consider implementing:
            * User similarity metrics
            * Plan feature vectors
            * Usage pattern analysis
            * Seasonal variations
    
    3. Dynamic Pricing:
        - Implement real-time premium adjustments
        - Consider:
            * Time of day pricing
            * Route-based pricing
            * Usage-based insurance features
    
    4. Fraud Detection:
        - Add anomaly detection
        - Monitor:
            * Claim patterns
            * Usage patterns
            * Payment behaviors
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_plan(self, plan: InsurancePlanCreate) -> InsurancePlan:
        """Create a new insurance plan"""
        db_plan = InsurancePlan(
            name=plan.name,
            provider=plan.provider,
            monthly_premium=float(plan.monthly_premium),
            benefits=plan.benefits,
            plan_type=plan.plan_type,
            description=plan.description,
            terms_conditions=plan.terms_conditions,
            suitability_score=0.0,  # Initial score
            popularity_score=0.0     # Initial score
        )
        self.db.add(db_plan)
        await self.db.commit()
        await self.db.refresh(db_plan)
        return db_plan

    async def get_comparable_plans(
        self,
        plan_type: Optional[str] = None,
        max_premium: Optional[float] = None,
        min_benefits: Optional[int] = None
    ) -> List[InsurancePlan]:
        """Get list of plans suitable for comparison"""
        query = select(InsurancePlan)
        
        if plan_type:
            query = query.filter(InsurancePlan.plan_type == plan_type)
        if max_premium:
            query = query.filter(InsurancePlan.monthly_premium <= max_premium)
            
        # Order by popularity and suitability
        query = query.order_by(
            desc(InsurancePlan.popularity_score),
            desc(InsurancePlan.suitability_score)
        )
        
        result = await self.db.execute(query)
        plans = result.scalars().all()
        
        # Filter by minimum benefits if specified
        if min_benefits:
            plans = [
                plan for plan in plans 
                if sum(1 for v in plan.benefits.values() if v) >= min_benefits
            ]
            
        return plans

    async def compare_plans(
        self,
        plan_ids: List[int],
        comparison_aspects: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Compare specific insurance plans"""
        # Fetch plans
        plans = []
        for plan_id in plan_ids:
            result = await self.db.execute(
                select(InsurancePlan).filter(InsurancePlan.id == plan_id)
            )
            plan = result.scalars().first()
            if not plan:
                raise PlanNotFoundException(f"Plan {plan_id} not found")
            plans.append(plan)

        # Perform comparison
        comparison = {
            "plans": plans,
            "benefit_comparison": self._compare_benefits(plans),
            "premium_analysis": self._analyze_premiums(plans),
            "coverage_summary": self._summarize_coverage(plans)
        }

        # Update popularity scores
        await self._update_comparison_popularity(plans)

        return comparison

    def _compare_benefits(self, plans: List[InsurancePlan]) -> Dict[str, Any]:
        """Compare benefits between plans"""
        all_benefits = set()
        for plan in plans:
            all_benefits.update(plan.benefits.keys())

        comparison = {}
        for benefit in all_benefits:
            comparison[benefit] = {
                plan.name: plan.benefits.get(benefit, False)
                for plan in plans
            }

        return comparison

    def _analyze_premiums(self, plans: List[InsurancePlan]) -> Dict[str, Any]:
        """Analyze premium differences"""
        premiums = [plan.monthly_premium for plan in plans]
        return {
            "lowest": min(premiums),
            "highest": max(premiums),
            "difference": max(premiums) - min(premiums),
            "average": sum(premiums) / len(premiums)
        }

    def _summarize_coverage(self, plans: List[InsurancePlan]) -> Dict[str, str]:
        """Generate coverage summary for each plan"""
        return {
            plan.name: {
                "type": plan.plan_type,
                "key_benefits": [
                    benefit for benefit, included in plan.benefits.items()
                    if included
                ],
                "premium_category": self._categorize_premium(plan.monthly_premium)
            }
            for plan in plans
        }

    async def _update_comparison_popularity(self, plans: List[InsurancePlan]):
        """Update popularity scores based on comparison frequency"""
        for plan in plans:
            plan.popularity_score = min(1.0, plan.popularity_score + 0.01)
        await self.db.commit()

    def _categorize_premium(self, premium: float) -> str:
        """Categorize premium into price brackets"""
        if premium < 5000:
            return "Budget"
        elif premium < 10000:
            return "Standard"
        elif premium < 20000:
            return "Premium"
        else:
            return "Luxury"