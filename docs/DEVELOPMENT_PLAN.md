# Raha Development Plan

## 1. Structural Alignment
The project follows a modern Django layout with apps isolated in an `apps/` directory. 
- `apps.accounts`: Custom Auth (Phone/Password)
- `apps.models_app`: Core domain (Models, Services, Locations)

## 2. TDD Approach
Behavioral tests will be written using `pytest` and `Django TestCase`.
**Key Behaviors to Test:**
- User registration creates a valid user with phone as username.
- Model onboarding requires compulsory fields (name, pfp, primary location).
- Optional face blurring correctly modifies the image buffer using OpenCV before storage.
- M2M relations for locations and services are correctly persisted.
- Model profiles are publicly listable (when active) and detail views include a protected gallery.
- **Verification System**: Service layer for verifying or rejecting profiles, ensuring only verified profiles become active.

## 3. Security Check
- `.env` is ignored. 
- Using `django-environ` for secret management.
- GCP Secret Manager to be integrated for production.
- CSRF protection enabled for all POST/HTMX requests.

## 4. Infra Impact
- `Dockerfile` and `docker-compose.yml` for local development and containerization.
- CircleCI configuration for automated testing and GCP deployment.

## 5. System Design
- **Architecture**: Monolithic Django with HTMX for interactivity.
- **Domain Driven**: Using "Model" and "Location" as ubiquitous language.
- **Service Layer**: Image processing (blurring) extracted to a separate service for OCP compliance.

## 6. Scaling
- Horizontal scaling via Docker containers.
- Media assets offloaded to S3/GCS.
- Database scaling via Cloud SQL (PostgreSQL).
