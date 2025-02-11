from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from typing import List
from datetime import datetime
import logging
import sentry_sdk

from app.models.claim import Claim, ClaimStatus
from app.models.policy import Policy  # Ensure Policy model exists
from app.schemas.claim import ClaimCreate, ClaimUpdate
from app.exceptions.claim import (
    ClaimNotFoundException,
    ClaimValidationError,
    DatabaseOperationError,
    ClaimBusinessRuleError,
)

logger = logging.getLogger(__name__)

class ClaimService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._setup_logging()

    def _setup_logging(self):
        """Configure service-specific logging with additional context."""
        self.logger = logging.getLogger(f"{__name__}.ClaimService")
        self.logger = logging.LoggerAdapter(self.logger, extra={"service": "claim_service"})

    async def submit_claim(self, claim_data: ClaimCreate) -> Claim:
        """Submit a new claim for a policy with robust error handling."""
        try:
            # Validate that the policy exists
            result = await self.db.execute(select(Policy).where(Policy.id == claim_data.policy_id))
            policy = result.scalars().first()
            if not policy:
                self.logger.warning(f"Policy not found for claim submission: {claim_data.policy_id}")
                raise ClaimValidationError(
                    message=f"Policy with ID {claim_data.policy_id} not found", field="policy_id"
                )

            # Business rule: only active policies may have claims submitted
            if policy.status != "ACTIVE":
                raise ClaimBusinessRuleError(
                    message="Claims can only be submitted for active policies", rule_name="policy_status"
                )

            # Create the Claim record
            db_claim = Claim(
                policy_id=claim_data.policy_id,
                incident_date=claim_data.incident_date,
                description=claim_data.description,
                amount_claimed=claim_data.amount_claimed,
                evidence_url=claim_data.evidence_url,
                status=ClaimStatus.SUBMITTED,
                submission_date=datetime.now(),
                last_modified=datetime.now(),
            )

            async with self.db.begin():
                self.db.add(db_claim)
            await self.db.refresh(db_claim)
            self.logger.info("Claim submitted successfully", extra={"claim_id": db_claim.id})
            return db_claim

        except IntegrityError as e:
            self.logger.error("Integrity error during claim submission: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise ClaimValidationError(
                message="Integrity error: duplicate or invalid data", field="unknown"
            ) from e
        except SQLAlchemyError as e:
            self.logger.error("Database error in submit_claim: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to submit claim", operation="create_claim"
            ) from e

    async def get_claim(self, claim_id: int) -> Claim:
        """Retrieve a claim by its ID."""
        try:
            result = await self.db.execute(select(Claim).where(Claim.id == claim_id))
            claim = result.scalars().first()
            if not claim:
                self.logger.warning(f"Claim not found: {claim_id}")
                raise ClaimNotFoundException(message=f"Claim {claim_id} not found", claim_id=claim_id)
            return claim

        except SQLAlchemyError as e:
            self.logger.error("Database error in get_claim: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to fetch claim", operation="read_claim"
            ) from e

    async def update_claim(self, claim_id: int, claim_update: ClaimUpdate) -> Claim:
        """Update an existing claim."""
        try:
            result = await self.db.execute(select(Claim).where(Claim.id == claim_id))
            db_claim = result.scalars().first()
            if not db_claim:
                self.logger.warning(f"Claim not found for update: {claim_id}")
                raise ClaimNotFoundException(message=f"Claim {claim_id} not found", claim_id=claim_id)
            
            # Update only allowed fields
            if claim_update.description is not None:
                db_claim.description = claim_update.description
            if claim_update.amount_claimed is not None:
                db_claim.amount_claimed = claim_update.amount_claimed
            if claim_update.evidence_url is not None:
                db_claim.evidence_url = claim_update.evidence_url
            if claim_update.status is not None:
                # Optionally, add validations for allowed status transitions.
                db_claim.status = claim_update.status
            db_claim.last_modified = datetime.now()

            async with self.db.begin():
                self.db.add(db_claim)
            await self.db.refresh(db_claim)
            self.logger.info("Claim updated successfully", extra={"claim_id": db_claim.id})
            return db_claim

        except IntegrityError as e:
            self.logger.error("Integrity error during claim update: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise ClaimValidationError(
                message="Integrity error: duplicate or invalid data", field="unknown"
            ) from e
        except SQLAlchemyError as e:
            self.logger.error("Database error in update_claim: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to update claim", operation="update_claim"
            ) from e

    async def list_claims(self, policy_id: int = None) -> List[Claim]:
        """List claims, optionally filtered by policy."""
        try:
            query = select(Claim)
            if policy_id is not None:
                query = query.where(Claim.policy_id == policy_id)
            result = await self.db.execute(query)
            claims = result.scalars().all()
            self.logger.info("Claims fetched", extra={"count": len(claims)})
            return claims
        except SQLAlchemyError as e:
            self.logger.error("Database error in list_claims: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to list claims", operation="read_claims"
            ) from e

    async def process_claim(self, claim_id: int, approved: bool, amount_settled: float = None) -> Claim:
        """
        Process a claim by approving or rejecting it.
        If approved, record the settled amount.
        """
        try:
            result = await self.db.execute(select(Claim).where(Claim.id == claim_id))
            db_claim = result.scalars().first()
            if not db_claim:
                self.logger.warning(f"Claim not found for processing: {claim_id}")
                raise ClaimNotFoundException(message=f"Claim {claim_id} not found", claim_id=claim_id)
            
            # Business rule: approved claims must have an amount_settled value
            if approved:
                if amount_settled is None:
                    raise ClaimBusinessRuleError(
                        message="Approved claims must include a settled amount", rule_name="settled_amount_required"
                    )
                db_claim.amount_settled = amount_settled
                db_claim.status = ClaimStatus.APPROVED
            else:
                db_claim.status = ClaimStatus.REJECTED

            db_claim.last_modified = datetime.now()

            async with self.db.begin():
                self.db.add(db_claim)
            await self.db.refresh(db_claim)
            self.logger.info("Claim processed", extra={"claim_id": db_claim.id, "approved": approved})
            return db_claim

        except SQLAlchemyError as e:
            self.logger.error("Database error in process_claim: %s", str(e), exc_info=True)
            sentry_sdk.capture_exception(e)
            raise DatabaseOperationError(
                message="Failed to process claim", operation="process_claim"
            ) from e
