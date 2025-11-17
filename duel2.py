# duel_game.py
# Interactive 2-player duel game per user's final rules.
# VERSION 2: Added Fiery Shield, split Heal/Shield, removed Pass.

from dataclasses import dataclass, field
from typing import List, Optional

MAX_HP = 25

@dataclass
class Minion:
    name: str
    hp: int
    owner: 'Player'
    age: int = 0
    attack: int = 0
    special: dict = field(default_factory=dict) 

    def start_of_owner_turn(self):
        """
        Handles start-of-turn logic for this minion (age, Bubble MP/Explode).
        Returns a list of event messages and an action string ('explode' or None).
        """
        self.age += 1
        events = []
        if self.name == 'Bubble':
            # Bubble explodes on the 4th turn *after being summoned*.
            # This means it triggers when age becomes 4.
            if self.age >= 4:
                mp_gain = max(0, self.hp)
                self.owner.mp += mp_gain
                events.append(f"⭐ {self.owner.name}'s Bubble (Age {self.age}) explodes and gives {mp_gain} MP!")
                return events, 'explode'
            else:
                self.owner.mp += 1
                events.append(f"  {self.owner.name}'s Bubble gives +1 MP (now {self.owner.mp}).")
                return events, None
        return events, None

    def take_damage(self, dmg: int):
        self.hp -= dmg
        return self.hp <= 0 # Returns True if died

    def __str__(self):
        if self.name == 'Specter':
            return f"👻 Specter (HP:{self.hp}, ATK:{self.attack}, Age:{self.age})"
        if self.name == 'Bubble':
            return f"🧊 Bubble (HP:{self.hp}, Age:{self.age}/4)"
        return f"{self.name}(HP:{self.hp}, Age:{self.age})"

@dataclass
class Player:
    name: str
    hp: int = MAX_HP
    mp: int = 0
    burn: int = 0
    shield: int = 0
    minions: List[Minion] = field(default_factory=list)

    def start_turn(self):
        """
        Handles all start-of-turn events for the player.
        1. Shield decay
        2. Burn damage
        3. Minion start-of-turn triggers (Bubble MP/Explode)
        """
        msgs = []
        # 1. Shield decay
        if self.shield > 0:
            self.shield -= 1
            msgs.append(f"  {self.name}'s shield decays by 1 -> {self.shield}.")
        
        # 2. Burn damage
        if self.burn > 0:
            self.hp -= self.burn
            msgs.append(f"  🔥 {self.name} takes {self.burn} burn damage -> HP {self.hp}.")
        
        # 3. Minion triggers
        remove_list = []
        for m in list(self.minions): # Iterate over a copy
            events, action = m.start_of_owner_turn()
            msgs.extend(events)
            if action == 'explode':
                remove_list.append(m)
        
        for m in remove_list:
            if m in self.minions:
                self.minions.remove(m)
                msgs.append(f"  {m.name} has been removed.")
        
        return msgs

    def heal_self(self):
        """
        Handles the healing portion of the Heal+Shield move.
        Heals 5 HP (capped) and removes all burn.
        """
        old_hp = self.hp
        self.hp = min(MAX_HP, self.hp + 5)
        removed_burn = self.burn
        self.burn = 0
        heal_amt = self.hp - old_hp
        msg = f"  {self.name} heals +{heal_amt} HP (now {self.hp})"
        if removed_burn > 0:
            msg += f" and removes all {removed_burn} burn."
        else:
            msg += "."
        return msg

    def create_shield(self, amount: int):
        """Handles adding shield. Used by multiple actions."""
        if amount < 0:
            amount = 0
        self.shield += amount
        return f"  {self.name} increases shield by {amount} -> {self.shield}."

    def take_attack(self, dmg: int, is_piercing=False):
        """
        Applies damage to the player.
        Returns: (actual_hp_damage, absorbed_by_shield, hp_after_hit)
        """
        if is_piercing:
            self.hp -= dmg
            return dmg, 0, self.hp
        else:
            if self.shield >= dmg:
                self.shield -= dmg
                return 0, dmg, self.hp
            else:
                absorbed = self.shield
                self.shield = 0
                actual = dmg - absorbed
                self.hp -= actual
                return actual, absorbed, self.hp

    def add_minion(self, minion: Minion):
        self.minions.append(minion)

    def __str__(self):
        mstr = ', '.join(str(m) for m in self.minions) if self.minions else "None"
        return f"[{self.name}]: HP {self.hp}/{MAX_HP}, MP {self.mp}, Burn {self.burn}, Shield {self.shield}\n  Minions: {mstr}"

