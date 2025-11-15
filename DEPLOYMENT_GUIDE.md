# AWS Elastic Beanstalk Deployment Guide

This project now runs on **Elastic Beanstalk (Docker on Amazon Linux 2023)**. The repository ships with a production-ready Dockerfile, entrypoint, and `.ebextensions` so you can recreate the environment or redeploy with a handful of commands.

> All CLI examples use `uv run eb …`. `uv` installs and caches the EB CLI inside the project environment, so nothing needs to be installed globally.

---

## Prerequisites

- AWS account with permissions for Elastic Beanstalk, EC2, RDS, S3, IAM, VPC, and ACM
- AWS CLI configured locally (`aws configure`) with region `eu-north-1`
- [`uv`](https://github.com/astral-sh/uv) installed
- Docker available locally (for optional sanity checks)
- (Optional) EC2 key pair for SSHing into the instances

---

## 1. Install tooling & verify access

```bash
uv add awsebcli --dev          # download EB CLI into the repo-managed venv
uv run eb --version            # confirm the CLI works
aws configure                  # ensure credentials & default region are set
```

---

## 2. Initialize the Elastic Beanstalk application (per workstation)

```bash
uv run eb init
# Region: eu-north-1 (Stockholm)
# Platform: Docker running on 64bit Amazon Linux 2023
# Application name: fl-backend
# SSH: yes if you want to use `uv run eb ssh`
```

This creates `.elasticbeanstalk/config.yml` (already gitignored) so future commands know which project and environment they should target.

---

## 3. Provision the production environment + RDS

```bash
uv run eb create fl-backend-prod \
  --platform "Docker running on 64bit Amazon Linux 2023" \
  --instance-type t3.micro \
  --database.engine postgres \
  --database.instance db.t3.micro \
  --database.username <db-user> \
  --database.password <db-password> \
  --database.size 20
```

Elastic Beanstalk provisions:

- EC2 autoscaling group running this Docker image
- Application Load Balancer (HTTP by default)
- RDS PostgreSQL (same VPC/security group)
- CloudWatch log groups + alarms

The environment automatically injects `RDS_HOSTNAME`, `RDS_PORT`, `RDS_USERNAME`, `RDS_PASSWORD`, and `RDS_DB_NAME`. `docker-entrypoint.sh` converts those into the `PG*` variables Django expects, so you do **not** need to set DB env vars manually.

---

## 4. Configure environment variables

1. Copy `.env.sample` → `.env.prod`, fill in secrets, and keep it out of git.
2. Push the values to EB (example below – adjust hosts/origins/secrets to match the current environment name/CNAME):

```bash
uv run eb setenv \
  DEBUG=False \
  DJANGO_SECRET_KEY='<your-secret>' \
  ALLOWED_HOSTS='fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com,.elasticbeanstalk.com' \
  CSRF_TRUSTED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com,https://*.elasticbeanstalk.com' \
  CORS_ALLOW_ALL_ORIGINS=False \
  CORS_ALLOWED_ORIGINS='https://fl-backend-prod.eba-y7gpd5mx.eu-north-1.elasticbeanstalk.com' \
  SECURE_SSL_REDIRECT=False \
  SESSION_COOKIE_SECURE=True \
  CSRF_COOKIE_SECURE=True \
  AWS_REGION=eu-north-1 \
  AWS_ACCESS_KEY_ID='<aws-access-key>' \
  AWS_SECRET_ACCESS_KEY='<aws-secret-key>' \
  AWS_S3_BUCKET_NAME='podcast-fl' \
  PODCAST_LIMIT=1000 \
  EMAIL='rfl.radiofrequenzalibera@gmail.com'
```

> Keep `SECURE_SSL_REDIRECT=False` until you attach an ACM certificate and enable HTTPS on the load balancer. Flip it to `True` afterwards and redeploy.

---

## 5. Deploy new code

```bash
uv run eb deploy fl-backend-prod
```

What happens:

1. EB uploads a tiny source bundle (thanks to `.ebignore` / `.dockerignore`).
2. Docker builds the image defined in `Dockerfile`.
3. `docker-entrypoint.sh` waits for Postgres, runs `migrate` + `collectstatic`, and finally starts Gunicorn.

Helpful diagnostics:

```bash
uv run eb events --follow fl-backend-prod   # live status updates
uv run eb logs fl-backend-prod --all        # full log bundle (engine, docker, nginx)
uv run eb open                              # open the environment URL in a browser
```

---

## 6. Post-deploy tasks

- **Media bucket** – create (or reuse) `s3://podcast-fl` in `eu-north-1` and attach a bucket policy if public reads are required.
- **Create superuser** – `uv run eb ssh`, then `sudo docker ps` + `sudo docker exec -it <container> /bin/bash -lc "python manage.py createsuperuser"`.
- **Verify health** – `uv run eb health --refresh fl-backend-prod` and `uv run eb status fl-backend-prod`. If health shows 301s, double-check that HTTPS isn’t forced yet.

---

## 7. Daily operations

| Task                 | Command                                       |
| -------------------- | --------------------------------------------- |
| Deploy latest commit | `uv run eb deploy fl-backend-prod`          |
| Tail events          | `uv run eb events --follow fl-backend-prod` |
| Download logs        | `uv run eb logs fl-backend-prod --all`      |
| Update env vars      | `uv run eb setenv KEY=value …`             |
| Check health/status  | `uv run eb health` / `uv run eb status`   |
| Scale instances      | `uv run eb scale <count>`                   |
| SSH into instance    | `uv run eb ssh fl-backend-prod`             |

`docker-entrypoint.sh` automatically reruns migrations and `collectstatic` every time the container restarts, so rolling out schema changes is simply `git push + eb deploy`.

---

## 8. HTTPS & custom domains

1. Request/validate an ACM certificate for the production domain.
2. Add a 443 listener to the load balancer and attach the certificate (AWS Console or `uv run eb config`).
3. Point DNS (Route 53 or your registrar) to the EB CNAME.
4. Set `SECURE_SSL_REDIRECT=True` (cookies are already marked secure) and redeploy.

---

## 9. Troubleshooting cheatsheet

- **Container exits instantly** → Check `var/log/eb-docker/containers/eb-current-app/unexpected-quit.log` inside the downloaded log bundle.
- **DB connection errors** → `uv run eb printenv | grep RDS_` to confirm EB injected credentials; verify the security group allows EC2 → RDS traffic.
- **Health stuck on 301** → Toggle `SECURE_SSL_REDIRECT=False` until HTTPS is configured.
- **Large uploads / slow builds** → Ensure `.ebignore` excludes `.elasticbeanstalk/`, `.venv/`, `media/`, etc. You can clear cached bundles with `rm -rf .elasticbeanstalk/app_versions/*`.

---

## 10. Cleanup

```bash
uv run eb terminate fl-backend-prod --force
```

This tears down EC2, RDS, ALB, and supporting resources. Delete the S3 bucket separately if it is no longer needed.

---

## Reference files

- `.env.sample` → copy to `.env.prod` for production secrets (never commit real values).
- `docker-entrypoint.sh` → maps RDS env vars, waits for the database, then runs migrations/collectstatic before booting Gunicorn.
- `.ebextensions/01_env.config` → defines default EB environment variables (port, Gunicorn tuning, etc.).

Happy deploying! 🎉
