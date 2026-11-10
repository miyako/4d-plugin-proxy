# Proxy native ownership audit

## Immutable scope and provenance

Baseline: `7ff8aeb1ce1d8a582f290f2c366dc79315ed6be2` on `master`.
Guidance: `miyako/skills`, `4d-skills/skills/4dplugin/SKILL.md` at
`e6b492fcb81e5e1a7f7db723594b420e63bf6eb9`, read via immutable Contents API.
Issue: miyako/4d-plugin-proxy#5.

The complete bundled engine/ABI files remain unchanged:

| File under `4D Plugin API/` | Git blob |
|---|---|
| `4DPluginAPI.c` | `29788ed041effaf67269ccd93f971e8aee2ce5f8` |
| `4DPluginAPI.h` | `1854e9db452592498ad9047d8e1ffa46df75b795` |
| `4DPluginAPI.def` | `996ecc4ab11ad165de9192eba2e7478db141c757` |
| `EntryPoints.h` | `730f2f77ff2713fb2fe4b7d6562baeedf5f664cb` |
| `Flags.h` | `10a83185333dac06a62dda61b9f9428243d1e2ee` |
| `PrivateTypes.h` | `77053dc0c0a3718d2d3b6f158371a6af78c6ae66` |
| `PublicTypes.h` | `2bb392e73e9c556c274fe0a75b3a6b83e310b77c` |

The implementation labels itself v14, the header/flags v13. These are file
comments, not a verified upstream SDK release identifier. The test runner
checks all seven blob identities before compilation. It compiles the entire
unchanged `4DPluginAPI.c`, not extracted functions or replacement PA APIs.

Harness/RAII prior art was read as immutable individual files from
`miyako/4d-plugin-ping` at `95bd88353008cf9ca212bae362ce3ea6fa271b95`:
`ownership_host.mm`, `ownership_platform.h`, `test_ownership.py`,
`CommandArguments.h`, `C_PICTURE.cpp`, and `C_POINTER.cpp`. The proxy-specific
SDK blobs, forwarding, dispatcher and fixtures were independently checked;
no other checkout/project was created and no previous test results reused.

## Complete tracked native/build inventory

`git ls-files` inventories one dispatcher, one SDK implementation, sixteen
class implementations, their headers, the ABI headers above, the export
definition, `4D Plugin_Prefix.pch`, and `include/proxy.h`. No additional
tracked `.c`, `.cpp`, `.m` or `.mm` implementation exists at baseline.
This indexed absence is an inventory fact, not a proof of runtime safety.

All sixteen class `.cpp` files below, `4DPlugin.cpp`, and `4DPluginAPI.c`
belong to the Xcode Sources phase and both `PROXY.vcxproj` and
`PROXY.vc10.vcxproj`. Header-only helpers are included by their callers;
adding `CommandArguments.h` requires no project-membership edit.
The source extension `.c` is compiled as C++/Objective-C++ in this project,
including repository-specific C_TEXT overloads. The harness compiles every
actual implementation and the Objective-C wrapper branches.

