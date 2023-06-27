from dtsl.config import Config

if __name__ == '__main__':
    config_filename = 'config.yml'  # Provide your custom filename or leave it as None for the default filename
    config = Config()
    config.print_config()
    value = config.get_config_value('telegram_api.api_id')
    print(value)