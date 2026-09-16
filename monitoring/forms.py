from django import forms

from .models import Device


class DeviceForm(forms.ModelForm):
    """Form for creating and editing network devices."""

    class Meta:
        model = Device
        fields = [
            "name",
            "ip_address",
            "device_type",
            "snmp_version",
            "location",
            "enabled",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "ip_address": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "device_type": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "snmp_version": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": "form-control",
                }
            ),
            "enabled": forms.CheckboxInput(
                attrs={
                    "class": "form-check-input",
                }
            ),
        }
