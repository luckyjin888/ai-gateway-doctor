# OpenClaw

OpenClaw can run multiple profiles intentionally. Do not stop duplicates based only on process count.

For each gateway process, establish:

- profile/config root;
- port;
- bot identity;
- intended channel;
- service supervisor;
- whether another process polls the same token.

Warn on multiple gateways, then distinguish intentional profile isolation from accidental duplication. Never copy one profile's bot token into another agent without verifying bot identity and ownership.

