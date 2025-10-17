# Ansible Demo Playbooks

This repository demonstrates a complete provisioning and promotion pipeline for a Dockerised Flask application that is automatically promoted across **development**, **staging**, and **production** EC2 environments.

## Infrastructure Playbooks

- `provision_envs.yml` — creates three EC2 instances (development, staging, production) with consistent settings, security groups (ports 22/80/443), and identifying tags.
- `deploy_app.yml` — installs Docker, builds the calculator web app image, deploys it as a **systemd**-managed container, and performs a health check that restarts the service if it is inactive.
- `service_health.yml` — lightweight playbook that checks the calculator service and restarts it if it is not active (useful for demoing the auto-recovery behaviour).

**Dynamic inventory:** `aws_ec2.yml` scopes hosts to instances tagged `ProvisionedBy=ansible-calculator` and automatically groups them by the `Environment` tag (development/staging/production).

### Provision the environments

```bash
# Ensure AWS credentials/region are configured, then:
ansible-galaxy collection install amazon.aws
ansible-playbook -i localhost, provision_envs.yml \
  -e key_name=ansible-test \
  -e region=ap-southeast-1
```

Override variables such as `instance_type`, `vpc_id`, or `subnet_id` with `-e` as required. The play outputs the public endpoints for each environment.

### Deploy or heal the application

```bash
export ANSIBLE_PRIVATE_KEY_FILE=~/.ssh/keys/ansible-test.pem
ansible-galaxy collection install amazon.aws community.docker
ansible-playbook -i aws_ec2.yml deploy_app.yml -e target_env=development -e app_version=demo1
```

Running the playbook again (or after intentionally stopping the service) re-checks the systemd unit and restarts the container if required for presentation purposes. For a lightweight self-healing demo, run `ansible-playbook -i aws_ec2.yml service_health.yml -e target_env=production`.

## Application

The Flask calculator app lives under `app/` and is packaged as a Docker container:

- Retro-styled single-page calculator UI with a live clock (`app/calculator/static`).
- JSON calculation API (`POST /api/calculate`) and health endpoint (`/healthz`).
- Pytest suite in `app/tests/` and linting configured via `.flake8`.
- Dockerfile (`app/Dockerfile`) builds a Gunicorn-based image exposing port 8080.

## GitHub Actions CI/CD

.github/workflows/ci-cd.yml implements the promotion pipeline:

1. **Lint & Test** — runs `flake8` and `pytest` on every push/PR to `development`, `staging`, or `main`.
2. **Deploy** — on successful pushes, determines the target environment from the branch (`development` → dev, `staging` → staging, `main` → production) and executes `ansible-playbook deploy_app.yml` against the matching EC2 host(s).

Required repository secrets:

- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` (and optionally `AWS_SESSION_TOKEN`).
- `ANSIBLE_PRIVATE_KEY` — private SSH key for the EC2 instances (PEM format, no passphrase).

The workflow sets `ANSIBLE_PRIVATE_KEY_FILE` so the dynamic inventory can connect, installs the necessary Ansible collections, and tags Docker images by the short commit SHA for traceability.

## Maintenance Tips

- Use `ansible-playbook -i aws_ec2.yml deploy_app.yml -e target_env=<env>` to redeploy after code changes or to demonstrate the auto-recovery task.
- To clean resources after a demo, terminate the EC2 instances manually or extend `cleanup.yml` to remove the tagged hosts.
- Update security group CIDRs in `provision_envs.yml` if you need to restrict access beyond `0.0.0.0/0`.
