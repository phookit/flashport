from django.contrib import admin

class OwnableAdmin(admin.ModelAdmin):
    def save_form(self, request, form, change):
        obj = form.save(commit=False)
        if obj.user_id is None:
            obj.user = request.user
        return super(OwnableAdmin, self).save_form(request, form, change)

