# 4d-plugin-proxy
4D implementation of [libproxy](https://github.com/libproxy/libproxy)

### Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|

### Version

<img src="https://cloud.githubusercontent.com/assets/1725068/18940649/21945000-8645-11e6-86ed-4a0f800e5a73.png" width="32" height="32" /> <img src="https://cloud.githubusercontent.com/assets/1725068/18940648/2192ddba-8645-11e6-864d-6d5692d55717.png" width="32" height="32" />

### Discussion

[libproxy](https://github.com/libproxy/libproxy) reads proxy configuration from system configuration or by using [Web Proxy Auto-Discovery Protocol](https://en.wikipedia.org/wiki/Web_Proxy_Auto-Discovery_Protocol) and [PAC](https://en.wikipedia.org/wiki/Proxy_auto-config)

---

## Syntax

```
GET PROXIES (url;proxies)
```

Parameter|Type|Description
------------|------------|----
url|TEXT|
proxies|ARRAY TEXT|

## Examples

```
$url:="http://www.google.com"

GET PROXIES ($url;$proxies)
```
