import logging
import sentry_sdk

from fastapi import BackgroundTasks

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
from datetime import datetime, timedelta

from app.services.webhook_service import WebhookService

from app.models.policy import Policy
from app.schemas.policy import PolicyCreate, PolicyUpdate, PolicyOut
from app.core.exceptions import (
    PolicyNotFoundException,
    PolicyValidationError,
    DatabaseOperationError,
    PolicyBusinessRuleError,
    PremiumCalculationError
)

logger = logging.getLogger(__name__)

class PolicyService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._setup_logging()

    def _setup_logging(self):
        """Configure service-specific logging with extra context."""
        self.logger = logging.getLogger(f"{__name__}.PolicyService")
        self.logger = logging.LoggerAdapter(
            self.logger,
            extra={"service": "policy_service"}
        )
        
    async def create_policy(self, policy: PolicyCreate) -> Policy:
        """Create a new insurance policy for a Matatu with robust error handling."""
        try:
            # Validate business rules before creating the policy.
            await self._validate_policy_creation(policy)
            
            # Calculate premium and handle any errors.
            try:
                premium = self._calculate_premium(
                    policy.coverage_type,
                    policy.matatu_registration
                )
            except Exception as e:
                self.logger.error(f"Premium calculation failed: {str(e)}", exc_info=True)
                sentry_sdk.capture_exception(e)
                raise PremiumCalculationError(
                    message="Failed to calculate premium",
                    calculation_details={
                        "coverage_type": policy.coverage_type,
                        "matatu_registration": policy.matatu_registration
                    }
                ) from e

            # Prepare the policy record.
            db_policy = Policy(
                matatu_registration=policy.matatu_registration.upper(),
                owner_name=policy.owner_name,
                coverage_type=policy.coverage_type,
                premium_amount=premium,
                start_date=datetime.now(),
                end_date=policy.end_date,
                status="ACTIVE",
                last_modified=datetime.now()
            )

            # Use a transaction block so that the add and commit happen atomically.
            async with self.db.begin():
                self.db.add(db_policy)
            
            # Refresh the instance to fetch generated values (e.g., primary key).
            await self.db.refresh(db_policy)
            self.logger.info(
                "Policy created successfully",
                extra={
                    "policy_id": db_policy.id,
                    "matatu_reg": db_policy.matatu_registration
                }
            )
            
            webhook_service = WebhookService(db)
            await webhook_service.trigger_event("policy_created", {"policy_id": new_policy.id, "status": new_policy.status})
            return db_policy

        except IntegrityError as e:
            self.logger.error(f"Database integrity error: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise PolicyValidationError(
                message="A policy with this registration number already exists",
                validation_errors={"matatu_registration": "duplicate"}
            ) from e
        except SQLAlchemyError as e:
            self.logger.error(f"Database error in create_policy: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to create policy",
                operation="create"
            ) from e

    async def _validate_policy_creation(self, policy: PolicyCreate):
        """Validate business rules before creating a policy."""
        # Check that the policy duration does not exceed 1 year.
        duration = (policy.end_date - datetime.now()).days
        if duration > 365:
            raise PolicyBusinessRuleError(
                message="Policy duration cannot exceed 1 year",
                rule_name="max_duration"
            )
        
        # Check if an active policy already exists for the given Matatu registration.
        result = await self.db.execute(
            select(Policy).where(
                and_(
                    Policy.matatu_registration == policy.matatu_registration.upper(),
                    Policy.status == "ACTIVE"
                )
            )
        )
        if result.scalars().first():
            raise PolicyBusinessRuleError(
                message="An active policy already exists for this Matatu",
                rule_name="unique_active_policy"
            )

    async def get_policy(self, policy_id: int) -> Policy:
        """Retrieve a single policy by ID with robust error handling."""
        try:
            result = await self.db.execute(
                select(Policy).where(Policy.id == policy_id)
            )
            policy = result.scalars().first()
            if not policy:
                self.logger.warning(f"Policy not found: {policy_id}")
                raise PolicyNotFoundException(
                    message=f"Policy {policy_id} not found",
                    policy_id=policy_id
                )
            return policy

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_policy: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to fetch policy",
                operation="read"
            ) from e

    async def get_expiring_policies(self, days_threshold: int = 30) -> List[Policy]:
        """Retrieve policies expiring soon with robust error handling."""
        try:
            expiry_date = datetime.now() + timedelta(days=days_threshold)
            query = select(Policy).where(
                and_(
                    Policy.status == "ACTIVE",
                    Policy.end_date <= expiry_date
                )
            )
            result = await self.db.execute(query)
            policies = result.scalars().all()
            self.logger.info(
                f"Found {len(policies)} policies expiring within {days_threshold} days"
            )
            return policies

        except SQLAlchemyError as e:
            self.logger.error(f"Database error in get_expiring_policies: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to fetch expiring policies",
                operation="read_expiring"
            ) from e

    def _calculate_premium(self, coverage_type: str, matatu_registration: str) -> float:
        """Calculate the premium based on coverage type and other business logic."""
        try:
            # Define base premium rates.
            base_rates = {
                "COMPREHENSIVE": 50000.0,
                "THIRD_PARTY": 25000.0,
                "THIRD_PARTY_FIRE_THEFT": 35000.0
            }
            
            coverage_type_key = coverage_type.upper()
            if coverage_type_key not in base_rates:
                raise PremiumCalculationError(
                    message="Invalid coverage type",
                    calculation_details={"invalid_type": coverage_type}
                )
            
            base_premium = base_rates[coverage_type_key]
            # Optionally, add more logic here (e.g., adjustments based on vehicle age, route, etc.)
            return base_premium

        except Exception as e:
            self.logger.error(f"Premium calculation error: {str(e)}", exc_info=True)
            sentry_sdk.capture_exception(e)
            raise PremiumCalculationError(
                message="Failed to calculate premium",
                calculation_details={
                    "coverage_type": coverage_type,
                    "matatu_registration": matatu_registration
                }
            ) from e
