[English](README.md) · [中文](README.zh-CN.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · [Français](README.fr.md) · **Español**

# Conjunto de datos de comisiones de exchanges

Datos estructurados y versionados sobre las comisiones de 7 exchanges cripto principales — spot y futuros perpetuos, maker y taker. Por ahora está cubierto el VIP0; los niveles de volumen superiores se van añadiendo. Se reverifican a mano todos los miércoles, y cada instantánea semanal queda guardada en `data/history/`.

JSON y CSV. Licencia MIT. Sin API key, sin límite de peticiones, sin registro — son simplemente archivos en un repositorio git.

---

## Por qué existe

Todos los exchanges publican su tabla de comisiones, y cada uno la publica de una forma distinta. Unos en una tabla, otros enterrada en un artículo del centro de ayuda, otros solo tras iniciar sesión. Los niveles cambian de nombre, las tarifas promocionales caducan sin aviso y nadie conserva las cifras antiguas.

El resultado es que una pregunta tan básica como **«¿cuál era la comisión taker de futuros de Bybit en marzo?»** hoy no se puede responder en ningún sitio.

Así que tomamos una instantánea de todos ellos, una vez por semana, bajo un mismo esquema.

---

## Instantánea actual

Nivel VIP0, según la última verificación:

| Exchange | Spot | Futuros maker | Futuros taker |
|---|---|---|---|
| Binance | 0,100 % | 0,020 % | 0,050 % |
| Bitget | 0,100 % | 0,020 % | 0,060 % |
| Gate.io | 0,100 % | 0,020 % | 0,050 % |
| Bybit | 0,100 % | 0,020 % | 0,055 % |
| OKX | 0,090 % | 0,020 % | 0,050 % |
| Backpack | 0,090 % | 0,020 % | 0,050 % |
| Polymarket | 0,75 %–1,8 % | — | — |

La versión de referencia es `data/fees.json`. La tabla anterior se genera a partir de él y puede llevar unas horas de retraso.

---

## Inicio rápido

```bash
# Instantánea más reciente, todos los exchanges
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# Solo las comisiones taker de futuros VIP0, ordenadas
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# Taker de perpetuos VIP0 más barato
(df[(df.market == "futures") & (df.tier == "vip0")]
   .sort_values("taker")[["exchange_id", "maker", "taker"]])
```

```javascript
const res = await fetch(
  "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json"
);
const { exchanges } = await res.json();
```

---

## Estructura

```
data/
├── fees.json              # instantánea actual, versión canónica
├── fees.csv               # los mismos datos, aplanados
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # ejecútalo antes de abrir un PR
```

### Esquema

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/es/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "Mantener BNB aplica un 25 % de descuento sobre las comisiones spot."
    }
  ]
}
```

Todas las tasas se expresan como **fracciones decimales**, no como porcentajes ni puntos básicos. `0.0005` significa 0,05 %. Es con diferencia el error más habitual al trabajar con datos de comisiones, por eso el esquema lo impone.

Columnas del CSV: `snapshot_date, exchange_id, market, tier, maker, taker`.

---

## Cómo se verifican las cifras

Cada miércoles se abre a mano la página pública de comisiones de cada exchange y se contrasta con las cifras del panel de afiliados, que suele estar más actualizado que la página pública. Cuando ambas discrepan, lo dejamos anotado en `notes` en lugar de resolverlo por nuestra cuenta.

El procedimiento completo — qué cuenta como un nivel, cómo se tratan las tarifas promocionales, qué hacer cuando un exchange cambia su tabla a mitad de semana — está documentado en [la metodología de RAILSDESK](https://railsdesk.com/es/#method).

No hacemos scraping. Rascar las páginas de comisiones produce datos erróneos más a menudo que correctos, porque la mayoría de exchanges renderiza los niveles en el cliente y los condiciona al estado de la cuenta.

---

## Comisión de tarifa frente a comisión efectiva

Una advertencia importante si vas a usar este conjunto de datos para comparar exchanges: **las cifras que aparecen aquí son comisiones de tarifa**, es decir, el precio de catálogo antes de cualquier descuento al que puedas tener derecho.

Hay tres factores que alteran habitualmente el coste real:

1. **Niveles por volumen** — hoy el conjunto incluye VIP0; VIP1 en adelante está en curso.
2. **Descuentos con el token del exchange** — por ejemplo, mantener BNB reduce un 25 % las comisiones spot de Binance. Se anota en `notes`, no en los campos de tasa.
3. **Reembolsos de afiliación** — una parte de la comisión que vuelve al trader a través de una relación de referido. No está en este conjunto de datos en absoluto, porque depende del enlace con el que se abrió la cuenta, no de la tabla del exchange.

El tercero suele ser el mayor de los tres en importe y el peor documentado. Los porcentajes vigentes por exchange se mantienen aparte en [reembolso de comisiones](https://railsdesk.com/es/), con la comparación cláusula a cláusula en [la sección de análisis](https://railsdesk.com/es/articles/).

Si estás construyendo un modelo de costes, trata estos tres factores como multiplicadores independientes. Fundirlos en un único campo `fee` es el motivo clásico de que un backtest salga demasiado optimista.

---

## Contribuir

Las correcciones son bienvenidas — de hecho son la razón principal de que este repositorio sea público.

1. Haz un fork y edita `data/fees.json`
2. Ejecuta `python scripts/validate.py` — valida el esquema y señala tasas inverosímiles
3. Abre un PR adjuntando el enlace a la página de comisiones del exchange como evidencia

Para pedir un exchange nuevo: abre una issue con la URL de su tabla de comisiones. El criterio es que tenga documentación de comisiones pública y legible por máquina, además de volumen relevante.

---

## Licencia

MIT para el código. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) para los datos — uso comercial, redistribución y desarrollo de productos permitidos; basta con mantener la atribución.

---

## Aviso legal

Esto son datos de comisiones, no asesoramiento de inversión. Operar con derivados cripto puede hacerte perder la totalidad del capital depositado. Las tasas cambian y la instantánea de este repositorio puede tener hasta siete días de antigüedad: verifícala en el exchange antes de que te importe de verdad.

Mantenido por [RAILSDESK](https://railsdesk.com/es/), que percibe comisiones de afiliación de algunos de los exchanges aquí listados. Esa relación financia el trabajo de recopilación y no afecta a las cifras registradas — publicar el historial completo existe precisamente para que puedas comprobarlo.
