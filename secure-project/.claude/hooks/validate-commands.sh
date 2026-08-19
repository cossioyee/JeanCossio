#!/bin/bash

# Read the JSON payload from stdin
INPUT=$(cat)

# Extract the command from the tool input
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty')

# Block dangerous rm -rf patterns
if echo "$COMMAND" | grep -qE 'rm\s+-rf\s+(/|\*)'; then
  echo "Blocked: dangerous rm -rf detected" >&2
  exit 2
fi

# Block pipe-to-shell patterns
if echo "$COMMAND" | grep -qE '\|\s*(sh|bash|zsh)'; then
  echo "Blocked: pipe-to-shell pattern detected" >&2
  exit 2
fi

# Block SQL injection patterns
if echo "$COMMAND" | grep -qiE '(DROP\s+TABLE|DELETE\s+FROM)'; then
  echo "Blocked: SQL injection pattern detected" >&2
  exit 2
fi

# Block bash writes to .env files
if echo "$COMMAND" | grep -qE '(>>|>).*\.env'; then
  echo "Blocked: bash write to .env file detected" >&2
  exit 2
fi

exit 0