def prompt_int(prompt, low=None, high=None, default=None):
    """Helper function to get validated integer input."""
    while True:
        try:
            raw = input(prompt).strip()
            if raw == "" and default is not None:
                return default
            val = int(raw)
            if low is not None and val < low:
                print(f"Value must be >= {low}.")
                continue
            if high is not None and val > high:
                print(f"Value must be <= {high}.")
                continue
            return val
        except ValueError:
            print("Please enter an integer.")

def choose_target(attacker: Player, defender: Player):
    """
    Lets the attacking *player* choose a target (defender or defender's minions).
    Returns: ('player', None) or ('minion', index_in_minion_list)
    """
    if defender.minions:
        print(f"Defender {defender.name}'s minions:")
        for i, m in enumerate(defender.minions, 1):
            print(f"  {i}: {m}")
        options = f"Choose target minion 1-{len(defender.minions)} or 0 to target {defender.name}: "
        choice = prompt_int(options, low=0, high=len(defender.minions))
        if choice == 0:
            return ('player', None)
        else:
            return ('minion', choice - 1)
    else:
        print(f"{defender.name} has no minions. Targeting player.")
        return ('player', None)

def perform_player_attack(attacker: Player, defender: Player):
    """Handles the logic for a player's Attack move."""
    print("Choose attack type:")
    print(f"  1: Normal Attack (3 + all {attacker.mp} MP, can add burn 0-2)")
    print("  2: Piercing Attack (5 damage, ignores shield, no burn)")
    choice = prompt_int("Attack type (1-2): ", low=1, high=2)

    if choice == 1:
        # Normal Attack
        base = 3
        mp_used = attacker.mp
        total = base + mp_used
        attacker.mp = 0 # Spend all MP
        print(f"  {attacker.name} uses Normal Attack for {total} damage (spending {mp_used} MP).")
        
        burn_to_apply = prompt_int("  Burn to apply on HP hit (0-2): ", low=0, high=2)
        target_type, idx = choose_target(attacker, defender)
        
        if target_type == 'player':
            actual, absorbed, hp_after = defender.take_attack(total)
            print(f"  Attack deals {total}. Shield absorbed {absorbed}. HP lost {actual}. {defender.name} HP: {hp_after}.")
            if actual > 0 and burn_to_apply > 0: # Burn only applies if HP is hit
                defender.burn += burn_to_apply
                print(f"  🔥 {defender.name} gets {burn_to_apply} burn (now {defender.burn}).")
        else:
            m = defender.minions[idx]
            died = m.take_damage(total)
            print(f"  Attack hits {m.name} for {total} -> HP {m.hp}.")
            if died:
                print(f"  💀 {m.name} dies.")
                defender.minions.pop(idx)

    else:
        # Piercing Attack
        total = 5 # Always 5 damage
        print(f"  {attacker.name} uses Piercing Attack for 5 damage.")
        # Does NOT spend MP
        
        target_type, idx = choose_target(attacker, defender)
        if target_type == 'player':
            actual, _, hp_after = defender.take_attack(total, is_piercing=True)
            print(f"  Piercing hit: {actual} damage -> {defender.name} HP: {hp_after}.")
        else:
            m = defender.minions[idx]
            died = m.take_damage(total) # Piercing also ignores minion shields if they had them
            print(f"  Piercing hits {m.name} for {total} -> HP {m.hp}.")
            if died:
                print(f"  💀 {m.name} dies.")
                defender.minions.pop(idx)

