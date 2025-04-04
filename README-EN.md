# FryPAM

FryPAM is a Privileged Access Management system for cloud environments, providing secure, controlled access to cloud accounts across different providers.

## Features

- Multi-tenant support for managing different organizational units
- User management with multiple roles (Admin, User, Validator)
- Support for multiple cloud providers:
  - Amazon Web Services (AWS)
  - Microsoft Azure (WIP)
  - Google Cloud Platform (GCP) (WIP)
  - Oracle Cloud Infrastructure (OCI)(WIP)
- Password request workflow with approval process
- Time-limited access windows
- Docker support for both development and production environments

## Architecture and Workflow

```
                                       ┌───────────────┐
                                       │               │
                                       │     User      │
                                       │   Interface   │
                                       │   (Django)    │
                                       │               │
                                       └───────┬───────┘
                                               │
                                               ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                         FryPAM System                                 │
│                                                                       │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐      │
│   │               │     │               │     │               │      │
│   │     User      │---->│    Access     │---->│   Temporary   │      │
│   │  Validation   │     │   Approval    │     │     Access    │      │
│   │               │     │               │     │               │      │
│   └───────────────┘     └───────────────┘     └───────┬───────┘      │
│                                                       │               │
└───────────────────────────────────────────────────────┼───────────────┘
                                                        │
                                                        ▼
┌───────────────────────────────────────────────────────────────────────┐
│                                                                       │
│                     Cloud Providers                                   │
│                                                                       │
│   ┌───────────────┐     ┌───────────────┐     ┌───────────────┐      │
│   │    AWS        │     │  Azure (WIP)  │     │   GCP (WIP)   │      │
│   │   ACTIVE      │     │    Future     │     │    Future     │      │
│   │     ✓         │     │               │     │               │      │
│   └───────────────┘     └───────────────┘     └───────────────┘      │
│                                                                       │
│                         ┌───────────────┐                             │
│                         │  OCI (WIP)    │                             │
│                         │    Future     │                             │
│                         │               │                             │
│                         └───────────────┘                             │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

### Access Request Workflow

1. **Request**: User requests access to a specific AWS account
2. **Validation**: The validator (responsible person) reviews and approves the request
3. **Approval**: The system grants temporary access to the requested account
4. **Usage**: The user accesses the account during the approved time period
5. **Expiration**: At the end of the period, access is automatically revoked

> **Note**: In the current version, only AWS integration is fully implemented. Integrations with Azure, GCP, and OCI are planned for future releases.

## Requirements

- Python 3.x
- Django 5.1
- Docker and Docker Compose (optional, for containerized deployment)

## Installation

### Local Development Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-org/FryPAM.git
   cd FryPAM
   ```

2. Create a virtual environment and install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   make migrations
   ```

4. Create a superuser:
   ```
   make superuser
   ```

5. Start the development server:
   ```
   make start
   ```

### Docker Setup

1. Build and start the containers:
   ```
   docker-compose up -d
   ```

2. Run migrations inside the container:
   ```
   docker-compose exec web python manage.py migrate
   ```

3. Create a superuser inside the container:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

## Usage

Access the application at:
- Local development: http://localhost:8000/
- Development server: https://FryPAM-dev.pavops.net/

Log in with your admin credentials to:
- Manage users and assign roles
- Configure tenants and cloud accounts
- Process password requests

## Development

### Available Make Commands

- `make help` - Show available commands
- `make migrations` - Run database migrations
- `make start` - Start the development server
- `make test` - Run tests
- `make full_start` - Run migrations and start the server
- `make superuser` - Create a superuser account

## License

[Your License Here]

## Contact

[Your Contact Information]
