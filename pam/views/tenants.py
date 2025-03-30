from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pam.models import Tenant

@login_required
def tenants_view(request):

    hide_fields = ['updated_at', 'created_at', 'id']

    objects = Tenant.objects.all()
    fields = Tenant._meta.fields
    field_names = [field.name for field in fields if field.name not in hide_fields]
    verbose_names = [field.verbose_name for field in fields if field.name not in hide_fields]

    content = {
        'title': 'tenants',
        'heading': 'tenants',
        'active_page': 'tenants',
        'objects': objects,
        'field_names': field_names,
        'verbose_names': verbose_names,
    }

    return render(request, 'tenants.html', content)