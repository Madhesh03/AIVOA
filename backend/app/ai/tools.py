from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.interaction import Channel, InteractionType, Sentiment, Source, Status
from app.schemas.interaction import InteractionCreate, InteractionDraft, InteractionUpdate
from app.services.hcp_service import HCPService
from app.services.interaction_service import InteractionService


class ToolExecutor:
    def __init__(self, session: AsyncSession, user_id: str):
        self.interaction_service = InteractionService(session)
        self.hcp_service = HCPService(session)
        self.user_id = user_id

    async def log_interaction(
        self,
        hcp_name: str,
        interaction_type: str,
        channel: str,
        subject: str,
        interaction_date: Optional[str] = None,
        notes: Optional[str] = None,
        sentiment: Optional[str] = None,
        products: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        try:
            hcp = await self.hcp_service.get_or_create_by_name(hcp_name)

            # Handle natural language dates
            if interaction_date:
                date_lower = interaction_date.lower().strip()
                now = datetime.utcnow()

                if date_lower in ("today", "now", "today's"):
                    interaction_date_dt = now
                elif date_lower == "yesterday":
                    interaction_date_dt = now - timedelta(days=1)
                elif date_lower == "tomorrow":
                    interaction_date_dt = now + timedelta(days=1)
                else:
                    try:
                        interaction_date_dt = datetime.fromisoformat(interaction_date)
                    except ValueError:
                        # Fallback to today if date parsing fails
                        interaction_date_dt = now
            else:
                interaction_date_dt = datetime.utcnow()

            # Handle products as either list or string representation
            products_list = []
            if products:
                if isinstance(products, str):
                    try:
                        import json
                        products_list = json.loads(products)
                        if not isinstance(products_list, list):
                            products_list = [str(products)]
                    except (json.JSONDecodeError, TypeError):
                        products_list = [str(products)]
                else:
                    products_list = list(products) if products else []

            create_data = InteractionCreate(
                hcp_id=hcp.id,
                user_id=self.user_id,
                interaction_type=InteractionType(interaction_type.lower()),
                channel=Channel(channel.lower().replace(" ", "_")),
                interaction_date=interaction_date_dt,
                subject=subject,
                notes=notes,
                sentiment=Sentiment(sentiment.lower()) if sentiment else None,
                products=products_list,
                follow_up_actions=[],
            )

            interaction = await self.interaction_service.create_interaction(
                create_data, source=Source.AI_ASSISTANT, status=Status.DRAFT
            )

            form_prefill = InteractionDraft(
                hcp_id=interaction.hcp_id,
                hcp_name=hcp_name,
                interaction_type=interaction.interaction_type,
                channel=interaction.channel,
                interaction_date=interaction.interaction_date,
                subject=interaction.subject,
                notes=interaction.notes,
                sentiment=interaction.sentiment,
                products=interaction.products or [],
                follow_up_actions=interaction.follow_up_actions or [],
            )

            return {
                "success": True,
                "interaction_id": str(interaction.id),
                "message": f"Logged interaction with {hcp_name}",
                # mode="json" ensures UUID/datetime become JSON-safe strings for
                # the SSE stream and the frontend form.
                "form_prefill": form_prefill.model_dump(mode="json"),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def edit_interaction(
        self,
        interaction_id: str,
        hcp_name: Optional[str] = None,
        interaction_type: Optional[str] = None,
        channel: Optional[str] = None,
        subject: Optional[str] = None,
        interaction_date: Optional[str] = None,
        notes: Optional[str] = None,
        sentiment: Optional[str] = None,
        products: Optional[list[str]] = None,
        follow_up_actions: Optional[list[dict[str, Any]]] = None,
    ) -> dict[str, Any]:
        import logging
        logger = logging.getLogger(__name__)

        try:
            logger.info(f"edit_interaction called: id={interaction_id}, fields={[k for k in [hcp_name, interaction_type, channel, subject, interaction_date, notes, sentiment, products, follow_up_actions] if k]}")

            interaction_id_uuid = UUID(interaction_id)

            update_data_dict: dict[str, Any] = {}
            if hcp_name:
                hcp = await self.hcp_service.get_or_create_by_name(hcp_name)
                update_data_dict["hcp_id"] = hcp.id
            if interaction_type:
                update_data_dict["interaction_type"] = InteractionType(
                    interaction_type.lower()
                )
            if channel:
                update_data_dict["channel"] = Channel(channel.lower().replace(" ", "_"))
            if subject:
                update_data_dict["subject"] = subject
            if interaction_date:
                # Handle natural language dates like log_interaction does
                date_lower = interaction_date.lower().strip()
                now = datetime.utcnow()

                if date_lower in ("today", "now", "today's"):
                    update_data_dict["interaction_date"] = now
                elif date_lower == "yesterday":
                    update_data_dict["interaction_date"] = now - timedelta(days=1)
                elif date_lower == "tomorrow":
                    update_data_dict["interaction_date"] = now + timedelta(days=1)
                else:
                    try:
                        update_data_dict["interaction_date"] = datetime.fromisoformat(interaction_date)
                    except ValueError:
                        logger.warning(f"Could not parse date: {interaction_date}, using now")
                        update_data_dict["interaction_date"] = now

            if notes is not None:
                update_data_dict["notes"] = notes
            if sentiment:
                update_data_dict["sentiment"] = Sentiment(sentiment.lower())
            if products is not None:
                # Handle products as either list or string representation
                if isinstance(products, str):
                    try:
                        import json
                        products_list = json.loads(products)
                        if not isinstance(products_list, list):
                            products_list = [str(products)]
                    except (json.JSONDecodeError, TypeError):
                        products_list = [str(products)]
                    update_data_dict["products"] = products_list
                else:
                    update_data_dict["products"] = list(products) if products else []

            if follow_up_actions is not None:
                update_data_dict["follow_up_actions"] = follow_up_actions

            logger.info(f"Update data: {update_data_dict}")
            update_data = InteractionUpdate(**update_data_dict)
            updated = await self.interaction_service.update_interaction(
                interaction_id_uuid, update_data
            )

            logger.info(f"Successfully updated interaction {interaction_id}")

            # Return form_prefill so the frontend updates the form with new values
            form_prefill = InteractionDraft(
                hcp_id=updated.hcp_id,
                hcp_name=None,  # Not retrieved, but not needed for display
                interaction_type=updated.interaction_type,
                channel=updated.channel,
                interaction_date=updated.interaction_date,
                subject=updated.subject,
                notes=updated.notes,
                sentiment=updated.sentiment,
                products=updated.products or [],
                follow_up_actions=updated.follow_up_actions or [],
            )

            return {
                "success": True,
                "interaction_id": str(updated.id),
                "message": f"Updated interaction {interaction_id}",
                "form_prefill": form_prefill.model_dump(mode="json"),
            }
        except Exception as e:
            logger.error(f"Error in edit_interaction: {str(e)}", exc_info=True)
            return {"success": False, "error": str(e)}

    async def search_interactions(
        self, query: str, hcp_name: Optional[str] = None, limit: int = 5
    ) -> dict[str, Any]:
        try:
            hcp_id = None
            if hcp_name:
                hcp = await self.hcp_service.get_or_create_by_name(hcp_name)
                hcp_id = hcp.id

            interactions, total = await self.interaction_service.search_interactions(
                query=query, hcp_id=hcp_id, skip=0, limit=limit
            )

            results = [
                {
                    "id": str(i.id),
                    "hcp_id": str(i.hcp_id),
                    "type": i.interaction_type,
                    "subject": i.subject,
                    "date": i.interaction_date.isoformat(),
                    "sentiment": i.sentiment,
                }
                for i in interactions
            ]

            return {
                "success": True,
                "results": results,
                "total": total,
                "message": f"Found {total} interactions matching '{query}'",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def summarize_interaction(
        self, interaction_id: str, summary: str
    ) -> dict[str, Any]:
        try:
            interaction_id_uuid = UUID(interaction_id)
            updated = await self.interaction_service.add_ai_summary(
                interaction_id_uuid, summary
            )

            return {
                "success": True,
                "interaction_id": str(updated.id),
                "message": f"Added summary to interaction {interaction_id}",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def suggest_followups(
        self, interaction_id: str, followup_actions: list[dict[str, Any]]
    ) -> dict[str, Any]:
        import logging
        logger = logging.getLogger(__name__)

        try:
            interaction_id_uuid = UUID(interaction_id)

            # Handle followup_actions as either list or string representation
            actions_list = []
            if followup_actions:
                if isinstance(followup_actions, str):
                    try:
                        import json
                        actions_list = json.loads(followup_actions)
                        if not isinstance(actions_list, list):
                            actions_list = [followup_actions]
                    except (json.JSONDecodeError, TypeError):
                        actions_list = [{"action": str(followup_actions)}]
                else:
                    actions_list = list(followup_actions) if followup_actions else []

            logger.info(f"suggest_followups: id={interaction_id}, actions={actions_list}")
            updated = await self.interaction_service.add_followup_actions(
                interaction_id_uuid, actions_list
            )

            return {
                "success": True,
                "interaction_id": str(updated.id),
                "actions_count": len(followup_actions),
                "message": f"Added {len(followup_actions)} follow-up actions",
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


def create_tools(executor: ToolExecutor) -> list[dict[str, Any]]:
    return [
        {
            "name": "log_interaction",
            "description": "Log a new healthcare professional interaction. Creates a draft interaction record.",
            "callable": executor.log_interaction,
            "schema": {
                "type": "object",
                "properties": {
                    "hcp_name": {
                        "type": "string",
                        "description": "Name of the healthcare professional",
                    },
                    "interaction_type": {
                        "type": "string",
                        "enum": ["meeting", "call", "email", "conference", "sample_drop"],
                        "description": "Type of interaction",
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["in_person", "phone", "video", "email"],
                        "description": "Communication channel used",
                    },
                    "subject": {
                        "type": "string",
                        "description": "Subject or title of the interaction",
                    },
                    "interaction_date": {
                        "type": "string",
                        "description": "ISO format date of interaction (optional, defaults to now)",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Detailed notes about the interaction",
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "neutral", "negative"],
                        "description": "Overall sentiment of the interaction",
                    },
                    "products": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Products or medications discussed",
                    },
                },
                "required": ["hcp_name", "interaction_type", "channel", "subject"],
            },
        },
        {
            "name": "edit_interaction",
            "description": "Edit an existing interaction record. Update any field.",
            "callable": executor.edit_interaction,
            "schema": {
                "type": "object",
                "properties": {
                    "interaction_id": {
                        "type": "string",
                        "description": "UUID of the interaction to edit",
                    },
                    "hcp_name": {
                        "type": "string",
                        "description": "New HCP name",
                    },
                    "interaction_type": {
                        "type": "string",
                        "enum": ["meeting", "call", "email", "conference", "sample_drop"],
                    },
                    "channel": {
                        "type": "string",
                        "enum": ["in_person", "phone", "video", "email"],
                    },
                    "subject": {
                        "type": "string",
                        "description": "New subject",
                    },
                    "interaction_date": {
                        "type": "string",
                        "description": "ISO format date",
                    },
                    "notes": {
                        "type": "string",
                        "description": "Updated notes",
                    },
                    "sentiment": {
                        "type": "string",
                        "enum": ["positive", "neutral", "negative"],
                    },
                    "products": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "follow_up_actions": {
                        "type": "array",
                        "items": {"type": "object"},
                    },
                },
                "required": ["interaction_id"],
            },
        },
        {
            "name": "search_interactions",
            "description": "Search for existing interactions by keyword or HCP name.",
            "callable": executor.search_interactions,
            "schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (subject, notes, etc.)",
                    },
                    "hcp_name": {
                        "type": "string",
                        "description": "Filter by HCP name",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum results to return",
                    },
                },
                "required": ["query"],
            },
        },
        {
            "name": "summarize_interaction",
            "description": "Add an AI-generated summary to an interaction.",
            "callable": executor.summarize_interaction,
            "schema": {
                "type": "object",
                "properties": {
                    "interaction_id": {
                        "type": "string",
                        "description": "UUID of the interaction",
                    },
                    "summary": {
                        "type": "string",
                        "description": "Summary text to add",
                    },
                },
                "required": ["interaction_id", "summary"],
            },
        },
        {
            "name": "suggest_followups",
            "description": "Add suggested follow-up actions to an interaction.",
            "callable": executor.suggest_followups,
            "schema": {
                "type": "object",
                "properties": {
                    "interaction_id": {
                        "type": "string",
                        "description": "UUID of the interaction",
                    },
                    "followup_actions": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "action": {"type": "string"},
                                "due_date": {"type": "string"},
                                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                            },
                        },
                        "description": "List of follow-up actions",
                    },
                },
                "required": ["interaction_id", "followup_actions"],
            },
        },
    ]