| Native surface | Ownership trace / disposition |
|---|---|
| `4DPlugin.cpp`, `4DPlugin.h` | One exported command `GET_PROXIES`; URL copied into C_TEXT then UTF-8 before the synchronous proxy query. Every returned C string is copied into ARRAY_TEXT before `px_proxy_factory_free_proxies`. Startup owns one factory; exit-process shutdown frees it. No scalar PA string struct assignment here. |
| `Classes/ARRAY_TEXT.{cpp,h}` | Borrowed element descriptors are immediately copied into independent C++ strings. Output creates a fresh PA string for every element, including element zero, then transfers it once without post-transfer disposal. Existing replacement/shrink/clear semantics preserved. Resize failure remains deferred below. |
| `Classes/C_TEXT.{cpp,h}` | Scalar input copied into C++ storage; parameter and result setters call `PA_SetUnistring`, not `PA_SetStringVariable`. UTF-8 conversion has explicit lengths; Objective-C path/URL copies have independent Foundation owners. No blanket disposal removal. |
| `Classes/C_PICTURE.{cpp,h}` | Compiled but not called by GET PROXIES. Audit includes path, bytes, conversions, grayscale, dimensions, thumbnail, parameter/result handoffs, native image and representation-cache helpers. Confirmed ownership/unit fixes below; undocumented successful metadata ownership explicitly deferred. |
| `Classes/C_POINTER.{cpp,h}` | Compiled but not called by GET PROXIES. `fromParamAtIndex` borrows pointer descriptors. `getVariable` fetches an owning value, copies the existing reference-metadata fields and now clears the fetched owner; failed lookup checked before reading output. Existing field/reference representation is intentionally not redesigned. |
| `Classes/C_BLOB.{cpp,h}` | CBytes owns vector storage; parameter handles borrowed/copied on input, independently created/transferred on output. Hex/base64 routes use C_TEXT content copies; no PA string alias transfers. Broader blob parsing/cache semantics not changed. |
| `Classes/ARRAY_BOOLEAN.{cpp,h}` | C++ bit vector; PA boolean array input/output, no string allocations. |
| `Classes/ARRAY_DATE.{cpp,h}` | C++ date vector; date array input/output, no string allocations. |
| `Classes/ARRAY_INTEGER.{cpp,h}` | C++ short vector; integer array input/output, no string allocations. |
| `Classes/ARRAY_LONGINT.{cpp,h}` | C++ integer vector; longint array input/output, no string allocations. |
| `Classes/ARRAY_REAL.{cpp,h}` | C++ double vector; real array input/output, no string allocations. |
| `Classes/ARRAY_TIME.{cpp,h}` | C++ integer vector; time array input/output, no string allocations. |
| `Classes/C_DATE.{cpp,h}` | Date fields copied by value; no string owners. |
| `Classes/C_INTEGER.{cpp,h}` | Short value copied by value; no string owners. |
| `Classes/C_LONGINT.{cpp,h}` | Integer value copied by value; no string owners. |
| `Classes/C_REAL.{cpp,h}` | Double value copied by value; no string owners. |
| `Classes/C_TIME.{cpp,h}` | Time value copied by value; no string owners. |
| `Classes/C_TYPES.h` | CUTF16String/CUTF8String and vector aliases; no independent PA owner/destructor. |
| `4DPluginAPI.{c,h,def}`, `EntryPoints.h`, `Flags.h`, `PrivateTypes.h`, `PublicTypes.h` | Protected engine entry points, variable/array implementation, packed ABI and export definition; exact blobs above, unchanged. |
| `4D Plugin_Prefix.pch` | Carbon prefix include, no ownership helper. |
| `include/proxy.h` | Four public libproxy factory/query/free declarations and synchronous result-ownership documentation. Real implementation exists only in prebuilt libraries. |

Both `manifest.json` and the bundle Resources copy are byte-identical:
`GET PROXIES(&T;&Y)`, one scalar text input and one text-array output, no
return. `documentation.htm` redirects to the bundled documentation, which describes
this same surface, as does README. No manifest/export/build-membership/binary
changes were made.
There are no plugin object/collection getter/setter wrappers or corresponding
SDK object/collection APIs in this inventory. Their owner balances are
reported as **n/a**, not zero verified operations. Prebuilt `.a`, `.lib`,
`.4DX` and DLL files are not treated as audited source or executed.

## Exact local contracts

Relevant line references below refer to the immutable baseline SDK.

- `PA_CreateUnistring` (244-250), `PA_DisposeUnistring` (252-260), and
  `PA_SetUnistring` (263-270) forward engine creation/disposal/content
  replacement. Struct assignment never makes a character-buffer copy.
- `PA_CreateVariable` (3523 onwards) allocates an empty owner for strings and
  pictures; Undefined initializes the discriminant without an owned payload.
  `PA_SetStringVariable` (3826 onwards) shallowly replaces the descriptor
  without clearing the previous owner. `PA_SetPictureVariable` is also
  shallow. Therefore overwriting initialized empty owners leaks them.
- `PA_GetStringInArray` (4266-4286) returns a borrowed descriptor.
  `PA_SetStringInArray` (4444-4460) disposes the old element and shallowly
  transfers the incoming descriptor only when kind is ArrayUnicode, data is
  non-null, index is **0 through count inclusive**, and descriptor is
  non-null. Rejected calls do not transfer. Copy before replacement or reuse.
