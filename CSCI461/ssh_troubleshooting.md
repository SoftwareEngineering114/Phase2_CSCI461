# SSH Authentication Troubleshooting Checklist

## Most Common Issues:

### 1. GitHub Secret Format Issue ⚠️ **MOST LIKELY**

**The `EC2_SSH_KEY` secret in GitHub must have NO blank lines.**

**WRONG (has blank lines):**
```
-----BEGIN OPENSSH PRIVATE KEY-----

b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz

c2gtZWQyNTUxOQAAACA30Fa2kSByxb7JSeq0myuawSv2LC4QO8Y08Whan+9YtQAA

-----END OPENSSH PRIVATE KEY-----
```

**CORRECT (no blank lines):**
```
-----BEGIN OPENSSH PRIVATE KEY-----
b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQAAAAAAAAABAAAAMwAAAAtz
c2gtZWQyNTUxOQAAACA30Fa2kSByxb7JSeq0myuawSv2LC4QO8Y08Whan+9YtQAA
AIi0Rxh1tEcYdQAAAAtzc2gtZWQyNTUxOQAAACA30Fa2kSByxb7JSeq0myuawSv2
LC4QO8Y08Whan+9YtQAAAEAwUQIBATAFBgMrZXAEIgQg1dCHVM7NKfaHqdRDNnJV
YjfQVraRIHLFvslJ6rSbK5rBK/YsLhA7xjTxaFqf71i1AAAAAAECAwQF
-----END OPENSSH PRIVATE KEY-----
```

**To fix:**
1. Go to GitHub → Repository → Settings → Secrets → Actions
2. Edit `EC2_SSH_KEY`
3. Remove ALL blank lines between BEGIN and END
4. Make sure there are no spaces before `-----BEGIN-----` or after `-----END-----`
5. Save

### 2. Public Key Mismatch

**The public key extracted from your private key should be:**
```
ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=
```

**Verify on EC2:**
```bash
ssh -i "C:\Users\om4la\Downloads\phase-2-key.pem" ec2-user@YOUR_EC2_HOST
cat ~/.ssh/authorized_keys | grep "N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU="
```

**If it's NOT there or different:**
```bash
# Remove any old/different keys
# Add the correct one:
echo "ssh-ed25519 N9BWtpEgcsW+yUnqtJsrmsEr9iwuEDvGNPFoWp/vWLU=" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 3. Wrong Username

**Check your GitHub secret `EC2_USER`:**
- Amazon Linux: `ec2-user`
- Ubuntu: `ubuntu`
- Debian: `admin`

**Test locally:**
```powershell
ssh -i "C:\Users\om4la\Downloads\phase-2-key.pem" YOUR_USERNAME@YOUR_EC2_HOST
```

### 4. Permissions on EC2

**SSH into EC2 and verify:**
```bash
# Check directory permissions
ls -ld ~/.ssh
# Should show: drwx------ (700)

# Check authorized_keys permissions
ls -l ~/.ssh/authorized_keys
# Should show: -rw------- (600)

# Fix if wrong:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

### 5. Wrong Host/IP

**Verify `EC2_HOST` secret in GitHub:**
- Should be the Public IPv4 address OR Public DNS name
- Check AWS Console → EC2 → Instances → Your instance

## Debugging Steps:

1. **Check the GitHub Actions log:**
   - Look at the "Prepare SSH key" step
   - See what public key is extracted
   - Compare it to what's on EC2

2. **Test SSH locally from your machine:**
   ```powershell
   # Create test key file
   # Copy your private key content to a file (no blank lines!)
   # Then test:
   ssh -i path/to/test_key -v ec2-user@YOUR_EC2_HOST
   ```
   The `-v` flag shows detailed connection info.

3. **Verify on EC2:**
   ```bash
   # Check authorized_keys content
   cat ~/.ssh/authorized_keys
   
   # Check SSH logs (on EC2)
   sudo tail -f /var/log/secure
   # Then try connecting from GitHub Actions
   # You'll see authentication attempts in the log
   ```

## Quick Fix Priority:

1. ✅ **First:** Check GitHub secret format (remove blank lines)
2. ✅ **Second:** Verify public key on EC2 matches
3. ✅ **Third:** Check username and host are correct
4. ✅ **Fourth:** Verify permissions on EC2

