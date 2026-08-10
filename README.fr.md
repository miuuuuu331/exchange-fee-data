[English](README.md) · [中文](README.zh-CN.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [日本語](README.ja.md) · **Français** · [Español](README.es.md)

# Jeu de données des frais de trading

Données structurées et versionnées sur les frais de 7 plateformes crypto majeures — spot et futures perpétuels, maker et taker. Le VIP0 est couvert à ce jour ; les paliers supérieurs sont en cours d'ajout. Revérifiées manuellement chaque mercredi, chaque instantané hebdomadaire étant conservé dans `data/history/`.

JSON et CSV. Licence MIT. Pas de clé API, pas de limite de requêtes, pas d'inscription — ce ne sont que des fichiers dans un dépôt git.

---

## Pourquoi ce dépôt existe

Chaque plateforme publie sa grille tarifaire, et chacune la publie différemment. Certaines sous forme de tableau, d'autres enfouie dans un article du centre d'aide, d'autres encore uniquement après connexion. Les paliers sont renommés, les tarifs promotionnels expirent sans annonce, et personne ne conserve les anciens chiffres.

Résultat : une question aussi élémentaire que **« quel était le taker sur les futures Bybit en mars ? »** n'a aujourd'hui aucune source consultable.

Nous prenons donc un instantané de toutes les plateformes, une fois par semaine, dans un schéma unique.

---

## Instantané actuel

Palier VIP0, à la date de la dernière vérification :

| Plateforme | Spot | Futures maker | Futures taker |
|---|---|---|---|
| Binance | 0,100 % | 0,020 % | 0,050 % |
| Bitget | 0,100 % | 0,020 % | 0,060 % |
| Gate.io | 0,100 % | 0,020 % | 0,050 % |
| Bybit | 0,100 % | 0,020 % | 0,055 % |
| OKX | 0,090 % | 0,020 % | 0,050 % |
| Backpack | 0,090 % | 0,020 % | 0,050 % |
| Polymarket | 0,75 %–1,8 % | — | — |

La version faisant foi est `data/fees.json`. Le tableau ci-dessus en est généré et peut accuser quelques heures de retard.

---

## Démarrage rapide

```bash
# Instantané le plus récent, toutes plateformes
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json

# Uniquement les frais taker futures VIP0, triés
curl -s https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.json \
  | jq -r '.exchanges[] | [.id, .futures.vip0.taker] | @tsv' | sort -k2 -n
```

```python
import pandas as pd

URL = "https://raw.githubusercontent.com/miuuuuu331/exchange-fee-data/main/data/fees.csv"
df = pd.read_csv(URL)

# Taker perp VIP0 le moins cher
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

## Arborescence

```
data/
├── fees.json              # instantané courant, version canonique
├── fees.csv               # mêmes données, aplaties
└── history/
    ├── 2026-08-05.json
    ├── 2026-07-29.json
    └── ...
schema/
└── fees.schema.json       # JSON Schema (draft 2020-12)
scripts/
└── validate.py            # à exécuter avant d'ouvrir une PR
```

### Schéma

```json
{
  "snapshot_date": "2026-08-05",
  "exchanges": [
    {
      "id": "binance",
      "name": "Binance",
      "source_url": "https://www.binance.com/fr/fee/schedule",
      "verified_at": "2026-08-05",
      "spot":    { "vip0": { "maker": 0.0010, "taker": 0.0010 } },
      "futures": { "vip0": { "maker": 0.0002, "taker": 0.0005 } },
      "notes": "La détention de BNB applique une remise de 25 % sur les frais spot."
    }
  ]
}
```

Tous les taux sont exprimés en **fractions décimales**, ni en pourcentages ni en points de base. `0.0005` signifie 0,05 %. C'est de loin l'erreur la plus fréquente sur ce type de données, aussi le schéma l'impose-t-il.

Colonnes du CSV : `snapshot_date, exchange_id, market, tier, maker, taker`.

---

## Comment les chiffres sont vérifiés

Chaque mercredi, la page tarifaire publique de chaque plateforme est consultée manuellement puis rapprochée des chiffres du tableau de bord d'affiliation, souvent plus à jour que la page publique. En cas d'écart, nous le consignons dans `notes` plutôt que de trancher arbitrairement.

La procédure complète — ce qui constitue un palier, le traitement des tarifs promotionnels, la conduite à tenir lorsqu'une plateforme modifie sa grille en cours de semaine — est documentée dans [la méthodologie RAILSDESK](https://railsdesk.com/fr/#method).

Nous ne faisons pas de scraping. Scraper les pages tarifaires produit plus souvent des données fausses que justes, la plupart des plateformes rendant les paliers côté client et les conditionnant à l'état du compte.

---

## Tarif affiché et coût réel

Une précision importante si vous comptez utiliser ce jeu de données pour comparer les plateformes : **les chiffres ici sont des tarifs affichés**, c'est-à-dire le prix catalogue avant toute remise à laquelle vous pourriez avoir droit.

Trois éléments modifient couramment le coût réel :

1. **Les paliers de volume** — le VIP0 figure aujourd'hui dans le jeu de données ; le VIP1 et au-delà sont en cours.
2. **Les remises en token natif** — détenir du BNB réduit par exemple de 25 % les frais spot sur Binance. Consigné dans `notes`, pas dans les champs de taux.
3. **Les remises d'affiliation** — une part des frais reversée au trader via une relation de parrainage. Totalement absente de ce jeu de données, car elle dépend du lien par lequel le compte a été ouvert, et non de la grille de la plateforme.

Le troisième élément est généralement le plus important en montant, et le moins documenté. Les taux de reversement en vigueur par plateforme sont suivis séparément sur [remise sur frais de trading](https://railsdesk.com/fr/), avec la comparaison clause par clause dans [la section analyses](https://railsdesk.com/fr/articles/).

Si vous construisez un modèle de coûts, traitez ces trois éléments comme trois multiplicateurs distincts. Les fusionner dans un unique champ `fee` est la raison classique pour laquelle un backtest ressort trop optimiste.

---

## Contribuer

Les corrections sont bienvenues — c'est la raison principale pour laquelle ce dépôt est public.

1. Forkez, modifiez `data/fees.json`
2. Exécutez `python scripts/validate.py` — il valide le schéma et signale les taux invraisemblables
3. Ouvrez une PR en joignant le lien vers la page tarifaire de la plateforme comme justificatif

Pour demander l'ajout d'une plateforme : ouvrez une issue avec l'URL de la grille tarifaire. Le critère est une documentation tarifaire publique et lisible par machine, ainsi qu'un volume significatif.

---

## Licence

MIT pour le code. [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) pour les données — usage commercial, redistribution et intégration produit autorisés, à condition de conserver l'attribution.

---

## Avertissement

Il s'agit de données tarifaires, pas de conseils en investissement. Le trading de dérivés crypto peut entraîner la perte totale du capital engagé. Les taux évoluent et l'instantané présent dans ce dépôt peut avoir jusqu'à sept jours de retard : vérifiez auprès de la plateforme avant que cela ne compte vraiment.

Maintenu par [RAILSDESK](https://railsdesk.com/fr/), qui perçoit une commission d'affiliation de la part de certaines plateformes listées ici. Cette relation finance le travail de collecte et n'influence pas les chiffres consignés — publier l'intégralité de l'historique sert précisément à vous permettre de le vérifier.