def perform_summon(attacker: Player):
    """Handles the logic for a player's Summon move."""
    print("Choose summon:")
    print(f"  1: 🧊 Bubble (2 MP) - Gives +1 MP/turn, explodes for HP as MP on 4th turn.")
    print(f"  2: 👻 Specter (5 MP) - 10 HP, 1 ATK, 1 Burn.")
    choice = prompt_int("Summon (1-2): ", low=1, high=2)

    if choice == 1:
        # Summon Bubble
        cost = 2
        if attacker.mp < cost:
            print("  Not enough MP.")
            return False # Move failed
        
        if len(attacker.minions) < 2:
            attacker.mp -= cost
            b = Minion(name='Bubble', hp=6, owner=attacker)
            attacker.add_minion(b)
            print(f"  Summoned 🧊 Bubble.")
        else:
            # 2 minions already. Can only buff an existing Bubble.
            bubbles = [m for m in attacker.minions if m.name == 'Bubble']
            if not bubbles:
                print(f"  Cannot cast Bubble: You have 2 minions, but no Bubbles to buff.")
                return False # Move failed
            
            attacker.mp -= cost
            print("  Choose a Bubble to buff (+2 HP):")
            for i, m in enumerate(bubbles, 1):
                print(f"    {i}: {m}")
            idx = prompt_int("  Choose: ", low=1, high=len(bubbles)) - 1
            m_to_buff = bubbles[idx]
            m_to_buff.hp += 2
            print(f"  {m_to_buff.name} buffed -> HP {m_to_buff.hp}.")

    else:
        # Summon Specter
        cost = 5
        if attacker.mp < cost:
            print("  Not enough MP.")
            return False # Move failed

        if len(attacker.minions) < 2:
            attacker.mp -= cost
            s = Minion(name='Specter', hp=10, owner=attacker, attack=1, special={'burn_on_hit':1})
            attacker.add_minion(s)
            print(f"  Summoned 👻 Specter.")
        else:
            # 2 minions already. Can only buff an existing Specter.
            specters = [m for m in attacker.minions if m.name == 'Specter']
            if not specters:
                print(f"  Cannot cast Specter: You have 2 minions, but no Specters to buff.")
                return False # Move failed
            
            attacker.mp -= cost
            print("  Choose a Specter to buff (+1 HP, +1 ATK):")
            for i, m in enumerate(specters, 1):
                print(f"    {i}: {m}")
            idx = prompt_int("  Choose: ", low=1, high=len(specters)) - 1
            m_to_buff = specters[idx]
            m_to_buff.hp += 1
            m_to_buff.attack += 1
            print(f"  {m_to_buff.name} buffed -> HP {m_to_buff.hp}, ATK {m_to_buff.attack}.")
    
    return True # Move succeeded

def minion_attack_phase(player: Player, enemy: Player):
    """
    Handles the attack phase for all of player's Specters.
    Occurs *after* the player's 2 moves.
    """
    specters = [m for m in list(player.minions) if m.name == "Specter" and m in player.minions]
    if not specters:
        return # No specters to attack with
    
    print(f"\n--- {player.name}'s Minion Attack Phase ---")
    
    for i, m in enumerate(specters):
        if m not in player.minions:
            continue 
        
        print(f"\n👻 {player.name}'s Specter {i+1} (ATK: {m.attack}) attacks...")
        
        # Build target list (enemy player + enemy minions)
        targets = [enemy] + enemy.minions
        print(f"  0: {enemy.name} (Player)")
        for j, em in enumerate(enemy.minions, 1):
            print(f"  {j}: {em}")
        
        tgt_idx = prompt_int("  Choose target: ", low=0, high=len(enemy.minions))
        
        dmg = m.attack
        
        if tgt_idx == 0:
            # Targeting player
            actual, absorbed, hp = enemy.take_attack(dmg)
            print(f"  Specter hits {enemy.name} for {dmg}. Shield absorbed {absorbed}. HP lost {actual}. {enemy.name} HP: {hp}.")
            if actual > 0: # Burn only applies if HP is hit
                enemy.burn += 1 # Per rules, Specter applies 1 burn
                print(f"  🔥 {enemy.name} gains 1 burn (now {enemy.burn}).")
        else:
            # Targeting minion
            t_minion = enemy.minions[tgt_idx - 1]
            died = t_minion.take_damage(dmg)
            print(f"  Specter hits {t_minion.name} for {dmg} -> HP {t_minion.hp}.")
            if died:
                print(f"  💀 {t_minion.name} dies.")
                enemy.minions.pop(tgt_idx - 1)
        
        # Check for game over after each minion attack
        if enemy.hp <= 0:
            return # Stop attack phase, game will end

