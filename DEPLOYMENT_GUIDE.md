# Elastic Beanstalk Deployment (Clean Slate)# AWS Elastic Beanstalk Deployment Guide



This repository now ships with everything you need to deploy the Django API on **AWS Elastic Beanstalk (Docker on AL2023)**. Follow the workflow below whenever you need to provision or redeploy the production environment.## What You'll Get



---- Automatic server management and scaling

- Load balancer (supports HTTPS)

## 1. Prerequisites- PostgreSQL database (RDS)

- Health monitoring and logs

- AWS account with permissions to manage Elastic Beanstalk, EC2, RDS, IAM, and S3- Zero-downtime deployments

- `uv` CLI installed locally (https://github.com/astral-sh/uv)- Easy environment variable management

- AWS credentials configured locally (`aws configure`)

- (Optional) SSH key pair if you want shell access to EC2 instances---



> **EB CLI via `uv`:** All of the commands below use `uv run eb …`. `uv` will download the Elastic Beanstalk CLI on demand, so you do not need to install it globally.## Step-by-Step Setup



---### 1. Install Prerequisites



## 2. Initialize Elastic Beanstalk for this project```bash

# Install AWS EB CLI using uv (adds to project dependencies)

```bashuv add awsebcli --dev

uv run eb init

# Region: eu-north-1# Verify installation

# Platform: Docker running on 64bit Amazon Linux 2023uv run eb --version

# Application: fl-backend```

# Enable SSH (recommended)

```### 2. Configure AWS Credentials



This creates `.elasticbeanstalk/config.yml`. Keep it out of commits.```bash

# Configure AWS CLI (if not already done)

---aws configure



## 3. Create the production environment + RDS# Enter your:

# - AWS Access Key ID

```bash# - AWS Secret Access Key

uv run eb create fl-backend-prod \# - Default region: eu-north-1

  --platform "Docker running on 64bit Amazon Linux 2023" \# - Default output format: json

  --instance-type t3.micro \```

  --database.engine postgres \

  --database.instance db.t3.micro \### 3. Initialize Elastic Beanstalk in Your Project

  --database.username <db-user> \

  --database.password <db-password> \```bash

  --database.size 20cd /Users/keewee/workspace/keewee/fl-backend

```

# Initialize EB application

This spins up:uv run eb init

- EC2 autoscaling group running your Docker container

- Application Load Balancer# Answer the prompts:

- RDS Postgres instance on the same VPC/security group# - Select region: 8) eu-north-1 (Stockholm)

- CloudWatch alarms and log groups# - Application name: fl-backend

# - Platform: Docker

> The build context uploaded to EB automatically excludes `.elasticbeanstalk/`, `.venv/`, `media/`, etc. thanks to the new `.ebignore` and `.dockerignore`, so the source bundle stays tiny and Docker builds finish well under the 5‑minute limit.# - Platform version: (select latest)

# - Do you want to set up SSH: Yes (recommended)

---```



## 4. Configure environment variablesThis creates a `.elasticbeanstalk/config.yml` file.



Use the sanitized `.env.production` template as a reference. Push the values to EB in one shot:### 4. Create Production Environment with Database



```bash```bash

uv run eb setenv \# Create environment with RDS PostgreSQL

  DEBUG=False \uv run eb create fl-backend-prod \

  DJANGO_SECRET_KEY='<generate-new-secret>' \  --database.engine postgres \

  ALLOWED_HOSTS='fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com,.elasticbeanstalk.com' \  --database.instance db.t3.micro \

  CSRF_TRUSTED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com,https://*.elasticbeanstalk.com' \  --database.username fldbuser \

  CORS_ALLOW_ALL_ORIGINS=False \  --database.password UoaLgmT91hwO \

  CORS_ALLOWED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com' \  --database.size 20 \

  SECURE_SSL_REDIRECT=False \  --instance-type t3.micro

  SESSION_COOKIE_SECURE=True \```

  CSRF_COOKIE_SECURE=True \

  AWS_REGION=eu-north-1 \Wait 5-10 minutes for environment creation. EB will:

  AWS_ACCESS_KEY_ID='<aws-access-key>' \

  AWS_SECRET_ACCESS_KEY='<aws-secret-key>' \- Create EC2 instances

  AWS_S3_BUCKET_NAME=podcast-fl \- Set up load balancer

  PODCAST_LIMIT=1000 \- Create RDS PostgreSQL database

  EMAIL='rfl.radiofrequenzalibera@gmail.com'- Configure security groups

```- Deploy your application



**RDS variables:** When you created the environment with `--database …`, Elastic Beanstalk automatically exposes `RDS_HOSTNAME`, `RDS_PORT`, `RDS_USERNAME`, `RDS_PASSWORD`, and `RDS_DB_NAME`. The new `docker-entrypoint.sh` and Django settings map those into the `PG*` variables automatically, so you no longer need to set them manually.### 5. Configure Environment Variables



**HTTPS toggle:** keep `SECURE_SSL_REDIRECT=False` until you attach a valid ACM certificate and enable the 443 listener on the load balancer. Once HTTPS is live, flip it to `True` and redeploy.Use `.env.production` as the source of truth locally, but never commit real secrets. Push the values to Elastic Beanstalk with a single `uv run eb setenv` command. Replace the placeholders below with the values stored in your password manager:



---```bash

uv run eb setenv \

## 5. Deploy  DEBUG=False \

  DJANGO_SECRET_KEY='<your-django-secret>' \

```bash  ALLOWED_HOSTS='fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com,.elasticbeanstalk.com' \

# Package + deploy the current commit  CSRF_TRUSTED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com' \

uv run eb deploy fl-backend-prod  CORS_ALLOW_ALL_ORIGINS=False \

```  CORS_ALLOWED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com' \

  SECURE_SSL_REDIRECT=False \

What happens during deployment:  SESSION_COOKIE_SECURE=True \

  CSRF_COOKIE_SECURE=True \

1. EB zips the repo (respecting `.ebignore`) and uploads it to S3.  AWS_REGION=eu-north-1 \

2. The Dockerfile builds a slim python:3.11 image with all requirements.  AWS_ACCESS_KEY_ID='<your-access-key>' \

3. `docker-entrypoint.sh` waits for Postgres, runs migrations + collectstatic, then launches Gunicorn.  AWS_SECRET_ACCESS_KEY='<your-secret-key>' \

  AWS_S3_BUCKET_NAME=podcast-fl \

You can tail progress with:  PODCAST_LIMIT=1000 \

  EMAIL='rfl.radiofrequenzalibera@gmail.com'

```bash```

uv run eb events --follow fl-backend-prod

uv run eb logs fl-backend-prod --all**Important:** `docker-entrypoint.sh` automatically maps the RDS-provided variables (`RDS_HOSTNAME`, `RDS_USERNAME`, etc.) into the `PG*` variables expected by Django, so you do **not** need to set `PGHOST`, `PGUSER`, or `PGPASSWORD` manually.

```

**HTTPS reminder:** keep `SECURE_SSL_REDIRECT=False` until your load balancer has a valid TLS certificate. Once HTTPS is configured (see “Enable HTTPS” below) you can flip it to `True` along with the secure cookie flags.

---

### 6. Create S3 Bucket for Media Files

## 6. Post-deploy tasks

```bash

### Create the Django superuser (only once per environment)# Create S3 bucket

aws s3 mb s3://fl-backend-media-prod --region eu-north-1

```bash

uv run eb ssh fl-backend-prod# Set bucket policy for public read access (if needed)

sudo docker ps   # grab the container IDaws s3api put-bucket-policy --bucket fl-backend-media-prod --policy file://s3-bucket-policy.json

sudo docker exec -it <container-id> /bin/bash -lc "python manage.py createsuperuser"```

exit

```Create `s3-bucket-policy.json`:



### Verify health```json

{

```bash  "Version": "2012-10-17",

uv run eb health --refresh fl-backend-prod  "Statement": [

uv run eb status fl-backend-prod    {

```      "Sid": "PublicReadGetObject",

      "Effect": "Allow",

If the health checker reports HTTP 301s, ensure `SECURE_SSL_REDIRECT` is still `False` until HTTPS is configured.      "Principal": "*",

      "Action": "s3:GetObject",

---      "Resource": "arn:aws:s3:::fl-backend-media-prod/*"

    }

## 7. HTTPS & custom domain  ]

}

