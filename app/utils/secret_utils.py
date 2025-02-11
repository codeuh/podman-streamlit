import streamlit as st

def get_cached_secrets(client):
    """
    Retrieves a list of cached secrets from the client.

    Args:
        client (PodmanClient): The client object used to access the secrets.

    Returns:
        A list of dictionaries containing the name and ID of each secret.
    """
    secrets_list = list_secrets(client)
    return [{"Name": secret.name, "ID": secret.id} for secret in secrets_list]

@st.cache_data
def refresh_cached_secrets(client):
    """
    Refreshes the cached secrets by clearing the cache and retrieving a new list of secrets from the client.

    Args:
        client (PodmanClient): The client object used to access the secrets.

    Returns:
        A list of dictionaries containing the name and ID of each secret.
    """
    st.cache_data.clear()
    return get_cached_secrets(client)

def list_secrets(client):
    """
    Retrieves a list of secrets from the client.

    Args:
        client (PodmanClient): The client object used to access the secrets.

    Returns:
        A list of secrets.
    """
    return client.secrets.list()

def create_secret(client, secret_name, data):
    """
    Creates a new secret with the provided name and data using the given client.

    Args:
        client (PodmanClient): The client object used to access the secrets.
        secret_name (str): The name of the secret to be created.
        data (str): The data associated with the secret.
    Returns:
        The newly created secret object.
    """
    secret = client.secrets.create(name=secret_name, data=data)
    return secret

def delete_secret(client, secret_id):
    """
    Deletes a secret by its ID using the provided client.
    Args:
        client (PodmanClient): The client object used to access the secrets.
        secret_id (str): The ID of the secret to be deleted.

    Returns:
        None

    Raises:
        Exception: If an error occurs during deletion, the exception is caught and printed.
    """
    try:
        client.secrets.remove(secret_id)
        print("Secret deleted successfully.")
    except Exception as e:
        print(str(e))

def secret_exists(client, secret_name):
    """
    Checks if a secret with the given name exists in the list of cached secrets.

    Args:
        client (PodmanClient): The client object used to access the secrets.
        secret_name (str): The name of the secret to be checked for existence.

    Returns:
        bool: True if a secret with the given name exists, False otherwise.
    """
    secrets = get_cached_secrets(client)
    return any(secret["Name"] == secret_name for secret in secrets)