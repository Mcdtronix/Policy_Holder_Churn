"""
Admin Configuration for Nyaradzo Assurance Management System
=========================================================
Professional Django admin configuration with proper
organization, search, filtering, and custom displays.

Author: Nyaradzo Engineering Team
Version: 1.0.0
"""

from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Sum, Count, Avg

from . import models


# ─────────────────────────────────────────────
# INLINE ADMIN CLASSES
# ─────────────────────────────────────────────

class PolicyDocumentInline(admin.TabularInline):
    """Inline policy documents."""
    model = models.PolicyDocument
    extra = 0
    readonly_fields = ('uploaded_by', 'uploaded_at')
    fields = ('doc_type', 'title', 'file', 'uploaded_by', 'uploaded_at')


class ClaimDocumentInline(admin.TabularInline):
    """Inline claim documents."""
    model = models.ClaimDocument
    extra = 0
    readonly_fields = ('uploaded_by', 'uploaded_at')
    fields = ('doc_type', 'title', 'file', 'uploaded_by', 'uploaded_at')


class ClaimNoteInline(admin.TabularInline):
    """Inline claim notes."""
    model = models.ClaimNote
    extra = 0
    readonly_fields = ('author', 'created_at')
    fields = ('author', 'body', 'created_at')


class PaymentAllocationInline(admin.TabularInline):
    """Inline payment allocations."""
    model = models.PaymentAllocation
    extra = 0
    fields = ('premium_schedule', 'amount_allocated')


class ChurnPredictionFeatureInline(admin.TabularInline):
    """Inline churn prediction features."""
    model = models.ChurnPredictionFeature
    extra = 0
    readonly_fields = ('prediction',)
    fields = ('feature_name', 'feature_value', 'feature_type')


# ─────────────────────────────────────────────
# REFERENCE TABLE ADMIN
# ─────────────────────────────────────────────

@admin.register(models.Gender)
class GenderAdmin(admin.ModelAdmin):
    list_display = ('code', 'label')
    search_fields = ('code', 'label')
    ordering = ('code',)


@admin.register(models.Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'district', 'province')
    search_fields = ('city', 'district', 'province')
    list_filter = ('province', 'district')
    ordering = ('city', 'district', 'province')


@admin.register(models.IncomeLevel)
class IncomeLevelAdmin(admin.ModelAdmin):
    list_display = ('label', 'code', 'min_usd', 'max_usd')
    search_fields = ('label', 'code')
    ordering = ('min_usd',)


@admin.register(models.PolicyType)
class PolicyTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active')
    search_fields = ('name', 'code', 'description')
    list_filter = ('is_active',)
    ordering = ('name',)


@admin.register(models.PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('label', 'code')
    search_fields = ('label', 'code')
    ordering = ('label',)


@admin.register(models.RiskLevel)
class RiskLevelAdmin(admin.ModelAdmin):
    list_display = ('label', 'code', 'min_threshold', 'max_threshold', 'color_display')
    search_fields = ('label', 'code')
    ordering = ('min_threshold',)
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
            obj.color_hex,
            obj.label
        )
    color_display.short_description = 'Color'


# ─────────────────────────────────────────────
# USER MANAGEMENT ADMIN
# ─────────────────────────────────────────────

