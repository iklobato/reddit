#!/usr/bin/env python3

import os
import sys

import requests


def test_quandl_token(api_key):
    test_url = "https://www.quandl.com/api/v3/datasets/WIKI/AAPL.json"
    params = {'api_key': api_key, 'rows': 1}
    
    try:
        response = requests.get(test_url, params=params, timeout=10)
        return response.status_code == 200 and 'dataset' in response.json()
    except:
        return False

def get_token_from_env():
    return os.getenv('QUANDL_API_KEY') or os.getenv('QUANDL_TOKEN')

def main():
    token = 'tzfgtC1umXNxmDLcUZ-5'
    
    if not token:
        sys.exit(1)
    
    is_valid = test_quandl_token(token)
    print("VALID" if is_valid else "INVALID")
    sys.exit(0 if is_valid else 1)

if __name__ == "__main__":
    main()
