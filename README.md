# Registro Incassi — Dashboard locale

Dashboard per tracciare incassi della piattaforma libri usati. Gira **solo in locale**, nessun server esterno. Il database è un unico file: `data/registro.csv`.

## Struttura

```
registro-incassi/
├── index.html                dashboard editabile (aprila con avvia.command)
├── avvia.command             doppio-click: avvia server locale + browser
├── data/registro.csv         database (config, scuole, assistenza, spese)
├── tools/
│   ├── cifra.py             (opzionale) cifra/decifra il CSV
│   └── registro.py          report a schermo da terminale
└── README.md
```

## Come si apre

**Doppio-click su `avvia.command`.** Parte un server locale e si apre il browser. Tieni aperta la finestra del terminale mentre lavori.

> Serve il server perché il browser, aprendo il file come `file://`, non può leggere `data/registro.csv`. `avvia.command` risolve.

## Come si usa

1. Modifica scuole, **assistenza** (persone + ore), spese, tariffe. Incassi, totali e grafici si ricalcolano da soli.
2. **💾 Salva CSV** → scarica `registro.csv` aggiornato. Sostituiscilo in `data/` per salvare.
3. **🔗 Esporta homepage** → crea `homepage.html`, un file singolo autonomo (dati inclusi) da **condividere con gli amici**. Loro possono guardare e modificare nel loro browser, ma nulla si salva.

### Sezioni

- **Registro per scuola**: incasso sistema = libri venduti × tariffa. `esente` esclude la scuola.
- **Assistenza**: una voce per ogni scuola; dentro ogni scuola aggiungi le persone con le loro ore. Ricavo = ore × tariffa oraria, con subtotale per scuola. La spunta include/esclude la persona dal totale.
- **Spese**: costi fissi, sottratti dal totale.
- **Netto sistema** = incasso vendite + assistenza (persone incluse) − spese.

## Cifratura (opzionale)

Di default i dati sono in chiaro in `data/registro.csv`. Se vuoi ri-cifrarli:

```bash
python3 tools/cifra.py            # data/registro.csv  ->  data/registro.csv.enc
python3 tools/cifra.py --decifra  # data/registro.csv.enc  ->  data/registro.csv
```

Richiede `pip3 install cryptography`.

## Report da terminale (opzionale)

```bash
python3 tools/registro.py report   # riepilogo a schermo
```