1. Request an SSL certificate in AWS Certificate Manager for your production domain.```

2. Attach the certificate to the load balancer (port 443 listener) via `uv run eb config` or the AWS console.

3. Update DNS (Route 53 or your registrar) to point the domain to the load balancer CNAME.### 7. Run Database Migrations & Create the Admin User

4. Set `SECURE_SSL_REDIRECT=True` and redeploy so Django enforces HTTPS.

`docker-entrypoint.sh` runs `python manage.py migrate --noinput` and `python manage.py collectstatic --noinput` every time the container starts, so migrations and static files stay up to date automatically.

---

You still need to create the initial Django superuser inside the running container:

## 8. Daily operations

```bash

| Task | Command |# SSH into the EC2 host managed by EB

| --- | --- |uv run eb ssh fl-backend-prod

| Deploy latest code | `uv run eb deploy fl-backend-prod` |

| View recent logs | `uv run eb logs fl-backend-prod` |# Find the container ID

| Tail events | `uv run eb events --follow fl-backend-prod` |sudo docker ps

| Update env vars | `uv run eb setenv KEY=value ...` |

| Scale instances | `uv run eb scale <count>` |# Execute Django management commands inside the container

sudo docker exec -it <container_id> /bin/bash -lc "python manage.py createsuperuser"

