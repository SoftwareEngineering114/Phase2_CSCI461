# Steps to Add SSH Public Key to EC2 Instance

## Step 1: Find your EC2 Hostname/IP
- Option A: Check GitHub Secrets
  - Go to: Repository → Settings → Secrets and variables → Actions
  - Look for `EC2_HOST` secret
  
- Option B: Check AWS Console
  - Go to: EC2 → Instances
  - Copy the "Public IPv4 address" or "Public IPv4 DNS"

## Step 2: SSH into your EC2 instance (run this in PowerShell)

```powershell
ssh -i "C:\Users\om4la\Downloads\phase-2-key.pem" ec2-user@YOUR_EC2_HOST_OR_IP
```

Replace `YOUR_EC2_HOST_OR_IP` with your actual EC2 hostname/IP.

**Note:** The username might be `ubuntu`, `admin`, or another user depending on your AMI. Common usernames:
- Amazon Linux: `ec2-user`
- Ubuntu: `ubuntu`
- Debian: `admin`
- Check your `EC2_USER` secret in GitHub

## Step 3: Once connected to EC2 (you'll see a Linux prompt), run these commands:

```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
echo "ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
cat ~/.ssh/authorized_keys
```

## Step 4: Verify it worked

The last command should show your new public key in the file. Then exit EC2:

```bash
exit
```

## Step 5: Update GitHub Secret

Make sure your `EC2_SSH_KEY` secret in GitHub has the private key with **NO blank lines**:

```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz
c2gtZWQyNTUxOQAAACA30Fa2kSByxb7JSeq0myuawSv2LC4QO8Y08Whan+9YtQAA
AIi0Rxh1tEcYdQAAAAtzc2gtZWQyNTUxOQAAACA30Fa2kSByxb7JSeq0myuawSv2
LC4QO8Y08Whan+9YtQAAAEAwUQIBATAFBgMrZXAEIgQg1dCHVM7NKfaHqdRDNnJV
YjfQVraRIHLFvslJ6rSbK5rBK/YsLhA7xjTxaFqf71i1AAAAAAECAwQF
-----END OPENSSH PRIVATE KEY-----
```

After these steps, your GitHub Actions should be able to authenticate to EC2!

