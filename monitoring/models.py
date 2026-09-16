from django.db import models


class Device(models.Model):
    """Store network device information."""

    DEVICE_TYPES = [
        ("cisco_ios", "Cisco IOS"),
        ("cisco_nxos", "Cisco NX-OS"),
        ("linux", "Linux"),
        ("other", "Other"),
    ]

    name = models.CharField(max_length=100)

    ip_address = models.GenericIPAddressField(
        unique=True,
    )

    device_type = models.CharField(
        max_length=50,
        choices=DEVICE_TYPES,
        default="cisco_ios",
    )

    snmp_version = models.CharField(
        max_length=10,
        choices=[
            ("2c", "SNMP v2c"),
            ("3", "SNMP v3"),
        ],
        default="2c",
    )

    snmp_community = models.CharField(
        max_length=100,
        blank=True,
    )

    location = models.CharField(
        max_length=100,
        blank=True,
    )

    enabled = models.BooleanField(
        default=True,
    )

    last_seen = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return self.name


class Interface(models.Model):
    """Store network interface information."""

    device = models.ForeignKey(
        Device,
        on_delete=models.CASCADE,
        related_name="interfaces",
    )

    name = models.CharField(
        max_length=100,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    status = models.CharField(
        max_length=50,
        default="unknown",
    )

    last_checked = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.device.name} - {self.name}"
