from .base import BaseModule


class azure_realm(BaseModule):
    watched_events = ["DNS_NAME"]
    produced_events = ["DNS_NAME"]
    flags = ["affiliates", "subdomain-enum", "cloud-enum", "web-basic", "passive", "safe"]
    meta = {"description": 'Retrieves the "AuthURL" from login.microsoftonline.com/getuserrealm'}

    async def setup(self):
        self.processed = set()
        return True

    async def handle_event(self, event):
        _, domain = self.helpers.split_domain(event.data)
        domain_hash = hash(domain)
        if domain_hash not in self.processed:
            self.processed.add(domain_hash)
            auth_url = await self.getuserrealm(domain)
            if auth_url:
                self.emit_event(auth_url, "URL_UNVERIFIED", source=event, tags=["affiliate", "ms-auth-url"])

    async def getuserrealm(self, domain):
        url = f"https://login.microsoftonline.com/getuserrealm.srf?login=test@{domain}"
        r = await self.helpers.request(url)
        if r is None:
            return
        try:
            json = r.json()
        except Exception:
            return
        if json and isinstance(json, dict):
            return json.get("AuthURL", "")
