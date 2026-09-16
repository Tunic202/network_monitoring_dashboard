# Network Monitoring Dashboard

A Django-based network monitoring dashboard for tracking network devices, interface status, system information, and monitoring health.

The project was built as a networking and Python portfolio project, combining Django, PostgreSQL, Bootstrap, automated testing, and an SNMP monitoring architecture.

## Features

- Network device management
- Add and edit devices through the web interface
- Device detail pages
- Device IP address and device-type information
- Device location tracking
- Online, offline, and unknown device states
- Last seen timestamp
- Last checked timestamp
- System information
- Interface monitoring
- Interface operational status
- Mock monitoring provider for development and testing
- SNMP monitoring provider using PySNMP
- SNMP interface discovery
- SNMP interface operational-status handling
- SNMP error and timeout handling
- Provider selection through environment configuration
- PostgreSQL database
- Django Admin integration
- Responsive Bootstrap interface
- Automated Django test suite
- Production-oriented security configuration
- Gunicorn application server configuration
- Upsun deployment configuration

## Technology Stack

### Backend

- Python 3.11 for local development
- Django 5.2
- PostgreSQL
- Gunicorn

### Networking

- PySNMP
- SNMP v2c / v3 configuration
- IF-MIB interface monitoring
- SNMP device system information

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- django-bootstrap5

### Testing

- Django TestCase
- Mocked SNMP responses
- Provider-level tests
- Dashboard and view tests
- Device management tests

### Deployment

- Upsun configuration
- PostgreSQL service configuration
- Environment-based production settings

## Application Architecture

The application uses a provider-based monitoring architecture.

```text
                    Django Dashboard
                           |
                           v
                  Monitoring Service
                           |
                           v
                 Monitoring Provider
                    /             \
                   /               \
                  v                 v
        MockMonitoringProvider   SNMPMonitoringProvider
                  |                 |
                  v                 v
             Mock data           PySNMP
                                      |
                                      v
                              Network Device
