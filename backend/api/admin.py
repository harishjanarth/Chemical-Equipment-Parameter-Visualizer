from django.contrib import admin

class DatasetAdmin(admin.ModelAdmin):
    list_display = ('id', 'uploader', 'uploaded_at')
    readonly_fields = ('uploaded_at',)
