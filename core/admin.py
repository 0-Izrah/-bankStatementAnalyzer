from django.contrib import admin
from .models import UploadedFile, Transaction

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bank_name', 'uploaded_at', 'processed')
    list_filter = ('bank_name', 'processed', 'uploaded_at')
    search_fields = ('user__username', 'bank_name')

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'description', 'amount', 'category', 'balance')
    list_filter = ('category', 'date')
    search_fields = ('description',)