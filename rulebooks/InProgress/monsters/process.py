import yaml # type: ignore
import re
import os
import string
from types import SimpleNamespace

with open("shadowdark_monsters.yaml", "r") as fin:
    monsters = yaml.safe_load(fin)

def scrub(d):
    if isinstance(d, dict):
        return {k: scrub(v) for k, v in d.items() if v}
    elif isinstance(d, list):
        return [scrub(i) for i in d if i]
    else:
        return d
    
for monster in monsters:
    monster_name = monster["name"]
    monster_name = re.sub("[^A-Za-z]", "_", monster_name)
    monster_name = re.sub("_+", "_", monster_name)

    level = f"{monster['level']['value']:02}"
    if level != "01":
        continue

    os.makedirs(level, exist_ok=True)

    monster["id"] = f"monster:Core:{monster_name}:{level}"

    monster_bonuses = []

    attacks = monster.get("attacks", [])
    for attack in attacks:
        attack_bonuses = []

        attack_name = attack["name"] = string.capwords(attack["name"])
        tohit = attack.get("tohit", 0)
        range = attack.get("range", None)

        if attack_name == "Spell":
            monster_bonuses.append({
                "key": "spells.cast",
                "value": tohit
            })
            # attack["DELETE"] = True
            pass

        if range == "near":
            attack["range"] = "melee"
            # attack["DELETE"] = True
            pass

        if tohit:
            del attack["tohit"]
            attack_bonuses.append({
                "key": "attack.tohit",
                "value": tohit
            })

        if attack_bonuses:
            attack["bonuses"] = attack_bonuses

    monster["attacks"] = [attack for attack in attacks if not attack.get("DELETE")]
    monster["bonuses"] = [bonus for bonus in monster_bonuses if not bonus.get("DELETE")]

    monster = scrub(monster)
    monster = scrub(monster)

    with open(f"{level}/{monster_name}.yaml", "w") as fout:
        monster_ordered = {
            "id": monster.pop("id"), 
            "name": monster.pop("name"), 
            "description": monster.pop("description"),
        }
        monster_ordered.update(monster)
        fout.write(yaml.dump(monster_ordered, sort_keys=False))
        fout.write("\n")
