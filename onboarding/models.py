import uuid 
from django.db import models
from django.utils.translation import gettext_lazy as _

class Contact(models.Model):
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
        ('', _('Let us know your industry')),
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
        verbose_name=_('Industry'),
    )
    email = models.EmailField(
        max_length = 254, 
        blank=True, 
        null=True, 
        verbose_name=_('Email'),
    )
    mailing_list = models.BooleanField(blank=True, default=False)
    sales_contact = models.BooleanField(blank=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    usm_simple_download_uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False) 
    usm_simple_requested = models.BooleanField(default=False)
    usm_simple_sent_at = models.DateTimeField(blank=True, null=True)
