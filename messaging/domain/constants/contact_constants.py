class ContactInquiryType:

    GENERAL = "GENERAL"
    INCUBATOR = "INCUBATOR"
    VOLUNTEERING = "VOLUNTEERING"
    INVESTMENT = "INVESTMENT"
    TECHNICAL = "TECHNICAL"

    CHOICES = (
        (GENERAL, "عام"),
        (INCUBATOR, "حول خدمات الحاضنة"),
        (VOLUNTEERING, "التطوع / الإرشاد"),
        (INVESTMENT, "الاستثمار / الشراكة"),
        (TECHNICAL, "مشكلة تقنية"),
    )

    LABELS = {
        GENERAL: "عام",
        INCUBATOR: "حول خدمات الحاضنة",
        VOLUNTEERING: "التطوع / الإرشاد",
        INVESTMENT: "الاستثمار / الشراكة",
        TECHNICAL: "مشكلة تقنية",
    }

    @classmethod
    def get_label(cls, value):
        return cls.LABELS.get(value, value)