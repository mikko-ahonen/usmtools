import uuid
from django.conf import settings
from django.db import models
from django_countries.fields import CountryField
from django.utils.translation import gettext_lazy as _

from workflows.models import Account

class Question(models.PositiveSmallIntegerField):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class USMSurvey(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    DEFAULT_CHOICES = [
        (1, _("Never")),
        (2, _("Rarely")),
        (3, _("Sometimes")),
        (4, _("Neutral")),
        (5, _("Often")),
        (6, _("Usually")),
         (7, _("Always")),
    ]

    REVERSE_CHOICES = [
        (1, _("Always")),
        (2, _("Usually")),
        (3, _("Often")),
        (4, _("Neutral")),
        (5, _("Sometimes")),
        (6, _("Rarely")),
         (7, _("Never")),
    ]

    proactive = Question(help_text=_('We manage improvements in a proactive way'), choices=DEFAULT_CHOICES, verbose_name='Proactive improvements')

    documentation = Question(help_text=_('The ways we work (our daily routines) are adequately documented'), choices=DEFAULT_CHOICES, verbose_name='Documentation')

    tooling = Question(help_text=_('The ways we work (our daily routines) are automated with adequate tooling where possible'), choices=DEFAULT_CHOICES, verbose_name='Tooling')

    internal_reporting  = Question(help_text=_('The reporting of service quality in my organization is good'), choices=DEFAULT_CHOICES, verbose_name='Internal reporting')

    responsibilities = Question(help_text=_('We have issues arising from unclear roles and responsibilities, or ownership'), choices=REVERSE_CHOICES, verbose_name='Roles and responsibilities')

    request = Question(help_text=_('We solve most of the customer requests as agreed'), choices=DEFAULT_CHOICES, verbose_name='Customer requests')

    reporting = Question(help_text=_('Our service reporting fully supports the expectations of our customers'), choices=DEFAULT_CHOICES, verbose_name='Customer reporting')

    compliance = Question(help_text=_('We have difficulties to comply with one or more required industry standards (ISO 9k, ISO 27k, ISO 13k etc.)'), choices=REVERSE_CHOICES, verbose_name='Standard compliance')

    employee = Question(help_text=_('Our employees are satisfied with the way we organize our work'), choices=DEFAULT_CHOICES, verbose_name='Employees')

    supplier = Question(help_text=_('We encounter problems with our supplier relationships, impacting our product/service quality'), choices=REVERSE_CHOICES, verbose_name='Suppliers')

    services = Question(help_text=_('Our services and related agreements are clearly specified'), choices=DEFAULT_CHOICES, verbose_name='Service and agreement specification')

    planning = Question(help_text=_('We are in control of our planning and our resources for the delivery of our services'), choices=DEFAULT_CHOICES, verbose_name='Planning')

    glossary = Question(help_text=_('We have a formalized and shared business glossary (definitions of terms) and it is actively used throughout the organization'), choices=DEFAULT_CHOICES, verbose_name='Glossary')

    countries = CountryField(verbose_name=_('The countries where your organization operates'), multiple=True)

    LANGUAGE_DUTCH = 'nl'
    LANGUAGE_ENGLISH = 'en'
    LANGUAGE_FINNISH = 'fi'
    LANGUAGE_FRENCH = 'fr'
    LANGUAGE_GERMAN = 'de'
    LANGUAGE_SPANISH = 'es'

    LANGUAGE_CHOICES = [
        (LANGUAGE_DUTCH, _('Dutch')),
        (LANGUAGE_ENGLISH, _('English')),
        (LANGUAGE_FINNISH, _('Finnish')),
        (LANGUAGE_FRENCH, _('French')),
        (LANGUAGE_GERMAN, _('German')),
        (LANGUAGE_SPANISH, _('Spanish')),
    ]

    lang = models.CharField(
        max_length=2,
        choices=LANGUAGE_CHOICES,
        verbose_name=_('Your preferred language'),
    )

    INDUSTRY_AGRICULTURE_FORESTRY_MINING = 'agriculture-forestry-mining'
    INDUSTRY_INDUSTRIALS = 'industrials'
    INDUSTRY_ENERGY_UTILITIES = 'energy-utilities'
    INDUSTRY_TRANSPORT_LOGISTICS = 'transport-logistics'
    INDUSTRY_MEDIA_CREATIVE = 'media-creative'
    INDUSTRY_IT_DATA_INFRA_TELECOM = 'it-data-infra-telecom'
    INDUSTRY_HEALTHCARE = 'healthcare'
    INDUSTRY_EDUCATION = 'education'
    INDUSTRY_LIFE_SCIENCES = 'life-sciences'
    INDUSTRY_RETAIL_ECOMMERCE = 'retail-ecommerce'
    INDUSTRY_HOSPITALITY_FOOD_LEISURE_TRAVEL = 'hospitality-food-leisure-travel'
    INDUSTRY_PUBLIC_AND_SOCIAL_SERVICE = 'public-social-service'
    INDUSTRY_FINANCIAL_SERVICES = 'financial-services'
    INDUSTRY_PROFESSIONAL_SERVICES = 'professional-services'
    INDUSTRY_OTHER = 'other'

    INDUSTRY_CHOICES = [
        (INDUSTRY_AGRICULTURE_FORESTRY_MINING, _('Agriculture, Forestry, Mining')),
        (INDUSTRY_INDUSTRIALS, _('Industrials (Manufacturing, Construction, etc.)')),
        (INDUSTRY_ENERGY_UTILITIES, _('Energy, Utilities')),
        (INDUSTRY_TRANSPORT_LOGISTICS, _('Transport, Logistics')),
        (INDUSTRY_MEDIA_CREATIVE, _('Media, Creative Industries')),
        (INDUSTRY_IT_DATA_INFRA_TELECOM, _('Information Technology, Data Infrastructure, Telecom')),
        (INDUSTRY_HEALTHCARE, _('Healthcare')),
        (INDUSTRY_EDUCATION, _('Education')),
        (INDUSTRY_LIFE_SCIENCES, _('Life Sciences')),
        (INDUSTRY_RETAIL_ECOMMERCE, _('Retail, E-Commerce')),
        (INDUSTRY_HOSPITALITY_FOOD_LEISURE_TRAVEL, _('Hospitality, Food, Leisure Travel')),
        (INDUSTRY_PUBLIC_AND_SOCIAL_SERVICE, _('Public Service, Social Service')),
        (INDUSTRY_FINANCIAL_SERVICES, _('Financial Services')),
        (INDUSTRY_PROFESSIONAL_SERVICES, _('Professional Services (Law, Consulting, etc.)')),
        (INDUSTRY_OTHER, _('Other')),
    ]

    industry = models.CharField(
        max_length=32,
        choices=INDUSTRY_CHOICES,
        verbose_name=_('Industry of your organisation'),
    )

    SIZE_1 = '1'
    SIZE_2_5 = '2-5'
    SIZE_6_10 = '6-10'
    SIZE_11_50 = '11-50'
    SIZE_51_100 = '51-100'
    SIZE_101_500 = '101-500'
    SIZE_501_1000  = '501-1000'
    SIZE_1001_5000 = '1001-5000'
    SIZE_MORE_THAN_5000 = '5000-'

    SIZE_CHOICES = [
        (SIZE_1, SIZE_1),
        (SIZE_2_5, SIZE_2_5),
        (SIZE_6_10, SIZE_6_10),
        (SIZE_11_50, SIZE_11_50),
        (SIZE_51_100, SIZE_51_100),
        (SIZE_101_500, SIZE_101_500),
        (SIZE_501_1000, SIZE_501_1000),
        (SIZE_1001_5000, SIZE_1001_5000),
        (SIZE_MORE_THAN_5000, SIZE_MORE_THAN_5000),
    ]

    size = models.CharField(
        max_length=32,
        choices=SIZE_CHOICES,
        verbose_name=_('Size of your organisation'),
    )
    name = models.CharField(
        max_length=255,
        verbose_name=_('Organisation name'),
        null=True,
    )
    email = models.EmailField(
        max_length = 254, 
        blank=True, 
        null=True, 
        verbose_name=_('Email'),
    )
    report_ok = models.BooleanField(blank=True, default=False, verbose_name='I want to get a report by email')
    sales_ok = models.BooleanField(blank=True, default=False, verbose_name='USM professionals may contact me so we can go over our needs')

    created_at = models.DateTimeField(auto_now_add=True)

class Answer(models.Model):
    question = models.CharField(max_length=255, verbose_name=_('Question'))
    low = models.PositiveSmallIntegerField(verbose_name=_('Lowest option that matches'))
    high = models.PositiveSmallIntegerField(verbose_name=_('Highest option that matches'))
    text_en = models.TextField(verbose_name=_('Text (en)'), blank=True, null=True)


class Lead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, verbose_name=_('Name'))
    email = models.EmailField(max_length=255, verbose_name=_('Email'))
    organization = models.CharField(max_length=255, verbose_name=_('Orgnization name'))
    title = models.CharField(max_length=255, verbose_name=_('Your title'))
    rationale = models.TextField(verbose_name=_('Why do you wish to participate in the survey?'), blank=True, null=True)

    CATEGORY_C_LEVEL = 'c-level'
    CATEGORY_ITSM_PRO = 'itsm-pro'
    CATEGORY_OTHER = 'other'
    CATEGORY_REJECTED = 'rejected'

    CATEGORY_CHOICES = [
        (CATEGORY_C_LEVEL, "C-level"),
        (CATEGORY_ITSM_PRO, "ITSM pro"),
        (CATEGORY_OTHER, "Other"),
        (CATEGORY_REJECTED, "Rejected"),
    ]

    category = models.CharField(
        max_length=32,
        choices=CATEGORY_CHOICES,
        verbose_name=_('Category'),
    )

    STATUS_UNQUALIFIED = 'unqualified'
    STATUS_REJECTED = 'rejected'
    STATUS_FREE = 'free'
    STATUS_CLAIMED = 'claimed'

    STATUS_CHOICES = [
        (STATUS_UNQUALIFIED, "Unqualified"),
        (STATUS_REJECTED, "Rejected"),
        (STATUS_FREE, "Free"),
        (STATUS_CLAIMED, "Claimed"),
    ]

    status = models.CharField(
        max_length=32,
        choices=STATUS_CHOICES,
        verbose_name=_('Status'),
    )
