# 4d-plugin-proxy
4D implementation of [libproxy](https://github.com/libproxy/libproxy)

### Platform

| carbon | cocoa | win32 | win64 |
|:------:|:-----:|:---------:|:---------:|
|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|<img src="https://cloud.githubusercontent.com/assets/1725068/22371562/1b091f0a-e4db-11e6-8458-8653954a7cce.png" width="24" height="24" />|

### Version

<img src="https://cloud.githubusercontent.com/assets/1725068/18940649/21945000-8645-11e6-86ed-4a0f800e5a73.png" width="32" height="32" /> <img src="https://cloud.githubusercontent.com/assets/1725068/18940648/2192ddba-8645-11e6-864d-6d5692d55717.png" width="32" height="32" />

### Discussion

WPAD, or [Web Proxy Auto-Discovery Protocol](https://en.wikipedia.org/wiki/Web_Proxy_Auto-Discovery_Protocol) is used with [DNS](https://en.wikipedia.org/wiki/Domain_Name_System) to locate the [PAC](https://en.wikipedia.org/wiki/Proxy_auto-config) file. the format of the returned proxy strings are as follows:

 * http://[username:password@]proxy:port
 * socks://[username:password@]proxy:port
 * socks5://[username:password@]proxy:port
 * socks4://[username:password@]proxy:port
 * direct:// (default)

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
