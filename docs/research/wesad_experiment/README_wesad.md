# WESAD Validation Experiment — LICET Layer 3

Valida o protocolo LICET (Camada 3 — Mahalanobis) contra o dataset público WESAD.

## Download do Dataset

**Link principal:**
https://uni-siegen.sciebo.de/s/HGdUkoNlW1Gy4em

Requer cadastro gratuito no portal da Universidade de Siegen.
Aprovação geralmente em 24–48h.

**Contato com os autores (se link indisponível):**
philip.schmidt@uni-siegen.de

**Referência:**
> Schmidt, P., Reiss, A., Duerichen, R., Marberger, C., & Van Laerhoven, K. (2018).
> Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection.
> ICMI 2018. DOI: 10.1145/3242969.3242985

## Setup

```
pip install numpy scipy
pip install cvxEDA     # opcional — decomposição tônica/fásica do EDA (Greco et al. 2015)
```

Sem `cvxEDA` instalado (requer `cvxopt`, que pode dar trabalho para compilar em
alguns ambientes Windows), o script roda normalmente mas degrada de 5 para 4
sinais no vetor Mahalanobis — EDA_SCL cai para um low-pass filter simples e
EDA_SCR é omitido. Um aviso é impresso no início da execução informando qual
caso está ativo.

Extrair o dataset mantendo a estrutura:
```
docs/research/wesad_experiment/
    WESAD/
        S2/S2.pkl
        S3/S3.pkl
        ...
        S17/S17.pkl
    wesad_experiment.py
```

## Execução

```bash
cd docs/research/wesad_experiment
python wesad_experiment.py
```

## Outputs

```
results/
    wesad_results.json      — métricas completas por sujeito + agregado
    wesad_per_subject.csv   — tabela para análise
    wesad_summary.txt       — texto pronto para Seção 6 do paper VLP
```

## Mapeamento LICET ↔ WESAD

| LICET           | WESAD                              | Frequência | Método |
|------------------|------------------------------------|------------|--------|
| RMSSD            | wrist BVP → picos → RR → RMSSD     | 64 Hz      | filtro banda 0.5-4Hz + detecção de picos |
| EDA_SCL / EDA_SCR| wrist EDA → cvxEDA (tônica/fásica) | 4 Hz       | Greco et al. 2015; fallback low-pass ≤0.05Hz se cvxEDA indisponível (só SCL) |
| DELTA_TEMP       | wrist TEMP → delta vs. média baseline | 4 Hz    | direto |
| TREMOR_8_12HZ    | wrist ACC (3 eixos) → potência 8-12Hz | 32 Hz    | periodograma da aceleração resultante |
| IP (GAP-B01)     | mesmos RR do RMSSD → `core.respiratory_periodicity` | — | import direto do módulo de produção |
| Ground-truth resp.| chest Resp (RespiBAN) → freq. dominante 0.05-0.6Hz | 700 Hz | cross-check independente do IP, não entra no D² |

O vetor Mahalanobis usa `core.mahalanobis.evaluate_mahalanobis_layer()` importado
diretamente (não reimplementado) — mesmos limiares χ² e mesma fórmula da produção.
SPO2 não está disponível no WESAD e não faz parte deste vetor de 5 sinais
(que corresponde ao "vetor completo" documentado em `core/mahalanobis.py`).

## Hipóteses Validadas

| Hipótese | Esperado | Referência |
|----------|----------|-----------|
| H1: RMSSD cai no stress | baseline > stress (p<0.001) | Thayer et al. 2012 |
| H2: D² stress > threshold | sensitivity >80% | — |
| H3: D² amusement < threshold | specificity >70% | — |
| H4: EDA SCL sobe no stress | baseline < stress | Boucsein 2012 |
| H5: IP não deve disparar falso-positivo em meditação genuína | taxa de FP baixa | GAP-B01, Laborde et al. 2022 — meditação guiada é o teste mais duro porque é o estado genuíno fisiologicamente mais próximo de paced breathing |

## Resultado Esperado (literatura)

Schmidt et al. 2018 reportam ~92.2% accuracy com LDA.
LICET usa Mahalanobis individual (não classificador populacional) —
sensitividade esperada: 75–90%, specificity: 70–85%.

Diferença metodológica importante para o paper: LICET constrói
baseline INDIVIDUAL por sujeito, não treina um classificador de
população. É um sistema de detecção de anomalia pessoal, não
um classificador binário stress/não-stress.
