# Apps

## ExtIP (External IP CLI)

### Development

#### Service

Running the service

```bash
EXTIP_TOKEN='[ipinfo-token]' moon run extip:run.service
```

#### Client

Running the client

```bash
moon run extip:run.client
```


### Publishing

```bash
moon run extip:version -- [version_update]
moon run extip:publish --dependents
```
