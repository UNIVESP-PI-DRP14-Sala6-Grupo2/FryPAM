from django.http import JsonResponse
from django.core import serializers
from cofre.models import Tenant
import json


def get_tenants(request):

    tenants = Tenant.objects.all()
    tenant_data = serializers.serialize('json', tenants)
    tenant_data = json.loads(tenant_data)

    # Convert serialized data to a cleaner format
    simplified_data = []
    for item in tenant_data:
        tenant_dict = item['fields']
        tenant_dict['id'] = item['pk']  # Add the primary key
        simplified_data.append(tenant_dict)

    return JsonResponse(simplified_data, safe=False)

def get_tenant_by_id(request, tenant_id):

    tenant = Tenant.objects.get(pk=tenant_id)

    tenant_data = serializers.serialize('json', [tenant])
    tenant_data = json.loads(tenant_data)
    tenant_dict = tenant_data[0]['fields']
    tenant_dict['id'] = tenant_data[0]['pk']

    return JsonResponse(tenant_dict, safe=False)
