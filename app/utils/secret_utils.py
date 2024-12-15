import streamlit as st

def get_cached_secrets(client):
    secrets_list = list_secrets(client)
    return [{"Name": secret.name, "ID": secret.id} for secret in secrets_list]

@st.cache_data
def refresh_cached_secrets(client):
    st.cache_data.clear()
    return get_cached_secrets(client)

def list_secrets(client):
    return client.secrets.list()

def create_secret(client, secret_name, data):
    secret = client.secrets.create(name=secret_name, data=data)
    return secret

def delete_secret(client, secret_id):
    try:
        client.secrets.remove(secret_id)
        print(f"Secret {secret_id} deleted successfully.")
    except Exception as e:
        print(str(e))

def secret_exists(client, secret_name):
    secrets = get_cached_secrets(client)
    return any(secret["Name"] == secret_name for secret in secrets)