---

# When finished

## 9. Troubleshootingexit

```

- **Docker build timed out** – ensure large folders (logs, .venv, .elasticbeanstalk) stay ignored. Run `git clean -fdx .elasticbeanstalk/app_versions` if needed.

- **Health checker stuck on 301/4xx** – most often caused by forcing HTTPS before TLS is configured. Confirm the ALB has a 443 listener + certificate before enabling `SECURE_SSL_REDIRECT`.Re-run the `docker exec` command any time you need to inspect the database, run ad-hoc management commands, or create additional users.

- **Database connection errors** – verify `RDS_*` env variables exist in `uv run eb printenv` and that the security groups allow EC2 → RDS traffic.

- **Admin unreachable** – temporarily set `SECURE_SSL_REDIRECT=False`, redeploy, and access over HTTP while you finish HTTPS setup.### 8. Open Your Application



---```bash

# Open application in browser

## 10. Cleanupuv run eb open



```bash# Check application status

uv run eb terminate fl-backend-prod --forceuv run eb status

```

# View logs

This tears down EC2, RDS, load balancer, and all linked resources. Remember to delete the S3 log/app-version bucket separately if you no longer need it.uv run eb logs

```

Your application is now live! 🎉

---

## GitLab CI/CD Integration

### 1. Add GitLab CI/CD Variables

Go to: **GitLab Project → Settings → CI/CD → Variables**

Add these variables (mark sensitive ones as "Masked"):

| Variable                        | Value                             | Masked |
| ------------------------------- | --------------------------------- | ------ |
| `AWS_ACCESS_KEY_ID`           | Your AWS access key               | ✓     |
| `AWS_SECRET_ACCESS_KEY`       | Your AWS secret key               | ✓     |
| `AWS_DEFAULT_REGION`          | `eu-north-1`                    |        |
| `EB_ENVIRONMENT_NAME`         | `fl-backend-prod`               |        |
| `PRODUCTION_URL`              | Your EB URL                       |        |
| `EB_STAGING_ENVIRONMENT_NAME` | `fl-backend-staging` (optional) |        |
| `STAGING_URL`                 | Staging URL (optional)            |        |

### 2. Commit and Push to GitLab

```bash
git add .
git commit -m "Add AWS Elastic Beanstalk deployment configuration"
git push origin main
```

### 3. Trigger Deployment

1. Go to GitLab → CI/CD → Pipelines
2. Wait for tests to complete
3. Manually trigger the `deploy_production` job
4. Monitor deployment progress

---

## Advanced Configuration

### Auto-run Migrations with .ebextensions

Create `.ebextensions/01_django.config`:

```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
    leader_only: true

