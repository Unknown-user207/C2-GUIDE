# Stealth Techniques for C2

## Domain Fronting
- Use a legitimate CDN domain (e.g., Cloudflare)
- Hide the real C2 domain behind it
- Traffic looks like normal web requests

## Jittered Beacons
- Randomize polling intervals (e.g., 10-15 seconds)
- Avoid predictable patterns
- Mimic human-like behavior

## Killswitch
- Check for specific environment variables or files
- If not found, self-destruct (delete files, stop service)
- Prevents analysis in sandboxes

## Polymorphic Payloads
- Change code structure on each build
- Different variable names, junk code, reordering
- Evades signature-based antivirus