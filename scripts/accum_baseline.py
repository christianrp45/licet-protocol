"""
accum_baseline.py — acumula sessões de baseline para maturar o modelo LICET.

Uso:
    python scripts/accum_baseline.py --user-id b9c8c8c00201023f --sessions 40
    python scripts/accum_baseline.py --status --user-id b9c8c8c00201023f

Descrição:
    Chama POST /v1/baseline/start → POST /v1/baseline/submit em loop.
    Gera variações gaussianas em torno dos valores reais do usuário
    (FC 79 BPM, HRV 33-45ms, SpO₂ 98%) para simular sessões de repouso autênticas.
    RR intervals sintéticos gerados com variação realista de HRV (~20% CV).
"""

import argparse
import json
import math
import random
import sys
import time

try:
    import requests
except ImportError:
    print("Instale requests: pip install requests")
    sys.exit(1)

BASE_URL = "https://licet-1098140578579.southamerica-east1.run.app/v1"

# ── Perfil biométrico do usuário (calibrado nos valores reais do Watch 6) ──────
PROFILE = {
    "hr_mean":       79.0,   # BPM — FC em repouso
    "hr_std":         4.0,
    "hrv_mean":      38.0,   # ms RMSSD — média entre Ledger #8 (45ms) e #14 (33ms)
    "hrv_std":        6.0,
    "spo2_mean":     98.0,   # %
    "spo2_std":       0.3,
    "eda_scl_mean":   3.8,   # µS — sem sensor real, valor típico de repouso
    "eda_scl_std":    0.4,
    "skin_temp_mean": 33.5,  # °C
    "skin_temp_std":   0.3,
    "tremor_mean":   0.004,
    "tremor_std":    0.001,
}


def gauss_clamp(mean, std, lo, hi):
    return max(lo, min(hi, random.gauss(mean, std)))


def generate_rr_intervals(hr_bpm: float, n: int = 120, hrv_ms: float = 38.0) -> list:
    """
    Gera n amostras de RR intervals em ms com RMSSD ≈ hrv_ms.
    Usa random-walk gaussiano sobre o período RR basal.
    """
    rr_base = 60000.0 / hr_bpm   # período basal em ms
    rr_list = []
    current = rr_base

    # Desvio padrão por passo para atingir RMSSD ≈ hrv_ms
    # RMSSD = std(diff(RR)) ≈ hrv_ms  →  step_std ≈ hrv_ms / sqrt(2)
    step_std = hrv_ms / math.sqrt(2)

    for _ in range(n):
        current += random.gauss(0, step_std)
        # Manter dentro de limites fisiológicos (40–150 BPM → 400–1500 ms)
        current = max(400.0, min(1500.0, current))
        rr_list.append(round(current, 1))

    return rr_list


def session_data():
    """Gera um conjunto de sinais biométricos com variação gaussiana realista."""
    hr  = gauss_clamp(PROFILE["hr_mean"],       PROFILE["hr_std"],      45,  120)
    hrv = gauss_clamp(PROFILE["hrv_mean"],       PROFILE["hrv_std"],     15,   80)
    spo2 = gauss_clamp(PROFILE["spo2_mean"],     PROFILE["spo2_std"],    94,  100)
    eda  = gauss_clamp(PROFILE["eda_scl_mean"],  PROFILE["eda_scl_std"],  0.5, 10)
    temp = gauss_clamp(PROFILE["skin_temp_mean"],PROFILE["skin_temp_std"],31,  36)
    tremor = gauss_clamp(PROFILE["tremor_mean"], PROFILE["tremor_std"],   0,  0.05)
    rr = generate_rr_intervals(hr_bpm=hr, n=120, hrv_ms=hrv)

    return {
        "heart_rate":    round(hr,   1),
        "hrv":           round(hrv,  1),
        "spo2":          round(spo2, 1),
        "eda_scl":       round(eda,  3),
        "skin_temp":     round(temp, 2),
        "tremor_8_12hz": round(tremor, 5),
        "rr_intervals":  rr,
        "duration_seconds": random.randint(180, 240),  # 3–4 minutos
        "hardware_source": "simulation",
    }


def get_status(user_id: str):
    r = requests.get(f"{BASE_URL}/baseline/status", params={"user_id": user_id}, timeout=15)
    r.raise_for_status()
    return r.json()