option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: "frequenza_libera.settings"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "frequenza_libera.wsgi:application"
```

### Enable HTTPS

1. Request/validate an SSL certificate in AWS Certificate Manager (ACM) for your production domain or the Elastic Beanstalk URL.
2. Add a listener on port 443 in the environment’s load balancer and attach the ACM certificate (via `uv run eb config` or the AWS Console).
3. Once HTTPS is confirmed working, set `SECURE_SSL_REDIRECT=True` (and keep the secure cookie flags enabled). Until then, leave it `False` to avoid redirect loops where the load balancer only listens on HTTP.

### Set Up Custom Domain

1. Get SSL certificate from AWS Certificate Manager
2. Configure Route 53 or your DNS provider
3. Update load balancer to use certificate
4. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`

### Environment-specific Deployments

```bash
# Create staging environment
uv run eb create fl-backend-staging --cname fl-backend-staging

# Deploy to staging
uv run eb deploy fl-backend-staging

# Deploy to production
uv run eb deploy fl-backend-prod
```

---

## Daily Operations

### Deploy New Changes

```bash
# Local deployment
git add .
git commit -m "Your changes"
uv run eb deploy

# Or use GitLab CI/CD (recommended)
git push origin main
# Then trigger manual deployment in GitLab
```

### View Logs

```bash
# View recent logs
uv run eb logs

# Stream logs in real-time
uv run eb logs --stream
```

### Check Application Health

```bash
uv run eb health
uv run eb status
```

### Scale Application

```bash
# Scale to multiple instances
uv run eb scale 3

# Or configure auto-scaling in AWS Console
```

### Update Environment Variables

```bash
uv run eb setenv NEW_VAR=value ANOTHER_VAR=value
```

---

## Monitoring & Debugging

### CloudWatch Logs

- Go to AWS Console → CloudWatch → Log Groups
- Find `/aws/elasticbeanstalk/fl-backend-prod/`
- View application logs, web server logs, etc.

### Health Dashboard

```bash
uv run eb health --refresh
```

### SSH into Instance

```bash
uv run eb ssh
```

---

## Cost Estimate (Minimal Setup)

- **EC2 t3.micro**: ~$8/month
- **RDS db.t3.micro**: ~$15/month
- **Load Balancer**: ~$16/month
- **Data Transfer**: Variable
- **S3 Storage**: ~$0.02/GB/month

**Total**: ~$40-50/month for small-scale deployment

---

## Troubleshooting

### Application Won't Start

1. Check logs: `uv run eb logs`
2. Verify environment variables: `uv run eb printenv`
3. SSH and test manually: `uv run eb ssh`

### Database Connection Fails

```bash
# Verify RDS environment variables are set
uv run eb printenv | grep PG

# Check security groups allow EC2 → RDS connection
```

### Static Files Not Loading

- `docker-entrypoint.sh` already runs `collectstatic`; check the container logs to confirm it finishes without errors.
- Verify WhiteNoise is configured for static delivery.
- Confirm S3 permissions if you offload media files there.

### Admin Page Redirects Forever

- If the admin URL keeps redirecting between HTTP and HTTPS, double-check whether `SECURE_SSL_REDIRECT` is set to `True` while the load balancer only exposes HTTP.
- Either add an HTTPS listener with a valid certificate or temporarily set `SECURE_SSL_REDIRECT=False` and redeploy so the admin UI stays reachable over HTTP.

### Deployment Fails

- Check `.elasticbeanstalk/logs/` directory
- Verify Docker image builds locally: `docker build .`
- Review GitLab CI/CD logs

---

## Cleanup (Delete Everything)

```bash
# Terminate environment (WARNING: This deletes everything)
uv run eb terminate fl-backend-prod

# Confirm when prompted
```

---

## Next Steps

1. ✓ Deploy to production
2. Set up custom domain with HTTPS
3. Configure automated backups for RDS
4. Set up monitoring alerts (CloudWatch Alarms)
5. Implement staging environment
6. Configure auto-scaling policies
7. Set up CI/CD automation for automatic deployments

---

## Support Resources

- [Elastic Beanstalk Documentation](https://docs.aws.amazon.com/elasticbeanstalk/)
- [EB CLI Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
- [Django on Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
