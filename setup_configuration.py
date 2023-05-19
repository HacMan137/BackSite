import json

TEMPLATE_PATH = "./configuration/config.json.template"
CONFIG_PATH = "./configuration/config.json"
# Read config template
with open(TEMPLATE_PATH,"r") as template_handle:
    template_data = json.loads(template_handle.read())
# Map configuration keys to explanation for each key
config_keys = {
    "API_LOCATION": {
        "explanation": "The internet-accessible location of the BackSite API. Should be in the form http(s)://domain.com(:port)",
        "default": "http://localhost:8080"
    },
    "API_COMMON_NAME": { 
        "explanation": "The name of your application. For example, Facebook, Twitter, etc. But obviously, not those. Used to fill email templates",
        "default": "My Cool Website"
    },
    "FRONTFACING_URL": {
        "explanation": "The URL of the UI that BackSite should point to. Used to generate email verification links",
        "default": "http://localhost:80"
    },
    "VERIFICATION_ENDPOINT": {
        "explanation": "The endpoint used by the front-facing UI to process user verification requests. Needed to generate email verification links. Must be able to accept a parameter called 'secret'",
        "default": "/user/verify"
    },
    "ADMIN_EMAIL": {
        "explanation": "Email address of the administrator account",
        "default": "admin@fake.com"
    },
    "API_EMAIL": {
        "explanation": "The 'From' email for each email sent out by the system",
        "default": "no-reply@fake.com"
    },
    "SMTP_HOST": {
        "explanation": "The server used for handling SMTP requests from the application",
        "default": "mail.smtp2go.com"
    },
    "SMTP_PORT": {
        "explanation": "Port serving the SSL-enabled SMTP service",
        "default": 465,
        "type": int
    },
    "SMTP_USERNAME": {
        "explanation": "Username to authenticate against the SMTP service with",
        "default": "smtpuser"
    },
    "SMTP_PASSWORD": {
        "explanation": "Password to authenticate against the SMTP service with",
        "default": "smtppass"
    }
}

def generate_config():
    final_config = {}
    for key in template_data:
        if key not in config_keys:
            print(f"Warning: {key} found in template, but is not supported by setup wizard")
            continue
        explanation = config_keys[key]["explanation"]
        default_val = config_keys[key]["default"]
        dtype = config_keys[key]["type"] if "type" in config_keys[key] else str
        print(f"\n{key}\n(default={default_val})\n{explanation}\n")
        while True:
            try:
                input_value = input(f"{key}=")
                if len(input_value) < 1:
                    value = dtype(default_val)
                else:
                    value = dtype(input_value)
                break
            except Exception as e:
                print(f"Error: {e}")
        final_config[key] = value
    return final_config

if __name__ == "__main__":
    print("BackSite Configuration File Setup Wizard\n--------------------------------\n\n")
    final_config = generate_config()
    with open(CONFIG_PATH, "w") as config_handle:
        config_handle.write(json.dumps(final_config, indent=4))
    print("Configuration file generated.")