def print_state(p1: Player, p2: Player):
    """Prints the current game state."""
    print("\n" + "="*25)
    print("--- CURRENT GAME STATE ---")
    print(p1)
    print(p2)
    print("="*25 + "\n")

def game_loop():
    p1 = Player("Player 1")
    p2 = Player("Player 2")
    players = [p1, p2]
    turn = 0

    print("Starting duel!")
    print_state(p1, p2)

    while True:
        current = players[turn % 2]
        opponent = players[(turn + 1) % 2]

        print(f"\n=== {current.name}'s TURN (Turn {turn//2 + 1}) ===")

        # 1. Start-of-turn effects
        for e in current.start_turn():
            print(e)

        if current.hp <= 0:
            print(f"{current.name} died from burn or explosion! {opponent.name} wins!")
            break

        # Check for simultaneous death
        if opponent.hp <= 0 and current.hp <= 0:
            print("Both players died simultaneously! It's a TIE!")
            break
        
        print_state(current, opponent)

        # 2. Player takes 2 moves
        for move in range(1, 3):
            print(f"--- {current.name}'s Move {move}/2 ---")
            print("  1: Heal + Shield (+5 HP, Clear Burn, Add Shield)")
            print("  2: Create Shield (Shield only)")
            print("  3: Fiery Shield (Costs all MP, gives MP+3 Shield, needs MP > 0)")
            print("  4: Attack (Normal or Piercing)")
            print("  5: Summon (Bubble or Specter)")
            print("  6: Gain 4 MP")

            action_succeeded = True
            action = prompt_int("Choose action (1-6): ", low=1, high=6)

            if action == 1:
                # 1. Heal + Shield (all heals have shields)
                print(current.heal_self())
                amt = prompt_int("  Shield amount to add (0 or more): ", low=0, default=0)
                print(current.create_shield(amt))

            elif action == 2:
                # 2. Create Shield (not all shields have heal)
                amt = prompt_int("  Shield amount to add (0 or more): ", low=0, default=0)
                print(current.create_shield(amt))
            
            elif action == 3:
                # 3. Fiery Shield
                if current.mp > 0:
                    shield_gain = current.mp + 3
                    mp_cost = current.mp
                    current.mp = 0
                    # Use the create_shield function to add the shield
                    print(current.create_shield(shield_gain))
                    print(f"  (Spent {mp_cost} MP to gain {shield_gain} shield).")
                else:
                    print("  Cannot cast Fiery Shield without any magic.")
                    action_succeeded = False

            elif action == 4:
                # 4. Attack
                perform_player_attack(current, opponent)

            elif action == 5:
                # 5. Summon
                action_succeeded = perform_summon(current)
                if not action_succeeded:
                    print("  Move failed.") # e.g., not enough MP or no valid buff target

            elif action == 6:
                # 6. Gain Magic
                current.mp += 4
                print(f"  {current.name} gains +4 MP (now {current.mp}).")
            
            # Check for death mid-turn (e.g., from an attack)
            if opponent.hp <= 0:
                print_state(current, opponent)
                print(f"{opponent.name} dies! {current.name} wins!")
                return # End game immediately
            
            # Show state after a successful move
            if action_succeeded:
                print_state(current, opponent)

        # 3. After moves, Minions attack
        minion_attack_phase(current, opponent)

        # Check for death after minion attacks
        if opponent.hp <= 0:
            print_state(current, opponent)
            print(f"{opponent.name} dies! {current.name} wins!")
            return
        
        # Check for simultaneous death again (e.g., player died to burn, opponent to minions)
        if opponent.hp <= 0 and current.hp <= 0:
            print("Both players died simultaneously! It's a TIE!")
            break

        turn += 1

if __name__ == "__main__":
    game_loop()
