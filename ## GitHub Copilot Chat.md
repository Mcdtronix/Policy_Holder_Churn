## GitHub Copilot Chat

- Extension: 0.39.2 (prod)
- VS Code: 1.111.0 (ce099c1ed25d9eb3076c11e4a280f3eb52b4fbeb)
- OS: linux 5.15.0-171-generic x64
- GitHub Account: Mcdtronix

## Network

User Settings:
```json
  "http.systemCertificatesNode": true,
  "github.copilot.advanced.debug.useElectronFetcher": true,
  "github.copilot.advanced.debug.useNodeFetcher": false,
  "github.copilot.advanced.debug.useNodeFetchFetcher": true
```

Connecting to https://api.github.com:
- DNS ipv4 Lookup: 20.87.245.6 (2 ms)
- DNS ipv6 Lookup: Error (52 ms): getaddrinfo ENOTFOUND api.github.com
- Proxy URL: None (3 ms)
- Electron fetch (configured): HTTP 200 (302 ms)
- Node.js https: HTTP 200 (225 ms)
- Node.js fetch: HTTP 200 (299 ms)

Connecting to https://api.githubcopilot.com/_ping:
- DNS ipv4 Lookup: 140.82.113.21 (2 ms)
- DNS ipv6 Lookup: Error (45 ms): getaddrinfo ENOTFOUND api.githubcopilot.com
- Proxy URL: None (24 ms)
- Electron fetch (configured): HTTP 200 (278 ms)
- Node.js https: HTTP 200 (877 ms)
- Node.js fetch: HTTP 200 (876 ms)

Connecting to https://copilot-proxy.githubusercontent.com/_ping:
- DNS ipv4 Lookup: 20.250.119.64 (48 ms)
- DNS ipv6 Lookup: Error (41 ms): getaddrinfo ENOTFOUND copilot-proxy.githubusercontent.com
- Proxy URL: None (46 ms)
- Electron fetch (configured): HTTP 200 (694 ms)
- Node.js https: HTTP 200 (717 ms)
- Node.js fetch: HTTP 200 (769 ms)

Connecting to https://mobile.events.data.microsoft.com: HTTP 404 (275 ms)
Connecting to https://dc.services.visualstudio.com: HTTP 404 (1137 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (927 ms)
Connecting to https://copilot-telemetry.githubusercontent.com/_ping: HTTP 200 (894 ms)
Connecting to https://default.exp-tas.com: HTTP 400 (787 ms)

Number of system certificates: 434

## Documentation

In corporate networks: [Troubleshooting firewall settings for GitHub Copilot](https://docs.github.com/en/copilot/troubleshooting-github-copilot/troubleshooting-firewall-settings-for-github-copilot).