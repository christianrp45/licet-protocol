"""
LICET — Detecção de Interferência Farmacológica
Identifica padrões de toxidrome que podem mascarar coerção ou incapacidade.

Três toxidromes-alvo:
  1. Beta-bloqueador (propranolol, metoprolol):
     Bloqueia receptores β₁/β₂ adrenérgicos → tremor 8–12 Hz suprimido + FC blunted.
     RMSSD reflete retirada vagal (parassimpático), não atividade adrenérgica — o
     betabloqueio NÃO suprime RMSSD diretamente. O que é atenuado é a potência LF
     (que reflete modulação barorreflexa do outflow autonômico, não tônus simpático
     cardíaco diretamente — Moak et al., Heart Rhythm 2007). A retirada vagal sob
     estresse agudo persiste mecanisticamente sob betabloqueio.

  2. Anticolinérgico (atropina, escopolamina, beladona):
     Bloqueia receptores muscarínicos → EDA plana + pele quente e seca + RMSSD abolido
     + taquicardia. As glândulas écrinas têm inervação simpática COLINÉRGICA — atropina
     bloqueia essa inervação, resultando em EDA plana. Simultaneamente, o bloqueio
     vagal (M₂) causa taquicardia e ABOLE RMSSD. A combinação (RMSSD abolido + EDA
     plana + FC elevada) não é produzida por nenhum estado genuíno de calma —
     assinatura autoincriminante. "Blind as a bat, hot as a hare, red as a beet,
     dry as a bone" — mnemônica clínica.

  3. Opioide (morfina, fentanil, codeína):
     Depressão do SNC → SpO2 baixa + bradicardia + tremor suprimido + pele quente (vasodilatação).

Todos os padrões são verificados contra o baseline INDIVIDUAL do usuário (z-scores),
não contra populações. Um usuário com FC de repouso de 50 BPM não dispara falso positivo
de opioide. Um atleta com HRV alto não dispara falso positivo de anticolinérgico.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class PharmacologicalCheckResult:
    clean: bool                         # True se nenhum padrão detectado
    pattern_detected: Optional[str]     # None | "BETA_BLOCKER" | "ANTICHOLINERGIC" | "OPIOID"
    confidence: str                     # "LOW" | "MEDIUM" | "HIGH"
    signals_evaluated: int              # Quantos sinais avançados foram usados
    reason: str
    self_incriminating: bool = False    # True quando a combinação é impossível em calma genuína
                                        # (RMSSD abolido + EDA plana + taquicardia)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _z(value: float, mean: Optional[float], std: Optional[float]) -> Optional[float]:
    """Z-score individual. Retorna None se baseline ausente."""
    if mean is None or std is None or std <= 0.0:
        return None
    return (value - mean) / std


def _fmt(v: Optional[float], unit: str = "") -> str:
    return f"{v:.3f}{unit}" if v is not None else "N/D"


# ── Avaliação farmacológica ───────────────────────────────────────────────────

def check_pharmacological_interference(
    heart_rate: float,
    hrv_rmssd: float,
    spo2: float,
    eda_scl: Optional[float] = None,
    eda_scr: Optional[float] = None,          # μS — componente fásico (SCR)
    skin_temp: Optional[float] = None,        # °C — temperatura cutânea
    tremor_8_12hz: Optional[float] = None,    # g² — potência acelerométrica 8–12 Hz
    # Baseline individual para z-scores
    baseline_hr_mean: Optional[float] = None,
    baseline_hr_std: Optional[float] = None,
    baseline_hrv_mean: Optional[float] = None,
    baseline_hrv_std: Optional[float] = None,
    baseline_tremor_mean: Optional[float] = None,
    baseline_tremor_std: Optional[float] = None,
    # GAP-L05 fix: acomodação razoável para medicação prescrita
    # True quando o usuário tem baseline calibrado com beta-bloqueador crônico.
    # Previne discriminação por condição médica (ADA / EU Employment Equality Directive).
    # Referência: beta-bloqueadores crônicos elevam RMSSD basal e reduzem HR de repouso
    # (Lampert et al., Am J Cardiol 2003) — baseline deslocado é o estado "normal" do usuário.
    medication_accommodation: bool = False,
) -> PharmacologicalCheckResult:
    """
    Verifica se os sinais biométricos correspondem a alguma toxidrome conhecida.

    Args:
        heart_rate:       FC em BPM (obrigatório)
        hrv_rmssd:        HRV RMSSD em ms (obrigatório)
        spo2:             Saturação de oxigênio em % (obrigatório)
        eda_scl:          EDA tônico em μS (opcional — WHOOP/Galaxy Watch 7)
        eda_scr:          EDA fásico em μS (opcional — componente SCR)
        skin_temp:        Temperatura cutânea em °C (opcional — wearables avançados)
        tremor_8_12hz:    Potência acelerométrica na banda 8–12 Hz em g² (opcional)
        baseline_*:       Parâmetros do baseline individual para cálculo de z-scores.

    Returns:
        PharmacologicalCheckResult
    """
    # Z-scores individuais (None se baseline ausente)
    z_hr     = _z(heart_rate, baseline_hr_mean, baseline_hr_std)
    z_hrv    = _z(hrv_rmssd, baseline_hrv_mean, baseline_hrv_std)
    z_tremor = _z(tremor_8_12hz, baseline_tremor_mean, baseline_tremor_std) if tremor_8_12hz is not None else None

    # Contar sinais avançados disponíveis (além de HR/HRV/SpO2)
    advanced = sum(x is not None for x in [eda_scl, skin_temp, tremor_8_12hz])

    # ── Padrão 1: Beta-bloqueador ────────────────────────────────────────────
    # Mecanismo: bloqueia receptores β₁/β₂ adrenérgicos.
    # Efeito no tremor: o tremor fisiológico de 8–12 Hz é beta-adrenérgico — betabloqueio suprime.
    # Efeito no RMSSD: RMSSD reflete retirada vagal (parassimpático), NÃO atividade adrenérgica.
    # Betabloqueio NÃO suprime RMSSD — vagal withdrawal persiste sob coerção.
    # LF power é atenuado (LF reflete modulação barorreflexa, não tônus simpático direto).
    # Sinal diagnóstico primário: dissociação tremor↓ + FC blunted, com RMSSD preservado.
    bb_score = 0

    if z_tremor is not None and z_tremor < -2.0:
        bb_score += 2   # sinal forte: tremor muito abaixo do próprio baseline
    elif tremor_8_12hz is not None and tremor_8_12hz < 0.002:
        bb_score += 1   # heurística absoluta quando sem baseline

    if z_hr is not None and z_hr > 1.5 and z_tremor is not None and z_tremor < -1.5:
        bb_score += 1   # dissociação FC↑ + tremor↓ — clássica

    if bb_score >= 2:
        conf = "HIGH" if (z_tremor is not None and advanced >= 1) else "MEDIUM"

        # GAP-L05 fix: se usuário tem acomodação documentada de beta-bloqueador crônico,
        # NÃO denegar — emitir "BETA_BLOCKER_ACCOMMODATED" com confiança rebaixada.
        # O baseline já foi calibrado sob medicação → padrão é o estado normal do usuário.
        # Legal: nega de outra forma configura discriminação por condição médica prescrita.
        if medication_accommodation:
            return PharmacologicalCheckResult(
                clean=True,   # Tratado como limpo para fins de autorização
                pattern_detected="BETA_BLOCKER_ACCOMMODATED",
                confidence="LOW",
                signals_evaluated=advanced,
                reason=(
                    f"Padrão beta-bloqueador detectado MAS acomodação documentada ativa: "
                    f"tremor suprimido (z={_fmt(z_tremor)}), FC (z={_fmt(z_hr)}). "
                    "Baseline calibrado sob medicação crônica — padrão esperado. "
                    "Autorização prossegue com aviso (GAP-L05). "
                    "Poder discriminativo do Mahalanobis reduzido para este usuário. "
                    "Ver: Lampert et al., Am J Cardiol 2003."
                ),
            )

        return PharmacologicalCheckResult(
            clean=False,
            pattern_detected="BETA_BLOCKER",
            confidence=conf,
            signals_evaluated=advanced,
            reason=(
                f"Padrão beta-bloqueador detectado: "
                f"tremor suprimido (z={_fmt(z_tremor)}) "
                f"com FC elevada (z={_fmt(z_hr)}). "
                "Possível uso de propranolol ou metoprolol para mascarar resposta de coerção. "
                "Se medicação é prescrita, solicitar acomodação via POST /accommodation/register."
            ),
        )

    # ── Padrão 2: Anticolinérgico ────────────────────────────────────────────
    # Mecanismo: bloqueia receptores muscarínicos M₂ (cardíaco) e M₃ (glândulas écrinas).
    # Efeito cardíaco: bloqueio vagal → taquicardia + RMSSD ABOLIDO (retirada parassimpática).
    # Efeito dérmico: glândulas écrinas têm inervação simpática COLINÉRGICA — atropina
    # bloqueia essa via → EDA plana (não por bloqueio simpático, mas colinérgico).
    # Resultado: EDA plana + RMSSD abolido + FC elevada.
    # Esta combinação é AUTOINCRIMINANTE: nenhum estado genuíno de calma a produz.
    # Taquicardia verificada por z-score (com baseline) OU limiar absoluto (sem baseline).
    ac_score = 0
    anticholinergic_triad = False   # tríade clássica: EDA plana + RMSSD abolido + taquicardia
    extended_triad = False          # tríade estendida: EDA gravemente suprimida + taquicardia
    partial_no_eda = False          # tríade parcial: RMSSD abolido + taquicardia, sem sensor EDA

    # Taquicardia: z-score individual preferencial; limiar absoluto como fallback
    tachycardia = (z_hr is not None and z_hr > 1.5) or (heart_rate > 100)

    # EDA SCL — dois limiares para capturar supressão colinérgica em gradações clínicas.
    # Normal em repouso: 1–20 µS. Abaixo de 0.3 µS: severamente suprimido (>3x abaixo
    # do mínimo normal). Abaixo de 0.05 µS: praticamente plano (atropina/escopolamina
    # em doses bloqueantes). V2 bug fix: limiar único < 0.05 µS não capturava 0.2 µS.
    if eda_scl is not None and eda_scl < 0.05:
        ac_score += 2   # EDA plana clássica — bloqueio colinérgico completo
    elif eda_scl is not None and eda_scl < 0.3:
        ac_score += 1   # EDA gravemente suprimida — suspeita moderada

    if eda_scr is not None and eda_scr < 0.01:
        ac_score += 1   # EDA SCR suprimida — corrobora bloqueio colinérgico
    if skin_temp is not None and skin_temp > 37.5:
        ac_score += 1   # pele quente e seca (toxidrome clássica)
    # RMSSD abolido — bloqueio vagal M₂.
    # Requer sensor EDA presente: sem EDA, HRV baixo pode refletir variação fisiológica
    # normal (ex: Watch 6 sem sensor EDA). Sem corroboração dérmica, z_hrv sozinho
    # não constitui evidência suficiente para bloqueio colinérgico.
    if eda_scl is not None and z_hrv is not None and z_hrv < -2.0:
        ac_score += 2   # RMSSD abolido confirmado com sensor EDA disponível

    # Tríade clássica autoincriminante: EDA plana + RMSSD abolido + taquicardia
    if (eda_scl is not None and eda_scl < 0.05
            and z_hrv is not None and z_hrv < -2.0
            and tachycardia):
        anticholinergic_triad = True
        ac_score += 2   # combinação impossível em calma genuína

    # Tríade estendida: EDA gravemente suprimida + taquicardia sem baseline de RMSSD.
    # V2 bug fix: EDA_SCL=0.2µS + HR=102bpm era retornado como CLEAN(HIGH).
    # Esta combinação não é produzida por calma genuína em repouso — EDA não cai abaixo
    # de 0.3 µS em repouso sem interferência farmacológica ou patologia severa.
    elif (not anticholinergic_triad
            and eda_scl is not None and eda_scl < 0.3
            and heart_rate > 100):
        extended_triad = True
        ac_score += 2   # padrão suspeito — MEDIUM sem sinais adicionais, HIGH com ≥2

    # Tríade parcial sem EDA: RMSSD abolido + taquicardia (sensor EDA ausente)
    if (not anticholinergic_triad
            and not extended_triad
            and eda_scl is None
            and z_hrv is not None and z_hrv < -2.0
            and tachycardia):
        partial_no_eda = True
        ac_score += 1   # evidência parcial — MEDIUM

    if ac_score >= 2:
        if anticholinergic_triad:
            conf = "HIGH"   # tríade clássica autoincriminante — confiança máxima
        elif extended_triad:
            conf = "HIGH" if advanced >= 2 else "MEDIUM"
        elif eda_scl is not None and advanced >= 2:
            conf = "HIGH"
        else:
            conf = "MEDIUM"

        if partial_no_eda:
            partial_note = (
                "Tríade parcial sem sensor EDA: RMSSD abolido + taquicardia detectados. "
                "Sensor EDA ausente — não é possível confirmar bloqueio colinérgico dérmico. "
            )
        elif anticholinergic_triad:
            partial_note = (
                "Tríade clássica autoincriminante (EDA plana + RMSSD abolido + taquicardia): "
                "nenhum estado genuíno de calma produz esta combinação. "
            )
        elif extended_triad:
            partial_note = (
                f"Tríade estendida: EDA gravemente suprimida ({eda_scl:.3f} µS < 0.3 µS) "
                f"+ taquicardia ({heart_rate:.0f} BPM > 100 BPM). "
                "EDA não cai abaixo de 0.3 µS em repouso sem interferência farmacológica. "
            )
        else:
            partial_note = ""

        return PharmacologicalCheckResult(
            clean=False,
            pattern_detected="ANTICHOLINERGIC",
            confidence=conf,
            signals_evaluated=advanced,
            self_incriminating=anticholinergic_triad or extended_triad,
            reason=(
                f"Padrão anticolinérgico detectado: "
                f"EDA SCL={_fmt(eda_scl, ' μS')}, EDA SCR={_fmt(eda_scr, ' μS')}, "
                f"RMSSD z={_fmt(z_hrv)} (vagal abolido), "
                f"FC={heart_rate:.0f} BPM (z={_fmt(z_hr)}), "
                f"pele={_fmt(skin_temp, '°C')}. "
                + partial_note
                + "Possível uso de atropina ou escopolamina."
            ),
        )

    # ── Padrão 3: Opioide ────────────────────────────────────────────────────
    # Mecanismo: agonismo em receptores μ/κ/δ opioides.
    # Efeito: depressão respiratória → SpO2 cai, bradicardia, miose, tremor suprimido,
    # vasodilatação periférica → pele quente.
    opioid_score = 0

    if spo2 < 94:
        opioid_score += 1
    if spo2 < 90:
        opioid_score += 1   # crítico
    if heart_rate < 55:
        opioid_score += 1   # bradicardia
    if z_tremor is not None and z_tremor < -2.0:
        opioid_score += 1
    if skin_temp is not None and skin_temp > 37.0:
        opioid_score += 1   # vasodilatação periférica opioidérgica

    if opioid_score >= 3:
        conf = "HIGH" if spo2 < 90 else "MEDIUM"
        return PharmacologicalCheckResult(
            clean=False,
            pattern_detected="OPIOID",
            confidence=conf,
            signals_evaluated=advanced,
            reason=(
                f"Padrão opioide detectado: "
                f"SpO2={spo2}%, FC={heart_rate} BPM, "
                f"tremor z={_fmt(z_tremor)}, pele={_fmt(skin_temp, '°C')}. "
                "Possível depressão do SNC por opioide."
            ),
        )

    # Nenhum padrão farmacológico detectado
    conf = "HIGH" if advanced >= 2 else ("MEDIUM" if advanced >= 1 else "LOW")
    return PharmacologicalCheckResult(
        clean=True,
        pattern_detected=None,
        confidence=conf,
        signals_evaluated=advanced,
        reason=(
            f"Nenhum padrão farmacológico detectado "
            f"({advanced} sinais avançados avaliados)."
        ),
    )
