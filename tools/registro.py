#!/usr/bin/env python3
"""
Registro Incassi - Piattaforma Libri Usati
Database in un UNICO file CSV: data/registro.csv

Il file ha una colonna 'tipo' che dice cos'è ogni riga:
  config -> tariffe e parametri   (nome = chiave, valore = valore)
  scuola -> una scuola            (gestiti, venduti, ricavo, netto, esente, ore, conta)
  spesa  -> un costo fisso        (nome = voce, valore = costo)

Uso:
  python3 registro.py report      mostra riepilogo a schermo

I dati stanno cifrati in data/registro.csv.enc: viene chiesta la password.
Se esiste ancora data/registro.csv in chiaro, viene usato quello.
"""
import csv, io, os, sys, argparse, getpass

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE, "data", "registro.csv")
ENC_PATH = os.path.join(BASE, "data", "registro.csv.enc")
FIELDS = ['tipo','nome','gestiti','venduti','ricavo','netto','esente','ore','conta','valore']

def si(v): return str(v).strip().lower() in ('si','sì','s','yes','y','true','1')
def num(v, d=0.0):
    try: return float(str(v).replace(',', '.'))
    except (ValueError, AttributeError): return d

def _read_csv_text():
    """Ritorna il CSV in chiaro: dal .enc (con password) o dal .csv se presente."""
    if os.path.exists(CSV_PATH):
        return open(CSV_PATH, encoding='utf-8').read()
    if os.path.exists(ENC_PATH):
        from cifra import decrypt
        pw = getpass.getpass("Password: ")
        try:
            return decrypt(open(ENC_PATH, encoding='utf-8').read(), pw)
        except Exception:
            sys.exit("Password errata o file danneggiato.")
    sys.exit(f"Nessun dato: manca sia {CSV_PATH} sia {ENC_PATH}")

def read_rows():
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    return list(csv.DictReader(io.StringIO(_read_csv_text())))

def load():
    cfg, scuole, spese = {}, [], []
    for r in read_rows():
        t = (r.get('tipo') or '').strip()
        if t == 'config':
            cfg[r['nome']] = r['valore']
        elif t == 'scuola':
            s = {'nome': r['nome'],
                 'gestiti': int(num(r['gestiti'])), 'venduti': int(num(r['venduti'])),
                 'ricavo': num(r['ricavo']), 'netto': num(r['netto']),
                 'esente': si(r['esente']),
                 'ore': num(r['ore']), 'conta': si(r['conta'])}
            scuole.append(s)
        elif t == 'spesa':
            spese.append({'voce': r['nome'], 'costo': num(r['valore'])})
    tariffa = num(cfg.get('tariffa_per_copia', 0.40))
    oraria  = num(cfg.get('tariffa_oraria_formazione', 15))
    for s in scuole:
        s['incasso'] = round(s['venduti'] * tariffa, 2)
        s['form_val'] = round(s['ore'] * oraria, 2)
    return cfg, tariffa, oraria, scuole, spese

def totali(scuole, spese):
    inc = round(sum(s['incasso'] for s in scuole if not s['esente']), 2)
    formz = round(sum(s['form_val'] for s in scuole if s['conta']), 2)
    spe = round(sum(x['costo'] for x in spese), 2)
    return inc, formz, spe, round(inc + formz - spe, 2)

def eur(n): return f"{n:,.2f} €".replace(",", "X").replace(".", ",").replace("X", ".")

def cmd_report(args):
    cfg, tariffa, oraria, scuole, spese = load()
    inc, formz, spe, netto = totali(scuole, spese)
    print(f"\n== REGISTRO INCASSI  (anno {cfg.get('anno_scolastico','-')}) ==")
    print(f"Tariffa: {eur(tariffa)}/copia  |  Formazione: {eur(oraria)}/h\n")
    print(f"{'Scuola':<12}{'Gest.':>7}{'Vend.':>7}{'Incasso':>12}   note")
    for s in scuole:
        print(f"{s['nome']:<12}{s['gestiti']:>7}{s['venduti']:>7}{eur(s['incasso']):>12}"
              f"   {'ESENTE' if s['esente'] else ''}")
    print("\n-- RIEPILOGO --")
    print(f"  Incasso vendite (attive) : + {eur(inc)}")
    print(f"  Ricavo formazione        : + {eur(formz)}")
    for x in spese:
        print(f"  Spesa {x['voce']:<18}: - {eur(x['costo'])}")
    print(f"  {'NETTO SISTEMA':<25}: = {eur(netto)}\n")

def main():
    p = argparse.ArgumentParser(description="Registro Incassi - CSV unico")
    sub = p.add_subparsers(dest='cmd')
    sub.add_parser('report').set_defaults(func=cmd_report)
    args = p.parse_args()
    if not getattr(args, 'func', None):
        p.print_help(); return
    args.func(args)

if __name__ == '__main__':
    main()
