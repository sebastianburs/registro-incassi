#!/bin/bash
# Doppio-click per aprire il Registro Incassi in locale.
# Avvia un piccolo server (serve per leggere data/registro.csv.enc) e apre il browser.
cd "$(dirname "$0")"
PORT=8765
echo "Registro Incassi — server locale su http://localhost:$PORT"
echo "Tieni aperta questa finestra mentre lavori. Chiudila per fermare."
python3 -m http.server "$PORT" >/dev/null 2>&1 &
SRV=$!
sleep 1
open "http://localhost:$PORT/index.html"
trap 'kill $SRV 2>/dev/null' EXIT
wait $SRV
