# Smartbonus package for Python language

This package provides Python implementation of Smartbonus api. Supported all public api of smartbonus.

With 100% test coverage.

## Installation

Use the `pip` command:

	$ pip install smartbonuspy

## Requirements

Smartbonus package tested against Python 3.8.1

## Example

```
from smartbonus import SmartBonus, set_root_path

# Creating sb
# Ask about params smartbonus team
set_root_path("https://your.smartbonus.com/api/v2/")
sb = SmartBonus("your store id")

# Get smartbonus info about client: catch error by self
client, ok = sb.get_client('0555555555')
print(client, ok)

# Get erorr
data, ok = sb.get_client('0555555555', raise_error=False)
if ok:
    print('your client', data)
else:
    print('error', data)

# see tests for more
```
