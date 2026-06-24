#!/usr/bin/env python3
import yaml
cfg_path = '/Users/jushuai/.hermes/config.yaml'
with open(cfg_path) as f:
    config = yaml.safe_load(f)
config['fallback_providers'] = [{'provider': 'lmstudio', 'model': 'gemma-4-12b'}]
with open(cfg_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
print('Config updated successfully')
print('New fallback_providers:', config['fallback_providers'])
