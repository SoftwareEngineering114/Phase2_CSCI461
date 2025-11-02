# Milestone 8 - CI/CD Demo Notes

## CI (Continuous Integration)

On every pull request, GitHub Actions runs the CI workflow (`.github/workflows/ci.yml`). This workflow checks out the repository, installs dependencies (including pytest), and runs `pytest -q` to execute automated tests. This gives early feedback before merging code to main, helping catch bugs and regressions before they reach production. This fulfills the "automated tests on every pull request" requirement.

## CD (Continuous Deployment)

After merging to main, GitHub Actions automatically runs the deploy workflow (`.github/workflows/deploy.yml`). This workflow:

1. Checks out the repository
2. Configures AWS credentials using IAM user keys stored in GitHub Secrets
3. Writes the EC2 private SSH key from secrets to a temporary key file
4. Creates the app directory on the EC2 instance if it doesn't exist
5. Copies the entire repository to `/home/$EC2_USER/app` on the EC2 instance via SCP
6. SSHes into the EC2 instance and runs `docker compose up -d --build`, which builds the Docker image from the Dockerfile and starts the FastAPI service

The EC2 instance is expected to serve the FastAPI app (via uvicorn) on port 80, which maps to the container's internal port 8000. The `/health` endpoint at `http://EC2_HOST/health` will return a status check so that instructors/autograder can verify the service is running.

Note: Deployment may currently fail at the AWS credential step because we are waiting for long-lived IAM user keys (Access Key ID starting with AKIA) instead of temporary SSO credentials. The pipeline is implemented and in place - once the IAM user credentials are configured in GitHub Secrets, the pipeline will complete end-to-end automatically after every merge to main.

This matches the requirement: "Automated service deployment (CD/Continuous Deployment) to AWS upon a successful merge."

## Screenshots to include in Milestone 8 submission

- Screenshot of a pull request with the CI workflow passing (or at least running pytest)
- Screenshot of the GitHub Actions 'CD - Deploy to AWS' run after a push to main, even if it fails at AWS creds
- Screenshot of the EC2 instance/security group showing that port 80 is open for HTTP

## Are we on track?

We are on track with CI/CD automation. The main blocker is AWS IAM keys: our AWS account uses IAM Identity Center (SSO), so we're waiting for a dedicated IAM user with programmatic access so that GitHub Actions can authenticate. Once that is issued, the pipeline will complete end-to-end automatically after every merge to main.

