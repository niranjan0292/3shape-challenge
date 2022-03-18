'''
Author: Niranjan Raguraman

Purpose:

The script performs a prerequesite check before making an API call to the GitHub. The REST API calls to GitHub is classified either as 'search' or 'core'(any request that does not access search)and applies appropriate limits.

Inputs:
'--pat', '-p'
    - Mandatory
    - The personal access token for which the limts are to be retrieved
'--url', '-u'
    - Optional
    - The endpoint(or the resource) to be accessed

Output:
    - a zero exit code when there's more than or equal to 10% of the rate limit left
    - a non-zero exit code when there's less than 10% of the rate limit left

Reference:
https://docs.github.com/en/rest/reference/rate-limit#understanding-your-rate-limit-status
https://docs.github.com/en/rest/reference/search#rate-limit

'''

from urllib import error, request
import json
import datetime
import sys
import argparse

api_host = 'https://api.github.com'
rate_limit_endpoint = "/rate_limit"
search_endpoint = '/search'
possiblities = [
    search_endpoint,
    search_endpoint.replace('/', ''),
    api_host+search_endpoint,
    'https://'+api_host+search_endpoint
]


def main(url, pat):

    if not pat.startswith('ghp_'):
        raise ValueError('PAT is not valid')

    if ([i for i in possiblities if url.startswith(i)]):
        category = 'search'
    else:
        category = 'core'

    req = request.Request(
        url=api_host + rate_limit_endpoint,
        method="GET"
    )

    req.add_header("Accept", 'application/vnd.github.v3+json')
    req.add_header("Authorization", 'Bearer ' + pat)
    req.add_header("User-Agent", 'python-niranjan0292')

    try:
        with request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except error.HTTPError as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(1)

    points = data.get('resources').get(category)

    remaining = points.get('remaining')
    limit = points.get('limit')

    pc = int((remaining/limit)*100)

    if pc < 10:
        try_after = datetime.datetime.fromtimestamp(points.get('reset'))
        print('The limit is less that 10 percent({}%). Try after {}'.format(
            pc, try_after))
        sys.exit(1)
    elif pc >= 10:
        print(
            'The limit is at or greater that 10 percent({0}%). We are good to go!'.format(pc))
        sys.exit


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--pat', '-p', help="The Personal Access Token(PAT) the limits are to be checked", type=str)
    parser.add_argument(
        '--url', '-u', help="The endpoint to which the limits are to be verfied. Can look like on of: search or /search/issues or api.github.com/search/issues", type=str, default="/user")
    args = parser.parse_args()
    main(args.pat, args.url)
