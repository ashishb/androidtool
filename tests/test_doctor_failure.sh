if python src/main.py doctor --verbose; then
  exit 1  # The command should have failed
else
  exit 0  # The command failure is expected
fi
