import asyncio
import logging
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.session import async_session_factory, init_db
from app.db.models import HCP, Interaction, Channel, InteractionType, Sentiment, Source, Status

logger = logging.getLogger(__name__)

SAMPLE_HCPS = [
    {
        "name": "Dr. Rajesh Kumar",
        "specialty": "Oncology",
        "organization": "City Medical Center",
        "email": "rajesh.kumar@citymed.com",
        "phone": "+1-555-0101",
        "notes": "Specializes in colorectal cancer",
    },
    {
        "name": "Dr. Sarah Chen",
        "specialty": "Cardiology",
        "organization": "Heart Health Hospital",
        "email": "sarah.chen@heartcare.com",
        "phone": "+1-555-0102",
        "notes": "Leading expert in interventional cardiology",
    },
    {
        "name": "Dr. Michael O'Brien",
        "specialty": "Respiratory Medicine",
        "organization": "Lung Institute",
        "email": "m.obrien@lunginst.com",
        "phone": "+1-555-0103",
        "notes": "COPD and asthma specialist",
    },
    {
        "name": "Dr. Emily Watson",
        "specialty": "Rheumatology",
        "organization": "Joint Care Clinic",
        "email": "emily.watson@jointcare.com",
        "phone": "+1-555-0104",
        "notes": "Lupus and autoimmune disease focus",
    },
    {
        "name": "Dr. Priya Patel",
        "specialty": "Gastroenterology",
        "organization": "Digestive Health Center",
        "email": "priya.patel@dighealth.com",
        "phone": "+1-555-0105",
        "notes": "IBD and endoscopy specialist",
    },
]

SAMPLE_INTERACTIONS = [
    {
        "hcp_name": "Dr. Rajesh Kumar",
        "interaction_type": InteractionType.MEETING,
        "channel": Channel.IN_PERSON,
        "subject": "Discussion on Onco-X Trial Results",
        "notes": "Presented Q3 efficacy data. Positive response to new formulation.",
        "sentiment": Sentiment.POSITIVE,
        "products": ["Onco-X", "Onco-X Plus"],
        "days_ago": 2,
    },
    {
        "hcp_name": "Dr. Sarah Chen",
        "interaction_type": InteractionType.CALL,
        "channel": Channel.PHONE,
        "subject": "Follow-up on Cardio-Z Patient Cases",
        "notes": "Discussed 5 patient case studies. Requested more clinical data.",
        "sentiment": Sentiment.NEUTRAL,
        "products": ["Cardio-Z"],
        "days_ago": 5,
    },
    {
        "hcp_name": "Dr. Michael O'Brien",
        "interaction_type": InteractionType.EMAIL,
        "channel": Channel.EMAIL,
        "subject": "Resp-Pro Conference Presentation",
        "notes": "Confirmed participation in CHEST conference. Will present on Resp-Pro.",
        "sentiment": Sentiment.POSITIVE,
        "products": ["Resp-Pro"],
        "days_ago": 7,
    },
    {
        "hcp_name": "Dr. Emily Watson",
        "interaction_type": InteractionType.SAMPLE_DROP,
        "channel": Channel.IN_PERSON,
        "subject": "Provided Rheumo-Care Sample",
        "notes": "Left 30 samples of Rheumo-Care. Request for patient feedback by EOQ.",
        "sentiment": Sentiment.POSITIVE,
        "products": ["Rheumo-Care"],
        "days_ago": 10,
    },
    {
        "hcp_name": "Dr. Priya Patel",
        "interaction_type": InteractionType.MEETING,
        "channel": Channel.VIDEO,
        "subject": "Gastro-Ease Review and Market Analysis",
        "notes": "Reviewed market trends. Discussed competitor landscape.",
        "sentiment": Sentiment.NEUTRAL,
        "products": ["Gastro-Ease"],
        "days_ago": 14,
    },
]


async def seed_database() -> None:
    async with async_session_factory() as session:
        try:
            existing_hcps = await session.execute(text("SELECT COUNT(*) FROM hcps"))
            if existing_hcps.scalar() > 0:
                logger.info("Database already seeded. Skipping...")
                return

            logger.info("Seeding HCPs...")
            hcps_by_name = {}
            for hcp_data in SAMPLE_HCPS:
                hcp = HCP(**hcp_data)
                session.add(hcp)
                await session.flush()
                hcps_by_name[hcp.name] = hcp
            await session.commit()
            logger.info(f"Created {len(SAMPLE_HCPS)} HCPs")

            logger.info("Seeding Interactions...")
            for interaction_data in SAMPLE_INTERACTIONS:
                hcp_name = interaction_data.pop("hcp_name")
                days_ago = interaction_data.pop("days_ago")
                hcp = hcps_by_name[hcp_name]

                interaction = Interaction(
                    hcp_id=hcp.id,
                    user_id="seed_user",
                    interaction_date=datetime.utcnow() - timedelta(days=days_ago),
                    source=Source.FORM,
                    status=Status.LOGGED,
                    **interaction_data,
                )
                session.add(interaction)
            await session.commit()
            logger.info(f"Created {len(SAMPLE_INTERACTIONS)} Interactions")
            logger.info("Database seeding completed successfully!")

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            await session.rollback()
            raise


async def main() -> None:
    settings = get_settings()
    logging.basicConfig(level=settings.log_level)
    # Ensure tables exist before seeding so the script is runnable standalone.
    await init_db()
    await seed_database()


if __name__ == "__main__":
    asyncio.run(main())
