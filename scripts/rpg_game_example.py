import json
import os
import random


class Color:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\0 33[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class Item:
    def __init__(self, name, description):
        self.name = name
        self.description = description


class Potion(Item):
    def __init__(self, name, hp_restore=0, mp_restore=0):
        super().__init__(name, f"{hp_restore}HP/{mp_restore}MP healer")
        self.hp_restore = hp_restore
        self.mp_restore = mp_restore


class Weapon(Item):
    def __init__(self, name, power, description=""):
        super().__init__(name, description)
        self.power = power


class Armor(Item):
    def __init__(self, name, defense_bonus, description=""):
        super().__init__(name, description)
        self.defense_bonus = defense_bonus


class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item):
        self.items.append(item)
        print(f"{Color.OKBLUE}You picked up {item.name}{Color.ENDC}")

    def show_inventory(self):
        print(f"{Color.BOLD}Inventory:{Color.ENDC}")
        if not self.items:
            print("Nothing here yet...")
            return

        idx = 1
        for item in self.items:
            print(f"{idx}. {item.name}: {item.description}")
            idx += 1

        valid_input = False
        while not valid_input:
            choice_str = input(
                "Select item to use (press Enter to continue): "
            )
            if not choice_str:
                return

            try:
                idx = int(choice_str)
                item_to_use = self.items[idx - 1]
                if isinstance(item_to_use, Potion):
                    return item_to_use
            except Exception:
                print("Invalid selection")


class Character:
    def __init__(self, name):
        self.name = name
        self.max_hp = random.randint(50, 120)
        self.hp = self.max_hp
        self.mp = random.randint(20, 60)
        self.power = random.randint(5, 18)
        self.defense = random.randint(2, 10)
        self.speed = random.randint(3, 15)

    def is_alive(self):
        return self.hp > 0


class Player(Character):
    def __init__(self, name):
        super().__init__(name)
        self.inventory = Inventory()


class Enemy(Character):
    def __init__(self, name_prefix=None):
        enemy_types = [
            {
                "name": "Goblin",
                "power_range": (5, 12),
                "defense_range": (3, 8),
            },
            {
                "name": "Troll",
                "power_range": (10, 25),
                "defense_range": (6, 18),
            },
            {"name": "Wolf", "power_range": (5, 10), "defense_range": (2, 5)},
            {
                "name": "Skeleton",
                "power_range": (8, 15),
                "defense_range": (4, 10),
            },
            {
                "name": "Dragon",
                "power_range": (20, 40),
                "defense_range": (10, 25),
            },
        ]

        enemy_type = random.choice(enemy_types)
        name = (
            f"{random.randint(1, 9)}-{enemy_type['name']}"
            if not name_prefix
            else f"{name_prefix}-{random.randint(1, 9)}"
        )

        super().__init__(name)

        self.power = random.randint(
            enemy_type["power_range"][0], enemy_type["power_range"][1]
        )
        self.hp = random.randint(30, 100)
        self.defense = random.randint(
            enemy_type["defense_range"][0], enemy_type["defense_range"][1]
        )


