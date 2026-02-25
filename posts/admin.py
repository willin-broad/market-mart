from django.contrib import admin

from .models import Post, Comment, Like, Dislike 

# class PostAdmin(admin.ModelAdmin):
#     # List of fields to display in the admin list view
#     list_display = ('description', 'user', 'created_at', 'image_preview')
    
#     # Optional: Add filters and search fields
#     list_filter = ('user', 'created_at')  # Filter by user or creation date
#     search_fields = ('description', 'user__username')  # Search by description or username

#     # Optional: If you want to preview the image in the admin interface
#     def image_preview(self, obj):
#         return f'<img src="{obj.image.url}" width="100" height="100" />'  # Modify size as needed
#     image_preview.allow_tags = True  # Allow HTML to render the image

# Register the Post model with the custom PostAdmin
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Dislike)
