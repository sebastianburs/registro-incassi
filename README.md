# Registro Incassi — Dashboard

Dashboard per tracciare incassi della piattaforma libri usati. **Nessun server, nessun database esterno**: tutto il DB sta in un unico file CSV versionato nel repo, `data/registro.csv`. Si modifica dalla pagina e si salva con un bottone — via GitHub o come download.

## Struttura

```
registro-incassi/
├── index.html                dashboard (apri nel browser)
├── data/registro.csv.enc     il database CIFRATO (config, scuole, spese)
├── tools/
│   ├── cifra.py              cifra/decifra il CSV (una tantum, da terminale)
│   └── registro.py          report a schermo (chiede la password)
└── README.md
```

> `data/registro.csv` in chiaro esiste solo in locale ed è in `.gitignore`: nel repo va **solo** il `.enc`.

## Il file `data/registro.csv`

La colonna `tipo` dice cos'è ogni riga:

- `config` → tariffa per copia, costo orario formazione, anno, crescita %/mese
- `scuola` → gestiti, venduti, ricavo, netto, esente (si/no), ore, conta (si/no)
- `spesa`  → nome nella colonna `nome`, importo nella colonna `valore`

## Come si usa

1. Apri `index.html` (in locale, o via GitHub Pages se attivato).
2. Modifica libri gestiti/venduti/ricavo/netto/ore, tariffe, spese. Incasso, formazione, totali e grafici si ricalcolano da soli.
3. Salva:
   - **💾 Salva su GitHub** — fa il commit di `data/registro.csv` direttamente nel repo (serve un token, vedi sotto).
   - **⬇ Scarica CSV** — backup locale, poi lo sovrascrivi/committi a mano.

### Calcoli

- Incasso sistema per scuola = libri venduti × tariffa per copia
- Scuole `esente = si` NON entrano nell'incasso del sistema
- Ricavo formazione = ore × costo orario (solo scuole con `conta = si`)
- Netto sistema = incasso vendite + formazione − spese

## Privacy: dati cifrati, dashboard pubblica

Il repo può essere **pubblico** (hosting GitHub Pages gratis) mantenendo i **dati privati**:

- Nel repo c'è solo `data/registro.csv.enc` — il CSV **cifrato AES-256-GCM**.
- La chiave si deriva da una **password** (PBKDF2-SHA256, 310k iterazioni) che **digiti ogni volta** e **non è salvata da nessuna parte** (né nel codice, né nel repo, né in localStorage).
- Aprendo la dashboard, un gate chiede la password e decifra **nel browser**. Il file `.enc` pubblico è illeggibile senza password.
- `data/registro.csv` (in chiaro) è in `.gitignore`: non va mai committato.

> La sicurezza dipende dalla **forza della password**: usa una passphrase lunga (4-5 parole). Chi scarica il `.enc` può tentare un attacco offline. Se perdi la password, i dati non si recuperano.

### Prima cifratura (una volta)

```bash
python3 tools/cifra.py            # crea data/registro.csv.enc dalla password scelta
# poi elimina il chiaro:
rm data/registro.csv
```

Richiede `pip3 install cryptography`. Per rileggere in chiaro: `python3 tools/cifra.py --decifra`.

## Salvataggio su GitHub (DB dentro GitHub, senza altri sistemi)

Il bottone «Salva su GitHub» usa la **GitHub Contents API** per committare il CSV nel repo. Serve un token personale:

1. GitHub → **Settings → Developer settings → Fine-grained tokens → Generate new token**.
2. Ambito: solo il repo `registro-incassi`. Permesso: **Contents → Read and write**.
3. Copia il token e incollalo nel pannello «Configurazione repository e token» della dashboard.

Il token è salvato **solo nel `localStorage` del tuo browser** e viene inviato esclusivamente a `api.github.com`. Non è mai committato nel repo.

## Hosting con GitHub Pages (opzionale)

Repo → **Settings → Pages** → Source: *Deploy from a branch* → `main` / `(root)` → Save.
> Nota: su piano gratuito Pages funziona solo con repo **pubbliche**. Per una repo **privata** serve GitHub Pro/Team.

## Uso da terminale (opzionale)

```bash
python3 tools/registro.py report   # riepilogo a schermo (chiede la password)
```
