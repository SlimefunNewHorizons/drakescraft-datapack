# Stellarity void predicate runtime probe

The void predicate must use `condition` in the overlay selected by Minecraft.
The base file in Stellarity 6.0.1 still uses `type`; checking that file alone
incorrectly reports a problem when the applicable overlay is valid. The probe
copies `pack.mcmeta` and all versions of `location/in_void.json` byte for byte
into a minimal datapack, so Minecraft selects its own overlay.

Run on a host with Java 25 and an existing Paper 26.2 bootstrap directory:

```sh
python3 scripts/probe_stellarity_predicate.py \
  --archive /path/to/Stellarity-6.0.1.zip \
  --server-home /path/to/stopped-staging \
  --server-jar /path/to/paper-26.2.jar \
  --work-dir /path/to/new-disposable-directory
```

On a shared host, run through its build lock and resource limiter. The probe
itself does not acquire a host-wide lock. It binds to loopback with an ephemeral
port, enables online mode and a whitelist, disables RCON, and loads no plugins.
The work directory must not already exist. Only bootstrap dependencies are copied
from the supplied server home; its worlds and configurations are never used.

The test requires a successful boot, actual console responses for true at Y = -65
and -64 and false at Y = -63, zero logged ERROR entries, a completed save, and exit
code 0. Missing, duplicated or echoed responses fail validation. `result.json`
records the archive, bootstrap JAR and predicate SHA-256 hashes; `console.log`
retains runtime evidence. A shutdown timeout leaves the process for investigation
instead of killing it during a save. After a clean shutdown, remove only the
disposable directory when its evidence has been archived.

If the command pipe breaks or is already closed, the probe still waits for the
child process and writes `result.json`. The `failure` field preserves the original
command error and any shutdown-command or timeout errors. A failed shutdown
command always fails the probe, even if all predicate checks passed and the child
later exits with code 0. The probe never terminates or kills a child during a save.

Measured on 2026-11-25: Paper 26.2 build 133 / Java 25 started in 29.522 seconds,
passed all three boundary checks, saved and exited with code 0. There were zero
ERROR entries and two WARN entries advising that this Paper build is outdated;
the JVM also emitted JOML Unsafe deprecation notices. The checked ZIP SHA-256 was
`854168e96af0045067323ab4f67c359e013af9b6d9587d8b43d27c294ec6e3c6`.

This isolates the shipped predicate and overlay selection. It does not validate
the full pack, plugin interactions, a running production registry, or another
Minecraft version. It does not install, patch or reload a production datapack.
