#!/usr/bin/env bash
set -e
echo "En attente de la MyriadX bootée (03e7:f63b)…"
# On attend la périphérique booté (PID f63b)
while ! lsusb | grep -q "03e7:f63b"; do
  sleep 0.1
done
echo "MyriadX bootée détectée, lancement de test_blob.py"
exec python3 test_blob.py
