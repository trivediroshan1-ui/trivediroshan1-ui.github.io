# Pyodide, self-hosted copy

- Version: 0.26.4 (the lock file says so, and so does pyodide.js).
- Release: https://github.com/pyodide/pyodide/releases/tag/0.26.4 (the "core" package, pyodide-core-0.26.4).
- Used by: /ca-mfa-lab/virtual-lab/run/ (runs the lab scripts in the browser, nothing leaves the device).

SHA-256 of the five files in this folder (also in SHA256SUMS, which the check workflow verifies on every pull request):

| File | SHA-256 |
|---|---|
| pyodide-lock.json | cd50b49de944c579045e122fe8628b31f9ce446379f032f36c05e273d38766e0 |
| pyodide.asm.js | 919560652ed3dad3707cb3a394785da1e046fb13dc0defa162058ff230cb7eed |
| pyodide.asm.wasm | b7e66a19427a55010ac3367c1b6c64b893f9826f783412945fdf0c3337f3bc94 |
| pyodide.js | c0069107621d5b942a659e737a12e774cc0451feaa2256f475d72e071d844ec7 |
| python_stdlib.zip | 72894522b791858b9d613ac786b951d8b5094035dcf376313ea24a466810f336 |

These are the hashes of the files as committed. They show the files have not changed since they were added; they do not by themselves prove the files match the published release. To check that once, download pyodide-core-0.26.4.tar.bz2 from the release page, unpack it and compare each file with `sha256sum`.

To update: replace the five files, change the version above, regenerate SHA256SUMS (`sha256sum pyodide-lock.json pyodide.asm.js pyodide.asm.wasm pyodide.js python_stdlib.zip > SHA256SUMS` inside this folder) and update the table.