- `PA_GetPictureVariable` explicitly returns a borrowed picture. Creation
  provides an owner; `PA_DuplicatePicture(p, 1)` retains one reference
  (447-455). Caller-owned output references must survive clearing command
  argument owners.
- `PA_ConvertCharsetToCharset` (4776 onwards) forwards input length and
  destination capacity as bytes and returns the engine's output byte count.
  UTF-16 wrapper lengths are code units: divide bytes by
  `sizeof(PA_Unichar)`. Test conversions reserve an additional terminator
  and return content bytes excluding it.
- `PA_ExecuteCommandByID` (5257 onwards) returns the engine result separately
  from arguments, uses a temporary handle of argument pointers, and sets
  `PA_GetLastError`. Handle creation failure returns raw `fType == 0`;
  `PA_GetVariableKind` normalizes this to string, so kind inspection is not
  an error check. Failed engine output is unspecified and not adopted or
  cleared. Successful separate result owners are cleared.
- `PA_GetPointerValue` (2035 onwards) returns an owning value on success;
  the header explicitly requires `PA_ClearVariable`. Failed output must
  not be interpreted, copied or cleared.

## Surgical fixes

`CommandArguments` initializes arguments Undefined, owns only successfully
installed values, and clears each exactly once on success or exception.
Checked picture creation never installs an unspecified failed picture.
Checked command execution saves the error before any other SDK calls,
throws with command/error context on failure, and clears the separate
successful result. Argument cleanup does not inspect failed return output.
The synchronous fixture keeps independent argument owners valid on failure.

`fromFileAtPath` transfers the fresh path descriptor into its sole argument
owner instead of overwriting an empty string or disposing its alias twice.
It retains the output through `setPicture` before argument cleanup.
`setBytes` releases the temporary creation owner after the wrapper retains.
`createCopy` corrects byte/code-unit length and checks conversion failure
before constructing the format string. Copy/grayscale/thumbnail return an
independently retained picture before clearing the output argument.
Dimension/thumbnail input arguments retain the wrapper's borrowed picture
instead of overwriting an allocated empty picture or clearing a borrowed
owner. `C_POINTER::getVariable` checks the error before copying the existing
metadata and disposes its successful fetched owner. No API/ABI rewrite.

The helpers now throw `std::runtime_error` rather than returning apparently
successful outputs on these failures. They are dormant under the current
command export; the existing dispatcher's broad catch and GET PROXIES
failure behavior are not changed by this patch.

## Reproducible isolated evidence

Run on macOS with the installed compiler:

```sh
python3 .github/tests/test_ownership.py
```

For comparison, extract **only** baseline native source into a separate
artifact directory and point the **same final harness** at it:

```sh
git archive 7ff8aeb1ce1d8a582f290f2c366dc79315ed6be2 \
  '4D Plugin API' 4DPlugin.cpp 4DPlugin.h include | tar -x -C "$BASELINE"
OWNERSHIP_SOURCE_ROOT="$BASELINE" python3 .github/tests/test_ownership.py
```

Local execution: Apple clang 21.0.0, arm64, Darwin 25.6.0; ASan and UBSan.
Alignment sanitizer alone is disabled for this SDK's explicit two-byte-packed
ABI. LeakSanitizer is disabled on macOS; explicit allocation/reference maps
enforce string/picture/handle balance at every successful leaf exit.

| Final harness category | Leaves | Baseline passes | Fixed passes |
|---|---:|---:|---:|
| Path/copy: ASCII, BMP, supplementary, empty; allocated/null empty engines | 16 | 0 | 16 |
| Picture bytes/grayscale/size/thumbnail handoffs | 4 | 0 | 4 |
| Array copy/churn/replacement/shrink/clear/rejection | 2 | 2 | 2 |
| Scalar input independence and content-setter output lifetimes | 8 | 8 | 8 |
| Command-handle/command/conversion/picture-creation failures | 14 | 0 | 14 |
| SDK failure predicates (not OOM certification) | 1 | 1 | 1 |
| Successful separate results: Undefined/string/picture, five commands | 15 | 0 | 15 |
| Pointer owning lookup and poisoned failure output | 2 | 0 | 2 |
| Actual offline dispatcher, six modes, two empty-string engines | 12 | 12 | 12 |
| **Total** | **74** | **23** | **74** |