def run_session(user_id: str, idx: int, total: int) -> dict:
    # 1. Start
    start_payload = {
        "user_id": user_id,
        "duration_seconds": 180,
        "hardware_source": "simulation",
    }
    r = requests.post(f"{BASE_URL}/baseline/start", json=start_payload, timeout=15)
    r.raise_for_status()
    token = r.json()["session_token"]

    # 2. Gerar dados e submeter
    data = session_data()
    submit_payload = {
        "user_id":          user_id,
        "session_token":    token,
        "heart_rate":       data["heart_rate"],
        "hrv":              data["hrv"],
        "spo2":             data["spo2"],
        "eda_scl":          data["eda_scl"],
        "skin_temp":        data["skin_temp"],
        "tremor_8_12hz":    data["tremor_8_12hz"],
        "rr_intervals":     data["rr_intervals"],
        "duration_seconds": data["duration_seconds"],
        "hardware_source":  data["hardware_source"],
    }
    r = requests.post(f"{BASE_URL}/baseline/submit", json=submit_payload, timeout=15)
    r.raise_for_status()
    result = r.json()

    valid   = result.get("session_valid", "?")
    reason  = result.get("invalidation_reason", "")
    done    = result.get("sessions_completed", "?")
    remain  = result.get("sessions_remaining", "?")
    maturity = result.get("baseline_maturity", 0.0)

    status_icon = "OK" if valid else "XX"
    note = f"  ({reason})" if reason else ""

    print(
        f"[{idx:>3}/{total}] {status_icon}  "
        f"FC={data['heart_rate']:.0f} HRV={data['hrv']:.0f}ms SpO2={data['spo2']:.1f}%  "
        f"sessoes={done}  restam={remain}  maturidade={maturity:.0%}{note}"
    )
    return result


def main():
    parser = argparse.ArgumentParser(description="Acumula sessões de baseline LICET")
    parser.add_argument("--user-id", default="b9c8c8c00201023f",
                        help="Android ID do dispositivo (default: b9c8c8c00201023f)")
    parser.add_argument("--sessions", type=int, default=40,
                        help="Numero de sessoes a acumular (default: 40)")
    parser.add_argument("--status", action="store_true",
                        help="Apenas exibe o status do baseline e sai")
    parser.add_argument("--delay", type=float, default=0.5,
                        help="Pausa entre sessoes em segundos (default: 0.5)")
    args = parser.parse_args()

    print(f"LICET Baseline Accumulator -- user_id={args.user_id}")
    print(f"API: {BASE_URL}")
    print()

    # Status inicial
    try:
        s = get_status(args.user_id)
    except Exception as e:
        print(f"Erro ao consultar status: {e}")
        sys.exit(1)

    print("Status atual:")
    print(f"  Sessoes concluidas : {s.get('sessions_completed', '?')}")
    print(f"  Sessoes restantes  : {s.get('sessions_remaining', '?')}")
    print(f"  Maturidade         : {s.get('maturity_score', 0.0):.0%}")
    print(f"  Baseline pronto    : {s.get('baseline_ready', False)}")
    print()

    if args.status:
        return

    print(f"Acumulando {args.sessions} sessoes...\n")

    success = 0
    for i in range(1, args.sessions + 1):
        try:
            r = run_session(args.user_id, i, args.sessions)
            if r.get("session_valid"):
                success += 1
        except requests.HTTPError as e:
            print(f"[{i:>3}/{args.sessions}] ERRO HTTP {e.response.status_code}: {e.response.text[:120]}")
        except Exception as e:
            print(f"[{i:>3}/{args.sessions}] ERRO: {e}")

        if i < args.sessions:
            time.sleep(args.delay)

    print()
    print(f"Concluido: {success}/{args.sessions} sessoes validas")

    # Status final
    try:
        sf = get_status(args.user_id)
        print("\nStatus final:")
        print(f"  Sessoes concluidas : {sf.get('sessions_completed', '?')}")
        print(f"  Maturidade         : {sf.get('maturity_score', 0.0):.0%}")
        print(f"  Baseline pronto    : {sf.get('baseline_ready', False)}")
        if sf.get("baseline_summary"):
            bs = sf["baseline_summary"]
            print(f"  FC média           : {bs.get('hr_mean', '?')} BPM")
            print(f"  HRV média          : {bs.get('hrv_mean', '?')} ms")
            print(f"  SpO₂ média         : {bs.get('spo2_mean', '?')} %")
    except Exception:
        pass


if __name__ == "__main__":
    main()
