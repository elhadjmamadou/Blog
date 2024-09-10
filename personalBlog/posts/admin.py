from django.contrib import admin
from .models import BlogPost,Category,Tag


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "published", "created_on", "last_update",)
    list_editable = ("published", )

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)



admin.site.register(Tag,TagAdmin)
admin.site.register(Category,CategoryAdmin)
admin.site.register(BlogPost,BlogPostAdmin)
