# Step-by-Step: Add Public Key to EC2

## ✅ Step 1: Private Key File Created
- File: `my-ci-key` (your private key)
- ✅ This matches what's in your GitHub secret `EC2_SSH_KEY`

## ✅ Step 2: Public Key Generated
- File: `my-ci-key.pub` 
- **Your public key is:**
  ```
  ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=
  ```

## 🔧 Step 3: Add Public Key to EC2

### From your Windows machine, SSH into EC2:

```powershell
# Use your existing AWS key that works
ssh -i "C:\Users\om4la\Downloads\phase-2-key.pem" ec2-user@YOUR_EC2_HOST
```

**Replace `YOUR_EC2_HOST` with:**
- Your EC2 Public IPv4 address, OR
- Your EC2 Public DNS name
- (Check GitHub secret `EC2_HOST` or AWS Console)

**If `ec2-user` doesn't work, try:**
- `ubuntu` (for Ubuntu AMI)
- `admin` (for Debian)
- Check your GitHub secret `EC2_USER`

### Once connected to EC2, run these commands:

```bash
# Make sure .ssh directory exists with correct permissions
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add the public key to authorized_keys
echo "ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=" >> ~/.ssh/authorized_keys

# Lock down permissions
chmod 600 ~/.ssh/authorized_keys

# Verify it was added correctly
cat ~/.ssh/authorized_keys
```

You should see your public key in the output.

## 🧪 Step 4: Test the Connection

### From your Windows machine, test with the new key:

```powershell
# Make sure you're in the directory with my-ci-key
cd C:\Users\om4la\Education\SoftwareEngineering\Phase2Code\Phase2_CSCI461\CSCI461

# Test SSH connection using the new key
ssh -i my-ci-key ec2-user@YOUR_EC2_HOST
```

**If this works:** ✅ You're all set! The GitHub Actions workflow should work.

**If this fails:**
- Try `ubuntu@YOUR_EC2_HOST` instead of `ec2-user`
- Verify the public key is in `~/.ssh/authorized_keys` on EC2
- Check EC2 Security Group allows SSH (port 22) from anywhere (or from GitHub Actions IPs)

## 📋 Step 5: Verify GitHub Secrets

Make sure these secrets are set correctly in GitHub:
- `EC2_HOST` → Your EC2 public IP or DNS
- `EC2_USER` → `ec2-user` (or `ubuntu` if that's what worked)
- `EC2_SSH_KEY` → The **private key** content (from `my-ci-key` file)
  - Must have NO blank lines between BEGIN and END markers

## 🚀 Step 6: Test GitHub Actions

After completing steps 1-4:
1. Push a commit to main (or trigger the workflow)
2. Watch the "Deploy on EC2" step
3. It should now authenticate successfully! ✅

---

## 🔍 Troubleshooting

### If SSH test fails locally:
- **Wrong username:** Try `ubuntu` instead of `ec2-user`
- **Key not found:** Make sure you're in the right directory with `my-ci-key`
- **Permission denied:** Check EC2 Security Group allows port 22

### If GitHub Actions still fails:
- Check the "Prepare SSH key" step logs - it will show the extracted public key
- Verify it matches: `ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=`
- Double-check GitHub secret `EC2_SSH_KEY` has no blank lines

