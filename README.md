# 4d-plugin-proxy

PROXY tells you which proxy servers to use to reach a given URL. It wraps [libproxy](https://github.com/libproxy/libproxy) (linked into the plugin), which reads the system's proxy configuration and, where configured, evaluates a [PAC](https://en.wikipedia.org/wiki/Proxy_auto-config) script or locates one with [WPAD](https://en.wikipedia.org/wiki/Web_Proxy_Auto-Discovery_Protocol). The result is a text array of proxy URLs, in the order they should be tried.

| Command | Returns | Purpose |
|---|---|---|
| [GET PROXIES](#get-proxies) | `ARRAY TEXT` (in parameter 2) | List the proxies to use for a URL, in order of preference |

**Platforms:** macOS (Apple silicon and Intel), Windows (64-bit)

---

## Requirements & platform notes

- **One command, two mandatory parameters.** `GET PROXIES` reads the URL from parameter 1 and writes the result into the text array passed as parameter 2 (`GET PROXIES(&T;&Y)` in the manifest). There is no return value.
- **The call blocks until libproxy answers.** Reading the system settings is fast, but when the configuration uses a PAC file that isn't cached yet, libproxy downloads it first, and a PAC script can itself make DNS lookups. The calling 4D process waits for all of this. Call it once and keep the result rather than calling it in a tight loop.
- **Failure is silent, not a 4D error.** If libproxy can't produce an answer, you get an empty array (size 0) and no 4D error. See [Error handling & troubleshooting](#error-handling--troubleshooting).
- **Platform support depends on the libproxy build linked into the plugin.** **On macOS**, the plugin links SystemConfiguration and JavaScriptCore, which libproxy uses to read the network settings and to run PAC scripts. **On Windows**, libproxy reads the system (Internet Options) proxy settings; whether this build can evaluate PAC scripts has not been verified.
- **Preemptive processes:** the manifest doesn't declare the command thread-safe, so expect 4D to treat it as unusable in preemptive processes.

---

## GET PROXIES

### Syntax

```
GET PROXIES ( url ; proxies )
```

| Parameter | Type | Description |
|---|---|---|
| `url` | Text | The URL you want to reach, e.g. `"http://www.example.com"` |
| `proxies` | ARRAY TEXT | Receives the proxies to try, in order (element 0 is unused) |
| Result | — | None. The result is written into `proxies` |

### Description

`GET PROXIES` asks libproxy which proxies apply to `url` and fills `proxies` with one entry per proxy, starting at element 1. If the first proxy fails, try the second, and so on.

Each entry is a URL-like string. The forms libproxy documents are:

| Entry | Meaning |
|---|---|
| `direct://` | Connect directly, without a proxy |
| `http://[user:password@]host:port` | HTTP proxy |
| `socks://[user:password@]host:port` | SOCKS proxy: try version 5, then fall back to version 4 |
| `socks4://…`, `socks5://…` | SOCKS proxy of that version only |
| `<protocol>://…` | Another proxy protocol (for example an RTSP proxy configured in macOS) |

The user name and password are only present when they are part of the system configuration. Treat the array as sensitive if they are.

`proxies` must be a text array or an undefined variable (which becomes a text array). If you pass an array of another type, it is left untouched.

The plugin creates one libproxy "factory" when it loads and keeps it until 4D quits. libproxy caches the configuration and any downloaded PAC file in that factory, so later calls are faster than the first one.

### Example

From the original README:

```4d
$url:="http://www.google.com"

GET PROXIES ($url;$proxies)
```

Pick the first entry, or connect directly when there is none:

```4d
ARRAY TEXT($proxies;0)
GET PROXIES("https://www.example.com";$proxies)

If (Size of array($proxies)>0)
	$proxy:=$proxies{1}
Else 
	$proxy:="direct://"
End if 

If ($proxy="direct://")
	// connect without a proxy
Else 
	// use $proxy as the proxy server
End if 
```

---

## Error handling & troubleshooting

- **Empty array.** libproxy returned no answer (an unrecoverable error inside libproxy), or the plugin failed to initialise it. No 4D error is raised. Treat an empty array like `direct://`, or report it, as suits your application.
- **The first call takes a long time.** The system configuration points to a PAC file (or WPAD is enabled) and libproxy is downloading and evaluating it. Later calls use the cached copy.
- **The array isn't filled.** `proxies` was declared as another array type (for example `ARRAY LONGINT`). Declare it with `ARRAY TEXT`.
- **Results differ from what a browser uses.** libproxy reads the system-wide settings. An application with its own proxy settings (some browsers) can behave differently.

---

## Quick reference

```4d
ARRAY TEXT($proxies;0)
GET PROXIES("http://www.example.com";$proxies)
// $proxies{1}: "direct://" or "http://host:port", ...
```
