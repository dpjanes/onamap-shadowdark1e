import yaml # type: ignore
import re
import os
import string
from types import SimpleNamespace

with open("shadowdark_monsters.yaml", "r") as fin:
    monsters = yaml.safe_load(fin)

def scrub(d):
    if isinstance(d, dict):
        if "DELETE" in d:
            return None
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

    moves = monster.get("moves", [])
    if moves == [{'range': 'near', 'type': ''}]:
        monster["moves"] = []

    skills = monster.get("skills", [])
    monster_bonuses = []
    weapons = []
    spells = []

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
        else:
            damage = attack.get("damage", None)
            extras = None
            if damage:
                parts = damage.split(" + ", 1)
                if len(parts) == 2:
                    damage, extras = parts

            if extras:
                found = False
                for skill in skills:
                    if extras not in skill["name"].lower():
                        continue

                    extras = f'''{skill["name"]}: {skill["description"]}'''
                    found = True

                    skill["DELETE"] = True
                    break

            weapon_bonuses = []
            weapon = {
                "name": attack_name,
                "bonuses": weapon_bonuses,
                "damage": damage,
                "description": extras,
            }
            weapons.append(weapon)

            if tohit:
                weapon_bonuses.append({
                    "key": "attack.tohit",
                    "value": tohit
                })
 
        for key in [ "tohit", "damage", "_range" ]:
            if key in attack:
                del attack[key]

    monster["weapons"] = weapons
    monster["attacks"] = attacks
    monster["bonuses"] = monster_bonuses

    monster = scrub(monster)
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
