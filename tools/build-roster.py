"""Build pokemon.json for Reagan's Pokemon Adventures from PokeAPI's GraphQL endpoint.

Run once (or whenever a new generation lands):
    python tools/build-roster.py

Output: pokemon.json in the repo root. Fields per entry are kept short to keep the file small:
    i = national dex id, n = display name, t = types, g = generation, b = base stat total,
    r = rarity tier used for spawn weighting and catch odds.
"""
import json, sys, urllib.request, datetime, pathlib

ENDPOINT = "https://beta.pokeapi.co/graphql/v1beta"
QUERY = """{ pokemon_v2_pokemonspecies(order_by:{id:asc}) {
  id name is_legendary is_mythical generation_id
  pokemon_v2_pokemonspeciesnames(where:{language_id:{_eq:9}}) { name }
  pokemon_v2_pokemons(where:{is_default:{_eq:true}}) {
    pokemon_v2_pokemontypes(order_by:{slot:asc}) { pokemon_v2_type { name } }
    pokemon_v2_pokemonstats { base_stat }
  } } }"""


def tier(species, bst):
    if species["is_mythical"]:
        return "mythical"
    if species["is_legendary"]:
        return "legendary"
    if bst >= 520:
        return "rare"
    if bst >= 420:
        return "uncommon"
    return "common"


def main():
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps({"query": QUERY}).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "reagans-pokemon-adventures roster builder"},
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        payload = json.load(r)
    if "errors" in payload:
        sys.exit("GraphQL errors: %s" % payload["errors"])

    out = []
    for sp in payload["data"]["pokemon_v2_pokemonspecies"]:
        forms = sp["pokemon_v2_pokemons"]
        if not forms:
            print("skipping %s: no default form" % sp["name"], file=sys.stderr)
            continue
        form = forms[0]
        names = sp["pokemon_v2_pokemonspeciesnames"]
        display = names[0]["name"] if names else sp["name"].title()
        types = [t["pokemon_v2_type"]["name"] for t in form["pokemon_v2_pokemontypes"]]
        bst = sum(s["base_stat"] for s in form["pokemon_v2_pokemonstats"])
        out.append({"i": sp["id"], "n": display, "t": types, "g": sp["generation_id"], "b": bst, "r": tier(sp, bst)})

    roster = {"v": 1, "generated": datetime.date.today().isoformat(), "pokemon": out}
    path = pathlib.Path(__file__).resolve().parent.parent / "pokemon.json"
    path.write_text(json.dumps(roster, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    counts = {}
    for p in out:
        counts[p["r"]] = counts.get(p["r"], 0) + 1
    print("wrote %s: %d pokemon, tiers %s" % (path.name, len(out), counts))


if __name__ == "__main__":
    main()
