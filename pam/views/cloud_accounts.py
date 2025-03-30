from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from pam.models import CloudAccount

@login_required
def cloud_accounts_view(request):

    hide_fields = ['updated_at', 'created_at', 'id', 'last_used']
    environment_pills = {
        'dev': 'text-bg-primary',
        'stage': 'text-bg-warning',
        'prod': 'text-bg-danger',
    }


    objects = CloudAccount.objects.all()
    fields = CloudAccount._meta.fields
    field_names = [field.name for field in fields if field.name not in hide_fields]
    verbose_names = [field.verbose_name for field in fields if field.name not in hide_fields]

    content = {
        'title': 'Cloud Accounts',
        'heading': 'Cloud Accounts',
        'active_page': 'cloud_accounts',
        'objects': objects,
        'field_names': field_names,
        'verbose_names': verbose_names,
        'environment_pills': environment_pills,
    }
    return render(request, 'cloud_accounts.html', content)