from django.core.exceptions import ValidationError

from messaging.domain.selectors.user_selectors import (
    get_admin_user,
)

from messaging.domain.constants.contact_constants import (
    ContactInquiryType,
)

from messaging.domain.services.conversation_service import (
    ConversationService,
)

from messaging.domain.services.message_service import (
    MessageService,
)


class ContactService:

    @staticmethod
    def send_contact_message(
        *,
        sender,
        inquiry_type,
        message,
    ):

        admin = get_admin_user()

        if admin is None:
            raise ValidationError(
                "No admin user found."
            )

        conversation = (
            ConversationService.start_private_conversation(
                creator=sender,
                target_user=admin,
            )
        )

        if not conversation.title:

            conversation.title = "تواصل معنا"

            conversation.save(
                update_fields=[
                    "title",
                    "updated_at",
                ]
            )

        formatted_message = (
            f" نوع الاستفسار : "
            f"{ContactInquiryType.get_label(inquiry_type)}"
            f"\n\n"
            f"{message.strip()}"
        )

        MessageService.send_message(
            conversation=conversation,
            sender=sender,
            content=formatted_message,
        )

        return conversation