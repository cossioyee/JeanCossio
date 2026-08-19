#!/bin/bash

# Read the JSON payload from stdin
INPUT=$(cat)

# Extract the file_path from the tool input
FILE_PATH=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Define protected file patterns
PROTECTED_PATTERNS=(".env" "package-lock.json" ".key" ".git/" "secrets/")

# Check if the file matches any protected pattern
for pattern in "${PROTECTED_PATTERNS[@]}"; do
  if [[ "$FILE_PATH" == *"$pattern"* ]]; then
    echo "Blocked: $FILE_PATH matches protected pattern '$pattern'" >&2
    exit 2
  fi
done

exit 0
