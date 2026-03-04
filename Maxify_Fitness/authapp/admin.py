from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils import timezone
from datetime import timedelta

from authapp.models import (
    Contact, MembershipPlan, Trainer, Enrollment, Gallery,
    Attendance, Service, WorkoutPlan, UserMembership, PaystackConfiguration
)

# ----- Basic Models -----
admin.site.register(Contact)
admin.site.register(MembershipPlan)
admin.site.register(Trainer)
admin.site.register(Enrollment)
admin.site.register(Gallery)
admin.site.register(Attendance)
admin.site.register(Service)


# ----- WorkoutPlan Admin -----
@admin.register(WorkoutPlan)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('title', 'membership_level')
    search_fields = ('title',)


# ----- UserMembership Admin -----
@admin.register(UserMembership)
class UserMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan_name', 'expiry_date', 'colored_status')
    search_fields = ('user__username', 'plan_name')
    list_filter = ('is_active',)

    def colored_status(self, obj):
        if obj.is_active and not obj.has_expired:
            return mark_safe('<span style="color:green; font-weight:bold;">Active</span>')
        return mark_safe('<span style="color:red; font-weight:bold;">Expired</span>')

    colored_status.short_description = 'Status'

    def changelist_view(self, request, extra_context=None):
        """Add extra summary stats to the admin dashboard"""
        qs = self.get_queryset(request)
        extra_context = extra_context or {}

        total_revenue = sum([m.amount_paid or 0 for m in qs])
        active_members = qs.filter(is_active=True, expiry_date__gte=timezone.now()).count()
        expiring_soon = qs.filter(
            is_active=True,
            expiry_date__gte=timezone.now(),
            expiry_date__lte=timezone.now() + timedelta(days=7)
        ).count()

        extra_context.update({
            "total_revenue": total_revenue,
            "active_members": active_members,
            "expiring_soon": expiring_soon,
        })

        return super().changelist_view(request, extra_context=extra_context)


# ----- Paystack Configuration Admin -----
@admin.register(PaystackConfiguration)
class PaystackConfigAdmin(admin.ModelAdmin):
    list_display = ('secret_key', 'is_active')

    # Prevent adding multiple configurations
    def has_add_permission(self, request):
        if PaystackConfiguration.objects.exists():
            return False
        return True