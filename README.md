# MagicDuel
Need ruleset in order to play, computer takes care of rest

# ⭐ **GAME RULES SHEET (FINAL VERSION)**

## 🎮 **Basic Structure**

* The game has **two players**.
* Each round, **each player takes a turn**.
* **Each player gets 2 moves per turn**.
* Moves can be spent on any combination of actions (attack, summon, heal+shield, gain magic, etc.).

---

# ❤️ **Player Stats**

Each player tracks:

### **Health**

* Max HP = **25**
* Cannot exceed max.

### **Magic Power**

* Starts at 0 unless modified.
* Used for attacks and summoning.

### **Burn**

* A non-negative integer.
* Burn **bypasses shields**.
* Burn **stacks**.
* Burn applies every time the enemy hits you with a *burn-capable* normal attack.

### **Shield**

* A shield value that:

  * **Persists for the entire game**.
  * **Reduces by 1 at the start of the player's turn** (minimum 0).
  * So shields “decay” automatically each turn.
* Reduces **normal** (non-piercing) damage.

---

# 🛠️ **Moves a Player Can Use Each Turn**

The player gets **2 of these moves** per turn:

---

## **1. Attack**

Two types:

### **Normal Attack**

* Base = **3 damage**
* * **All magic power** (magic is spent entirely).
* * **Burn (0–2)** chosen by the attacker *as long as the attack hits the player (not shield)*.
* Shield reduces normal damage.
* Burn **ignores shield** but applies only if the attack hits HP.
* If damage is fully absorbed by shield, **no burn applies**.

### **Piercing Attack**

* Always **5 damage**.
* Ignores shields completely.
* **Cannot apply burn**.

---

## **2. Heal + Shield (Combined Action)**

*This action is now a single move.*

Player chooses:

* **Heal amount?** (always: +5 HP, capped at 25)
* Healing also **removes all burn and negative effects** on the healer.
* AND the player chooses:
* **Shield amount to add?** (any non-negative integer; stacks with current shield)
* Shield still decays by 1 each turn automatically.

---

## **3. Gain Magic**

* Player gains **+4 Magic Power**.

---

## **4. Summon a Minion**

Each player may control **up to 2 minions**.

Minion types:

---

# 🧊 **Minion: Bubble**

* Costs **2 Magic**.
* Starts with **6 HP**.
* On the **start of its owner’s turn**, it gives **+1 Magic**.
* On the **4th turn after being summoned**, it **explodes**:

  * Bubble dies.
  * Player gains **Magic equal to the Bubble’s remaining HP**.
* If the player already has 2 minions:

  * Additional Bubble cast **does not summon a 3rd one**.
  * Instead, one Bubble is chosen and **buffed: +2 HP**.
  * Bubble buffs *do not* increase its explosion timer.

---

# 👻 **Minion: Specter**

* Costs **5 Magic**.
* Starts with:

  * **10 HP**
  * **1 attack damage**
  * **1 burn**
* On its owner’s turn, each Specter can attack, but the player must choose:

  * Attack enemy player?
  * Attack a Bubble?
  * Attack a Specter?
* Only **normal damage** (not piercing).
* Burn applies normally.
* If a player already has 2 minions:

  * Summoning another Specter **buffs an existing Specter**:

    * +1 HP
    * +1 attack damage

---

# ⚔️ **Damage and Targeting Rules**

### When attacking with minions:

* Player is asked where each minion attacks.
* Specters can apply burn.
* Bubble does **not** attack.

### When targeting minions:

* Damage goes directly to their HP.
* If HP ≤ 0 → minion dies.

### Order of start-of-turn events:

1. Shields decay (shield = max(shield-1, 0))
2. Bubbles give +1 magic
3. Bubbles check if it is their 4th round → if yes, explode
4. Then player takes their 2 moves

---

# 🎲 **Turn Structure (Exact Sequence)**

### **Start of Player Turn**

1. Shield reduces by 1 (min 0)
2. Each Bubble gives +1 magic
3. Each Bubble checks explosion turn → explode if necessary
4. Player chooses **2 moves**
5. After moves, Specters attack (based on chosen targets)

---

# 🏁 **Win Condition**

* A player reaches **0 HP or less** → they lose.
* If both die simultaneously → tie.
