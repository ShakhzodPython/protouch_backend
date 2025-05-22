from django.contrib import admin

from .models import Customer

# Register your models here.


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ["id", "display_contact", "is_superuser", "date_joined"]

    def display_contact(self, obj):
        return obj.email if obj.email else obj.phone_number

    display_contact.short_description = "Email/Phone"
