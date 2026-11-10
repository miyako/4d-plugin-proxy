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

## Versioning and publication

### Native ownership regression checks

The unsigned, offline ownership harness compiles the actual dispatcher, all
sixteen class implementations and the complete unchanged bundled SDK:
`python3 .github/tests/test_ownership.py` on macOS. Proxy discovery, network,
PAC and platform-path operations are replaced with synthetic boundaries;
the project/release build is not invoked. See the [audit inventory and
contracts](.github/tests/ownership-audit.md) for immutable baseline comparison,
owner balances and explicit SDK OOM, metadata, Windows and 4D-host limits.

### Release operations

**Bump version** is manual and source-only. Select an explicit branch in Actions
(or `gh workflow run bump-version.yml --ref <branch> -f mode=patch`, with `minor`
and `major` also supported). It checks out the immutable dispatch `github.sha`,
validates a clean checkout and exact remote branch tip, commits one direct-child
version change, and pushes only that branch without force or followed tags.
The mandatory executable `.github/scripts/bump-hooks/pre-push` guard validates
exactly one advertised update: its old SHA must be the selected SHA and its
literal new SHA must be HEAD with exactly that one parent. Late advance,
ancestor rewind, deletion and same-result races fail closed. Missing or
nonexecutable guards are checked both initially and immediately before push.
No tag, Build or publication is triggered by a bump.

**Build** is a separate manual, zero-input workflow:
`gh workflow run release.yml --ref <branch>`. All three checkouts use the
selected immutable `github.sha`; strict source `X.Y.Z` determines `vX.Y.Z`
and the `PROXY-X.Y.Z.zip` / `PROXY-X.Y.Z.dmg` assets. There is no tag/push/PR
trigger or new branch restriction. Publication uses one repository-wide
cross-branch concurrency group and never cancels a running build.

The original bump workflow header at `7520b20` explicitly promised coordinated
`MARKETING_VERSION` / `CURRENT_PROJECT_VERSION`. Its marketing-first
implementation left current settings behind through `474df39` (`1.0.3`).
Source authority is the three marketing settings and source `Info.plist`
at `1.0.3`; this migration repairs three stale current settings (`1.0.0`) and
the source English display/info strings (`1.0`) to that existing version,
without a release increment. Future bumps validate and co-bump all applicable
literal fields in `PROXY.xcodeproj/project.pbxproj`, `Info.plist` and
`English.lproj/InfoPlist.strings`. Supported Xcode references stay references;
absent `CFBundleVersion` stays absent. Other bytes, BOM, line endings and
permissions are preserved. Prebuilt bundle metadata, 4D data/schema and
localization counters, manifests, native dependencies and API files are excluded.

Build retains Windows x64 MSBuild (v143 / Windows SDK 10.0 overrides, committed
`lib/64` dependencies and `ws2_32.lib`), then universal macOS Xcode with committed
`a/libproxy.a` / `a/libmodman.a`, SystemConfiguration and JavaScriptCore.
The macOS path keeps prebuilt checks, fresh universal binary/resource verification,
Windows artifact merge, Developer ID signing/verification, ZIP/DMG packaging,
both notarization submissions and DMG stapling before publication. The original
prebuilt path scanner only matches explicit `a/...` or `lib/...` paths; this
project's libraries use group-relative paths. Xcode linking and universal binary
verification remain the actual gates; the scanner is not a comprehensive
architecture audit. Native builds and signing/notarization require their runners
and credentials and are not run by the Python lifecycle tests.

Signing uses the unchanged secret names `APPLE_DEVELOPER_ID_CERTIFICATE`,
`APPLE_DEVELOPER_ID_CERTIFICATE_PASSWORD`, `KEYCHAIN_PASSWORD`,
`NOTARYTOOL_APPLE_ID`, `NOTARYTOOL_TEAM_ID` and `NOTARYTOOL_PASSWORD`.

### Create-only release safety and recovery

Before native work and again after every build/sign/notary/staple gate, publication
checks the remote tag and authenticated, paginated release list including drafts.
Every page and entry is validated. Authentication, 404, network, malformed data
or later-page failures stop publication; only a complete successful no-match
scan permits creation.

Publication POSTs a new tag ref at the selected SHA (a same-SHA concurrent
creation also fails), verifies the remote SHA, then POSTs a new public,
non-prerelease release with the explicit tag, target SHA, name and empty body
(the original notes policy). Assets are separately POSTed to the newly returned
release ID. There is no release updater, asset clobber, DELETE, rollback or retry.

If anything fails after creation, **the tag, release and any uploaded assets
remain**. Inspect the reported selected SHA, tag and release ID in the run log
and the repository's tags/releases before taking action. A rerun for the same
version intentionally fails if any tag or draft/published release remains.
Recovery is an explicit maintainer decision outside automation: retain the
partial record, or separately investigate and authorize any manual cleanup;
then choose a new source version through Bump if a new publication is needed.
Never assume a failed API response means no remote object was created.

Local lifecycle checks (no native/signing execution):
`python3 -B -m unittest discover -s .github/tests` and
`actionlint .github/workflows/*.yml`.
