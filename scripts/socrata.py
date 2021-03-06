import typing

import requests

from nycodex import db

BASE = "https://api.us.socrata.com/api/catalog/v1"
DOMAIN = "data.cityofnewyork.us"


def api(path: str, params: typing.Dict[str, str]=None):
    if params is None:
        params = {}
    params.update({
        "domains": DOMAIN,
        "search_context": DOMAIN,
    })

    if path:
        url = "{}/{}".format(BASE, path)
    else:
        url = BASE
    return requests.get(url, params=params)


def get_facets():
    url = "{}/domains/{}/facets".format(BASE, DOMAIN)
    facets = requests.get(url, params={"limit": 10000}).json()
    for facet in facets:  # noqa
        pass


def main():
    db.Base.metadata.create_all(db.engine)

    owners = {}
    datasets = {}

    for category in db.DomainCategory.__members__.values():
        r = api("", params={"categories": category.value, "limit": 10000})
        for result in r.json()['results']:
            owner = result['owner']
            classification = result['classification']
            resource = result['resource']

            owners[owner['id']] = db.Owner(
                id=owner['id'], name=owner['display_name'])
            datasets[resource['id']] = db.Dataset(
                id=resource['id'],
                name=resource['name'],
                description=resource['description'],
                domain_category=classification['domain_category'],
                owner_id=owner['id'])

    print("INSERTING", len(datasets), "datasets")

    db.Owner.upsert(owners.values())
    db.Dataset.upsert(datasets.values())


if __name__ == "__main__":
    main()
