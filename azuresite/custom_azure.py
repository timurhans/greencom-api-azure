from storages.backends.azure_storage import AzureStorage

class AzureMediaStorage(AzureStorage):
    account_name = 'ondasstr092020' # Must be replaced by your <storage_account_name>
    account_key = '36dU3mBiwh55yB4LjSywH++J6V1HZbdjWe3UjQpmVFsyOYviHT6LX+Tvj6923qR2EpInMjgIggZFhZXKr3xs8Q==' # Must be replaced by your <storage_account_key>
    azure_container = 'greencom'
    expiration_secs = None