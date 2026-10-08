import os, subprocess
# Production scheduling hook. Configure your host scheduler to call:
# POST /api/cron/sync with X-Cron-Secret.
# This keeps scheduling provider-neutral.
