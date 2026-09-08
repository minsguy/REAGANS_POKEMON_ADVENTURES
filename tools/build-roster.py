"""Build pokemon.json for Reagan's Pokemon Adventures from PokeAPI's GraphQL endpoint.

Run once (or whenever a new generation lands):
    python tools/build-roster.py

Output: pokemon.json in the repo root. Fields per entry are kept short to keep the file small:
    i = national dex id, n = display name, t = types, g = generation, b = base stat total,
    r = rarity tier used for spawn weighting and catch odds, h = height in metres,
    m / ms = size in KB of the regular / shiny 3D model in the Pokemon-3D-api assets repository
    at the pinned commit (0 = no model). Sizes come from GitHub's tree API (metadata only);
    no model files are downloaded by this script.
"""
import json, os, subprocess, sys, urllib.request, datetime, pathlib

ENDPOINT = "https://beta.pokeapi.co/graphql/v1beta"
ASSETS_REPO = "Pokemon-3D-api/assets"
ASSETS_SHA = "429de1288cea0d43f5b4f56305d2276e94239d65"   # pinned; bump deliberately, never track main
QUERY = """{ pokemon_v2_pokemonspecies(order_by:{id:asc}) {
  id name is_legendary is_mythical generation_id
  pokemon_v2_pokemonspeciesnames(where:{language_id:{_eq:9}}) { name }
  pokemon_v2_pokemons(where:{is_default:{_eq:true}}) {
    height
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


def model_sizes():
    """{('regular'|'shiny', id): size_kb} from the GitHub tree listing at the pinned commit."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        try:
            token = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, check=True).stdout.strip()
        except Exception:
            token = None
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "reagans-pokemon-adventures roster builder"}
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request("https://api.github.com/repos/%s/git/trees/%s?recursive=1" % (ASSETS_REPO, ASSETS_SHA), headers=headers)
    with urllib.request.urlopen(req, timeout=120) as r:
        tree = json.load(r)
    if tree.get("truncated"):
        sys.exit("GitHub tree listing was truncated; cannot trust model sizes")
    sizes = {}
    for entry in tree["tree"]:
        path = entry.get("path", "")
        for kind in ("regular", "shiny"):
            prefix = "models/opt/%s/" % kind
            if entry.get("type") == "blob" and path.startswith(prefix) and path.endswith(".glb"):
                stem = path[len(prefix):-4]
                if stem.isdigit():
                    sizes[(kind, int(stem))] = int(round(entry["size"] / 1024))
    return sizes


def main():
    sizes = model_sizes()
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
        height_m = round((form.get("height") or 10) / 10, 2)
        out.append({"i": sp["id"], "n": display, "t": types, "g": sp["generation_id"], "b": bst, "r": tier(sp, bst),
                    "h": height_m, "m": sizes.get(("regular", sp["id"]), 0), "ms": sizes.get(("shiny", sp["id"]), 0)})

    roster = {"v": 2, "generated": datetime.date.today().isoformat(),
              "assets": {"repo": ASSETS_REPO, "sha": ASSETS_SHA}, "pokemon": out}
    path = pathlib.Path(__file__).resolve().parent.parent / "pokemon.json"
    path.write_text(json.dumps(roster, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    counts = {}
    for p in out:
        counts[p["r"]] = counts.get(p["r"], 0) + 1
    with_model = sum(1 for p in out if p["m"])
    print("wrote %s: %d pokemon, tiers %s, %d with a 3D model" % (path.name, len(out), counts, with_model))


if __name__ == "__main__":
    main()
