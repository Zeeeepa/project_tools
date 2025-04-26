# Security Best Practices

This document outlines security best practices for using the Project Tools application, particularly regarding API key management.

## API Key Management

### Development Environment

For development environments, you can use environment variables to store API keys:

```bash
export OPENAI_API_KEY=your_key_here
export ANTHROPIC_API_KEY=your_key_here
```

However, this approach is not recommended for production environments.

### Production Environment

For production environments, consider the following approaches:

1. **Use a Secrets Manager**:
   - AWS Secrets Manager
   - Google Secret Manager
   - Azure Key Vault
   - HashiCorp Vault

2. **Use Encrypted Configuration Files**:
   - Store encrypted configuration files
   - Decrypt them at runtime
   - Use tools like `ansible-vault` or similar encryption tools

3. **Use Environment-Specific Configuration**:
   - Different configuration files for different environments
   - Restrict access to production configuration files

## Example: Using AWS Secrets Manager

```python
import boto3
from botocore.exceptions import ClientError

def get_secret():
    secret_name = "projects_tools/api_keys"
    region_name = "us-west-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # Handle exceptions
        raise e
    else:
        # Decrypts secret using the associated KMS key
        secret = get_secret_value_response['SecretString']
        return secret

# Use the secret in your application
api_keys = get_secret()
```

## Example: Using Encrypted Configuration Files

```python
import json
import os
from cryptography.fernet import Fernet

def load_encrypted_config(config_path, key_path):
    # Load the key
    with open(key_path, 'rb') as key_file:
        key = key_file.read()
    
    # Initialize the Fernet cipher
    cipher = Fernet(key)
    
    # Read and decrypt the config file
    with open(config_path, 'rb') as config_file:
        encrypted_data = config_file.read()
    
    decrypted_data = cipher.decrypt(encrypted_data)
    config = json.loads(decrypted_data)
    
    return config

# Use the encrypted config
config = load_encrypted_config('config.encrypted', '.key')
openai_api_key = config['openai_api_key']
anthropic_api_key = config['anthropic_api_key']
```

## Additional Security Considerations

1. **Rotate API Keys Regularly**: Implement a process to rotate API keys on a regular schedule.

2. **Implement Least Privilege**: Ensure that API keys have the minimum permissions necessary.

3. **Monitor API Usage**: Set up monitoring and alerting for unusual API usage patterns.

4. **Secure Your Application**: Implement proper authentication and authorization in your application.

5. **Audit Logging**: Maintain comprehensive logs of API key usage for audit purposes.

## References

- [OpenAI API Key Best Practices](https://platform.openai.com/docs/guides/safety-best-practices)
- [AWS Secrets Manager Documentation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html)
- [OWASP Secrets Management Guide](https://owasp.org/www-project-cheat-sheets/cheatsheets/Secrets_Management_Cheat_Sheet.html)