Baseline: **51 failed leaves**. Named failures include
`duplicate/unowned string disposal` in path tests, ASan heap-buffer-overflow
in ASCII copy tests, `independently retained return` for repeated bytes,
unbalanced string/picture owners, missing surfaced command/pointer errors,
and disposing failed picture-creation poison. Fixed: **74/74**, each success
reports `strings=0 pictures=0 handles=0 objects=n/a collections=n/a`.
These are synthetic host results, not a reproduced 4D or Windows crash.

The array controls cover accepted index zero, distinct owned elements,
borrowed-to-C++ copying before mutation, churn and twenty rewrites, shrink,
clear, Undefined destinations, and wrong kind/null data/negative or excessive
index/null descriptor rejection. Scalar controls verify the original input
can change and the wrapper can die before reading independent outputs.
Unicode checks assert exact UTF-16 content, code-unit counts, byte capacity
and terminators; supplementary fixtures contain a surrogate pair.

The actual dispatcher is compiled and called, not reimplemented. All four
libproxy entry points are renamed by a forced-include header **before every
translation unit** and implemented synthetically. No real libproxy/modman
library or SystemConfiguration/JavaScriptCore framework is linked. A query
accepts only `https://synthetic.invalid/path`, never resolves it, and returns
synthetic direct/ASCII/BMP/supplementary/empty proxy strings. Twenty repeated
calls per leaf cover normal/empty/null result, factory initialization failure,
Undefined output and wrong-kind output. Exact query/free counts are asserted;
all result arrays and the factory are released before exit. URL/path/native
image classes/functions are redirected to in-memory stubs, so dormant
compiled helpers cannot access real files/URLs through those boundaries.

An `nm -u` import gate runs before dispatch and rejects network/DNS/proxy,
system configuration/PAC, URL, process-launch and platform-file boundaries.
No engine callback falls through: unexpected selectors/commands terminate
the test. There are no actual DNS queries, sockets, packets, PAC evaluation,
proxy discovery/configuration reads or writes, or private/user fixtures.

## Non-release boundary and explicit deferrals

Before validation, both workflows, release/bump scripts, Xcode phases and
Windows memberships/settings were read. Existing Build and Bump version
workflows are **manual only**. Build signs, packages, notarizes and publishes;
it was not run. The Xcode target includes resource/copy/Rez phases, a bundle
output and signing identity; no project build was used. No release, tag,
signing, notarization, packaging, binary upload or manual dispatch occurs.
New `Ownership` CI is read-only, unsigned, `macos-latest`, relevant-path-only,
with push filters for the exact audit branch and `master`, plus matching
pull requests. It runs only the isolated harness above.

- **SDK resize/OOM:** `PA_ResizeArray` (3973 onwards) updates logical count
  even after `PA_SetHandleSize` fails. The harness deliberately fails resize,
  verifies physical bytes stay unchanged while logical count advances, and
  restores only its test descriptor for cleanup. It does not then run the
  unsafe wrapper over that descriptor. A reliable preservation boundary
  across void wrappers and the protected SDK needs a separate design.
  Successful tests do not certify OOM behavior.
- **Unistring allocation failure:** this SDK's create/set string functions
  do not provide a reliable refreshed error status or transactional
  allocation-failure contract. No speculative SDK rewrite, silent empty
  success fallback, or claim of allocation-failure preservation is made.
- **Picture metadata:** `PA_GetPictureData` forwards an engine string but
  this exact header/implementation does not state whether a successful
  representation/type string is owning or borrowed. `_GetCount` and
  `loadImageOfType` successful metadata cleanup are not guessed. The shim
  returns an error and poison there; these tests verify no access/cleanup of
  failed metadata, not success metadata correctness.
- **Other platform/host boundaries:** Windows/MSVC, actual 4D execution and
  exact host engine failure mutation/retention guarantees remain unexecuted.
  ABI behavior is the bundled packed interface on the executed macOS
  architecture, not cross-platform certification.
- **Opaque native libraries:** bundled libproxy/modman and shipped native
  binaries are not source-audited or exercised. Dispatcher tests certify
  only copying and ownership across the documented synthetic result boundary.