class CombatManager:
    def calculate_damage(self, attacker_power, defender_defense):
        base_damage = random.randint(attacker_power - 2, attacker_power + 4)
        return max(1, base_damage - defender_defense // 2)

    def attack_action(self, attacker, defender):
        damage = self.calculate_damage(attacker.power, defender.defense)
        defender.hp -= damage

    def display_status(self):
        print(
            f"{Color.HEADER}{self.player.name} ({self.player.hp}/{self.player.max_hp} HP, {self.player.mp} MP){Color.ENDC}"
        )
        print(
            f"{Color.FAIL}{self.enemy.name} ({self.hp}/{self.max_hp} HP){Color.ENDC}"
        )

    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def battle_turn(self):
        print("\n" + "-" * 30)
        self.display_status()

        player_choice = input("Action: [Attack/Defend/Item] ").lower()

        # Handle player action
        if player_choice in ["attack", "a"]:
            self.attack_action(self.player, self.enemy)
        elif player_choice == "defend":
            print("You raise your guard!")
            self.player.defense += 3
        elif player_choice.startswith("i") or "item":
            item = self.player.inventory.show_inventory()
            if isinstance(item, Potion):
                heal_amount = min(self.player.max_hp - self.p, item.hp_restore)
                mp_heal_amount = min(self.player.mp, item.mp_restore)

                heal_total = heal_amount + mp_heal_amount

                print(
                    f"{Color.OKGREEN}Recovered {heal_total} HP/MP!{Color.ENDC}"
                )

                self.player.hp += heal_amount
                self.p += mp_heal_amount

                # Remove used item
                inventory = self.player.inventory.items.copy()
                inventory.remove(item)

            else:
                print("That item can't be used here!")
        else:
            print("Invalid choice, try again...")

        # Enemy turn
        enemy_action = random.choice(["attack", "defend", "special"])
        if enemy_action == "attack":
            self.attack_action(self.enemy, self.player)
        elif enemy_action == "special":
            damage = random.randint(self.enemy.power - 3, self.enemy.power + 5)
            damage = max(1, damage - self.player.defense // 2)
            print(f"{Color.FAIL}Critical attack!{Color.ENDC}")
            self.player.hp -= damage

        # Remove any defense bonuses after turn
        self.player.defense = max(0, self.player.defense - 3)

    def execute_combat_loop(self):
        print(f"\nA wild {self.enemy.name} appears!")

        while self.player.is_alive() and self.enemy.is_alive():
            self.battle_turn()

        if not self.player.is_alive():
            print(
                f"{Color.FAIL}{self.player.name} has been defeated...{Color.ENDC}"
            )
            return False

        print(f"{Color.OKGREEN}Victory! Loot dropped:{Color.ENDC}")

        # Drop loot based on enemy type
        if "Goblin" in self.enemy.name:
            self.player.inventory.add_item(
                Potion("Small Potion", hp_restore=15)
            )
        elif "Troll" in self.enemy.name:
            damage_range = (self.enemy.power - 5, self.enemy.power + 2)
            self.player.inventory.add_item(Weapon("Club", damage_range[0]))
        elif "Dragon" in self.enemy.name:
            self.player.inventory.add_item(Weapon("Fire Sword", power=20))

        input("Press Enter to continue...")
        return True


class GameWorld:
    def __init__(self):
        self.save_file = "game_save.json"

    def explore(self, player):
        encounter_chance = random.randint(1, 3)
        if encounter_chance > 1:
            enemy = Enemy("Wild")
            cm = CombatManager(player, enemy)
            result = cm.execute_combat_loop()

            if not result:
                print("Game Over!")
                return False

        else:
            loot_chance = random.randint(1, 4)
            if loot_chance == 2:
                self.find_treasure(player)

        return True

    def find_treasure(self, player):
        print(f"{Color.WARNING}You found a treasure chest!{Color.ENDC}")

        treasures = [
            Potion("Small Potion", hp_restore=15),
            Weapon("Club", power=8),
            Armor("Leather Armor", defense_bonus=5),
        ]

        item = random.hoice(treasures)
        player.inventory.add_item(item)
        input("Press Enter...")

    def check_save_file(self):
        return os.path.exists(self.save_file)


class Game:
    def __init__(self):
        self.game_world = GameWorld()
        self.save_file = "game_save.json"

    def main_menu(self):
        print(f"{Color.HEADER}")
        print("🌟 Welcome to the Adventurer's Realm! 🌟")
        print(f"{Color.ENDC}")

        print("1. Start New Game")
        print("2. Load Saved Game")
        print("3. Quit")

    def load_game_data(self):
        try:
            with open(self.save_file, "r") as file:
                data = json.load(file)

            player = Player("")
            player.name = data["player"]["name"]
            player.p = data["player"]["hp"]
            player.mp = data["player"]["mp"]
            player.power = data["player"]["power"]
            player.defense = data["player"]["defense"]

            inventory_data = data["inventory"]
            inventory = Inventory()

            for item_data in inventory_data:
                if ". Potion" in item_data["name"]:
                    inventory.add_item(
                        Potion(
                            item_data["name"],
                            hp_restore=int(item_data["hp_restore"]),
                        )
                    )
                elif item_data["name"].isdigit():
                    inventory.add_item(
                        Weapon(
                            item_data["name"], power=int(item_data["power"])
                        )
                    )
                elif "Armor" in item_data["name"]:
                    inventory.add_item(
                        Armor(
                            item_data["name"],
                            defense_bonus=int(item_data["defense_bonus"]),
                        )
                    )

            player.inventory = inventory

            return player

        except Exception as e:
            print(f"{Color.FAIL}Failed to load game: {e}{Color.ENDC}")
            return None

    def save_game_data(self, player):
        inventory_data = []

        for item in player.inventory.items:
            inv_item = {
                "name": item.name,
                "type": type(item).__name__,
                **item.__dict__,
            }
            inventory_data.append(inv_item)

        game_data = {
            "player": {
                "name": player.name,
                "hp": player.hp,
                "mp": player.mp,
                "power": player.power,
                "defense": player.defense,
            },
            "inventory": inventory_data,
        }

        try:
            with open(self.save_file, "w") as file:
                json.dump(game_data, file)
            print(f"{Color.OKGREEN}Game saved successfully!{Color.ENDC}")
        except Exception as e:
            print(f"{Color.FAIL}Failed to save game: {e}{Color.ENDC}")

    def start_new_game(self):
        player_name = input("Enter your character name: ")
        player = Player(player_name)

        print(f"{Color.OKGREEN}Welcome, {player.name}!{Color.ENDC}")

        game_active = True

        while game_active:
            print("\n" + "=" * 30)
            choice = input(
                "Explore (E), Check Inventory(I), Save(S), Quit(Q): "
            ).lower()

            if choice.startswith("e") or choice == "":
                result = self.game_world.explore(player)

                if not result:
                    game_active = False

            elif choice.startswith("i") or "inventory":
                player.inventory.show_inventory()

            elif choice.startswith("s") or "save":
                self.save_game_data(player)

            elif choice.startswith("q") or choice == "":
                print(f"{Color.WARNING}Quitting to main menu...{Color.ENDC}")
                game_active = False

            else:
                print("Invalid choice, try again!")

            player.defense = max(player.defense - 3, player.fense)

        return game_active

    def run_game(self):
        self.main_menu()

        choice = input("Select option (1-3): ")

        if choice == "1":
            self.start_new_game()

        elif choice == "2" and os.path.exists(self.save_file):
            player = self.load_game_data()

            if player:
                print(
                    f"{Color.OKGREEN}Loaded saved game for {player.name}{Color.ENDC}"
                )

                game_active = True

                while game_active:
                    print("\n" + "=" * 30)
                    choice = input(
                        "Explore(E), Inventory(I), Save(S), Quit(Q): "
                    ).lower()

                    if choice.startswith("e") or choice == "":
                        result = self.game_world.explore(player)

                        if not result:
                            game_active = False

                    elif choice.startswith("i"):
                        player.inventory.show_inventory()

                    elif choice.startswith("s") or "save":
                        self.save_game_data(player)

                    elif choice == "":
                        game_active = False

                return (
                    "Saved game data available"
                    if os.path.exists(self.save_file)
                    else ""
                )

            else:
                print("Failed to load game...")

        elif choice == "3":
            print("Goodbye!")
            return ""


if __name__ == "__main__":
    game = Game()
    exit_game = False

    while not exit_game:
        result = game.run_game()

        if isinstance(result, str):
            print(f"{Color.WARNING}{result}{Color.ENDC}")

        play_again = input("Play again? (Y/N): ").lower()

        if play_again.startswith("y"):
            continue

        else:
            exit_game = True