@admin.register(models.User)
class UserAdmin(admin.ModelAdmin):
    """Professional user management with proper password hashing and reset functionality."""
    
    form = UserChangeForm
    add_form = UserCreationForm
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'department', 'is_active', 'date_joined')
    list_filter = ('role', 'department', 'is_active', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'created_at', 'updated_at', 'last_login')
    
    # Fieldsets for editing existing users
    fieldsets = (
        ('Personal Information', {
            'fields': ('username', 'email', 'first_name', 'last_name')
        }),
        ('Password', {
            'fields': ('password',),
            'description': 'Raw passwords are not stored, so there is no way to see this user\'s password. '
                          'However, you can use <a href=\"../password/\">this form</a> to change the password.'
        }),
        ('Role & Department', {
            'fields': ('role', 'department', 'phone')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Audit', {
            'fields': ('date_joined', 'created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        })
    )
    
    # Fieldsets for creating new users
    add_fieldsets = (
        ('Create New User', {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        }),
        ('Role & Department', {
            'fields': ('role', 'department', 'phone', 'is_active', 'is_staff')
        }),
    )
    
    def get_fieldsets(self, request, obj=None):
        """Use add_fieldsets when creating a new user, fieldsets when editing."""
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
    
    def get_form(self, request, obj=None, **kwargs):
        """Use UserCreationForm for new users, UserChangeForm for existing users."""
        if obj is None:
            self.form = self.add_form
        else:
            self.form = UserChangeForm
        return super().get_form(request, obj, **kwargs)
    
    def save_model(self, request, obj, form, change):
        """Ensure password is properly hashed when saving."""
        if not change:
            # New user creation - set_password handles hashing
            obj.set_password(form.cleaned_data['password1'])
        else:
            # Existing user
            if form.cleaned_data.get('password'):
                # Password was changed - handle hashing
                obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


# ─────────────────────────────────────────────
# CUSTOMER ADMIN
# ─────────────────────────────────────────────

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_number', 'full_name', 'email', 'gender', 'location', 'is_active', 'created_at')
    list_filter = ('gender', 'location', 'income_level', 'is_active')
    search_fields = ('customer_number', 'first_name', 'last_name', 'email', 'national_id')
    ordering = ('-created_at',)
    readonly_fields = ('customer_number', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Identity', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'national_id')
        }),
        ('Demographics', {
            'fields': ('gender', 'location', 'income_level')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_primary', 'phone_secondary', 'address_line1', 'address_line2')
        }),
        ('Status', {
            'fields': ('is_active', 'registered_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Full Name'


# ─────────────────────────────────────────────
# POLICY ADMIN
# ─────────────────────────────────────────────

@admin.register(models.Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'customer_name', 'policy_type', 'status', 'premium_amount', 'start_date', 'is_active')
    list_filter = ('policy_type', 'status', 'start_date')
    search_fields = ('policy_number', 'customer__first_name', 'customer__last_name')
    ordering = ('-created_at',)
    readonly_fields = ('policy_number', 'created_at', 'updated_at')
    inlines = [PolicyDocumentInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('customer', 'policy_type', 'underwritten_by')
        }),
        ('Policy Terms', {
            'fields': ('start_date', 'end_date', 'sum_assured', 'premium_amount', 'premium_frequency', 'dependents')
        }),
        ('Status & Notes', {
            'fields': ('status', 'notes')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_name(self, obj):
        return obj.customer.full_name if obj.customer else 'N/A'
    customer_name.short_description = 'Customer'
    
    def is_active(self, obj):
        return obj.status == models.Policy.Status.ACTIVE
    is_active.boolean = True
    is_active.short_description = 'Active'


# ─────────────────────────────────────────────
# CLAIM ADMIN
# ─────────────────────────────────────────────

@admin.register(models.Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'customer_name', 'claim_type', 'status', 'amount_claimed', 'event_date', 'assigned_officer')
    list_filter = ('claim_type', 'status', 'event_date')
    search_fields = ('claim_number', 'policy__policy_number', 'policy__customer__first_name')
    ordering = ('-reported_date',)
    readonly_fields = ('claim_number', 'reported_date', 'created_at', 'updated_at')
    inlines = [ClaimDocumentInline, ClaimNoteInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('policy', 'claim_type', 'status', 'assigned_officer')
        }),
        ('Event Details', {
            'fields': ('event_date', 'description')
        }),
        ('Financial Information', {
            'fields': ('amount_claimed', 'amount_approved', 'amount_settled')
        }),
        ('Resolution', {
            'fields': ('rejection_reason', 'settled_at')
        }),
        ('Audit', {
            'fields': ('reported_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_name(self, obj):
        return obj.policy.customer.full_name if obj.policy else 'N/A'
    customer_name.short_description = 'Customer'


# ─────────────────────────────────────────────
# PAYMENT ADMIN
# ─────────────────────────────────────────────

@admin.register(models.Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_reference', 'customer_name', 'category', 'status', 'amount', 'transaction_date', 'processed_by')
    list_filter = ('payment_method', 'category', 'status', 'transaction_date')
    search_fields = ('payment_reference', 'policy__policy_number', 'policy__customer__first_name')
    ordering = ('-transaction_date',)
    readonly_fields = ('payment_reference', 'created_at', 'updated_at')
    inlines = [PaymentAllocationInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('policy', 'claim', 'payment_method', 'category')
        }),
        ('Financial Details', {
            'fields': ('amount', 'currency', 'status')
        }),
        ('Transaction Details', {
            'fields': ('transaction_date', 'external_ref', 'notes', 'processed_by')
        }),
        ('Audit', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def customer_name(self, obj):
        return obj.policy.customer.full_name if obj.policy else 'N/A'
    customer_name.short_description = 'Customer'


# ─────────────────────────────────────────────
# CUSTOMER ENGAGEMENT ADMIN
# ─────────────────────────────────────────────

@admin.register(models.CustomerEngagement)
class CustomerEngagementAdmin(admin.ModelAdmin):
    list_display = ('customer', 'number_of_complaints', 'claims_filed', 'service_satisfaction', 'last_interaction_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__customer_number')
    ordering = ('-updated_at',)
    readonly_fields = ('updated_at',)


# ─────────────────────────────────────────────
# CHURN PREDICTION ADMIN
# ─────────────────────────────────────────────

@admin.register(models.ChurnBatchJob)
class ChurnBatchJobAdmin(admin.ModelAdmin):
    list_display = ('id', 'model_version', 'status', 'total_customers', 'processed', 'triggered_by', 'started_at', 'completed_at')
    list_filter = ('status', 'model_version', 'started_at')
    search_fields = ('triggered_by__username', 'model_version')
    ordering = ('-started_at',)
    readonly_fields = ('id',)
    
    def has_predictions(self, obj):
        count = obj.predictions.count()
        url = reverse('admin:churn_churnprediction_changelist') + f'?batch_job__id__exact={obj.id}'
        return format_html('<a href="{}">{} predictions</a>', url, count)
    has_predictions.short_description = 'Predictions'


@admin.register(models.ChurnPrediction)
class ChurnPredictionAdmin(admin.ModelAdmin):
    list_display = ('customer', 'risk_level', 'churn_percentage', 'is_churned', 'model_version', 'predicted_at')
    list_filter = ('risk_level', 'is_churned', 'predicted_at')
    search_fields = ('customer__first_name', 'customer__last_name', 'customer__customer_number')
    ordering = ('-predicted_at',)
    readonly_fields = ('model_version', 'predicted_at')
    inlines = [ChurnPredictionFeatureInline]
    
    fieldsets = (
        ('Prediction Details', {
            'fields': ('customer', 'batch_job', 'risk_level', 'churn_percentage', 'is_churned')
        }),
        ('Model Information', {
            'fields': ('model_version', 'predicted_at'),
            'classes': ('collapse',)
        })
    )
    
    def churn_percentage_display(self, obj):
        color = 'red' if obj.churn_percentage >= 70 else 'orange' if obj.churn_percentage >= 40 else 'green'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            obj.churn_percentage
        )
    churn_percentage_display.short_description = 'Churn %'


# ─────────────────────────────────────────────
# PREMIUM SCHEDULE ADMIN
# ─────────────────────────────────────────────

@admin.register(models.PremiumSchedule)
class PremiumScheduleAdmin(admin.ModelAdmin):
    list_display = ('policy', 'due_date', 'amount_due', 'is_paid', 'is_late')
    list_filter = ('is_paid', 'is_late', 'due_date')
    search_fields = ('policy__policy_number', 'policy__customer__first_name')
    ordering = ('due_date',)
    
    def policy_display(self, obj):
        return obj.policy.policy_number
    policy_display.short_description = 'Policy'


# ─────────────────────────────────────────────
# DOCUMENT ADMIN
# ─────────────────────────────────────────────

@admin.register(models.PolicyDocument)
class PolicyDocumentAdmin(admin.ModelAdmin):
    list_display = ('policy', 'doc_type', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('policy__policy_number', 'title')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(models.ClaimDocument)
class ClaimDocumentAdmin(admin.ModelAdmin):
    list_display = ('claim', 'doc_type', 'title', 'uploaded_by', 'uploaded_at')
    list_filter = ('doc_type', 'uploaded_at')
    search_fields = ('claim__claim_number', 'title')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(models.ClaimNote)
class ClaimNoteAdmin(admin.ModelAdmin):
    list_display = ('claim', 'author', 'body_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('claim__claim_number', 'body', 'author__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    
    def body_preview(self, obj):
        return obj.body[:50] + '...' if len(obj.body) > 50 else obj.body
    body_preview.short_description = 'Note'


# ─────────────────────────────────────────────
# PAYMENT ALLOCATION ADMIN
# ─────────────────────────────────────────────

@admin.register(models.PaymentAllocation)
class PaymentAllocationAdmin(admin.ModelAdmin):
    list_display = ('payment', 'premium_schedule', 'amount_allocated')
    search_fields = ('payment__payment_reference', 'premium_schedule__policy__policy_number')
    ordering = ('-payment__transaction_date',)


@admin.register(models.ChurnPredictionFeature)
class ChurnPredictionFeatureAdmin(admin.ModelAdmin):
    list_display = ('prediction', 'feature_name', 'feature_value', 'feature_type')
    list_filter = ('feature_type', 'prediction__predicted_at')
    search_fields = ('prediction__customer__first_name', 'feature_name')
    ordering = ('prediction__predicted_at', 'feature_name')
    readonly_fields = ('prediction',)


# ─────────────────────────────────────────────
# ADMIN CUSTOMIZATION
# ─────────────────────────────────────────────

# Customize admin site
admin.site.site_header = 'Nyaradzo Assurance Management System'
admin.site.site_title = 'Nyaradzo Admin'
admin.site.index_title = 'Welcome to Nyaradzo Administration'

# Customize admin site URLs
admin.site.site_url = '/admin/'
