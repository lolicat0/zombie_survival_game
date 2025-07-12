import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time
import math

class ZombieSurvivalGame:
    def __init__(self, root):
        self.root = root
        self.root.title("🧟 ZOMBIE SURVIVAL APOCALYPSE 🧟")
        self.root.geometry("1000x700")
        self.root.configure(bg='#1a1a1a')
        self.root.resizable(False, False)
        
        # Game state
        self.player_health = 100
        self.player_max_health = 100
        self.player_ammo = 30
        self.player_max_ammo = 30
        self.zombies_killed = 0
        self.current_zombie = None
        self.game_over = False
        self.game_paused = False
        self.wave_number = 1
        self.zombies_in_wave = 0
        self.zombies_killed_this_wave = 0
        self.experience = 0
        self.level = 1
        self.weapon_damage = 20
        self.critical_chance = 10
        
        # Inventory
        self.health_kits = 3
        self.ammo_clips = 5
        self.grenades = 2
        self.armor = 0
        
        # Combat state
        self.is_reloading = False
        self.reload_time = 0
        self.zombie_attack_timer = 0
        
        # Animation variables
        self.screen_shake = 0
        self.blood_splatter = []
        self.muzzle_flash = False
        
        # Colors
        self.colors = {
            'bg': '#0d1117',
            'panel': '#161b22',
            'text': '#c9d1d9',
            'health': '#2ea043',
            'ammo': '#fd7e14',
            'danger': '#f85149',
            'warning': '#d29922',
            'success': '#2ea043',
            'zombie': '#6f42c1'
        }
        
        self.setup_gui()
        self.setup_keybindings()
        self.start_game_loop()
        
    def setup_gui(self):
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with style
        title_frame = tk.Frame(main_frame, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title_label = tk.Label(title_frame, text="🧟 ZOMBIE SURVIVAL APOCALYPSE 🧟", 
                              font=("Impact", 24, "bold"), 
                              fg='#ff6b6b', bg=self.colors['panel'])
        title_label.pack(pady=10)
        
        # Top stats panel
        self.setup_stats_panel(main_frame)
        
        # Game canvas (main play area)
        self.setup_game_canvas(main_frame)
        
        # Bottom control panel
        self.setup_control_panel(main_frame)
        
        # Side panels
        self.setup_side_panels(main_frame)
        
    def setup_stats_panel(self, parent):
        stats_frame = tk.Frame(parent, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        stats_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Health bar
        health_frame = tk.Frame(stats_frame, bg=self.colors['panel'])
        health_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(health_frame, text="HEALTH", font=("Arial", 10, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack()
        
        self.health_bar = ttk.Progressbar(health_frame, length=200, mode='determinate')
        self.health_bar.pack(pady=2)
        self.health_bar['maximum'] = 100
        self.health_bar['value'] = 100
        
        self.health_label = tk.Label(health_frame, text="100/100", 
                                    font=("Arial", 12, "bold"), 
                                    fg=self.colors['health'], bg=self.colors['panel'])
        self.health_label.pack()
        
        # Ammo display
        ammo_frame = tk.Frame(stats_frame, bg=self.colors['panel'])
        ammo_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(ammo_frame, text="AMMO", font=("Arial", 10, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack()
        
        self.ammo_label = tk.Label(ammo_frame, text="30/30", 
                                  font=("Arial", 16, "bold"), 
                                  fg=self.colors['ammo'], bg=self.colors['panel'])
        self.ammo_label.pack(pady=5)
        
        # Wave info
        wave_frame = tk.Frame(stats_frame, bg=self.colors['panel'])
        wave_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(wave_frame, text="WAVE", font=("Arial", 10, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack()
        
        self.wave_label = tk.Label(wave_frame, text="1", 
                                  font=("Arial", 16, "bold"), 
                                  fg=self.colors['warning'], bg=self.colors['panel'])
        self.wave_label.pack(pady=5)
        
        # Kills counter
        kills_frame = tk.Frame(stats_frame, bg=self.colors['panel'])
        kills_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(kills_frame, text="KILLS", font=("Arial", 10, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack()
        
        self.kills_label = tk.Label(kills_frame, text="0", 
                                   font=("Arial", 16, "bold"), 
                                   fg=self.colors['danger'], bg=self.colors['panel'])
        self.kills_label.pack(pady=5)
        
        # Level and XP
        level_frame = tk.Frame(stats_frame, bg=self.colors['panel'])
        level_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(level_frame, text="LEVEL", font=("Arial", 10, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack()
        
        self.level_label = tk.Label(level_frame, text="1", 
                                   font=("Arial", 16, "bold"), 
                                   fg=self.colors['success'], bg=self.colors['panel'])
        self.level_label.pack(pady=5)
        
    def setup_game_canvas(self, parent):
        canvas_frame = tk.Frame(parent, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        canvas_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.canvas = tk.Canvas(canvas_frame, bg='#000000', width=800, height=400)
        self.canvas.pack(padx=10, pady=10)
        
        # Game text area
        self.game_text = tk.Text(canvas_frame, height=8, width=100, 
                                font=("Consolas", 11), 
                                bg='#0d1117', fg='#00ff41',
                                insertbackground='#00ff41', 
                                wrap=tk.WORD, state=tk.DISABLED)
        self.game_text.pack(padx=10, pady=(0, 10))
        
        # Scrollbar for text
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.game_text.yview)
        self.game_text.configure(yscrollcommand=scrollbar.set)
        
    def setup_control_panel(self, parent):
        control_frame = tk.Frame(parent, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Command input
        input_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(input_frame, text="COMMAND:", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack(side=tk.LEFT)
        
        self.command_entry = tk.Entry(input_frame, font=("Arial", 14), 
                                     bg='#21262d', fg='#c9d1d9', 
                                     insertbackground='#c9d1d9', bd=0, 
                                     relief=tk.FLAT)
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        self.command_entry.bind('<Return>', self.process_command)
        
        # Action buttons with better styling
        button_frame = tk.Frame(control_frame, bg=self.colors['panel'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        buttons = [
            ("🔫 SHOOT", self.shoot_zombie, '#e74c3c'),
            ("🔄 RELOAD", self.reload_weapon, '#3498db'),
            ("💊 HEAL", self.heal_player, '#2ecc71'),
            ("💣 GRENADE", self.throw_grenade, '#e67e22'),
            ("🏃 RUN", self.run_away, '#9b59b6'),
            ("⏸️ PAUSE", self.toggle_pause, '#95a5a6')
        ]
        
        for text, command, color in buttons:
            btn = tk.Button(button_frame, text=text, command=command,
                           font=("Arial", 10, "bold"), bg=color, fg='white',
                           relief=tk.FLAT, bd=0, padx=15, pady=5,
                           activebackground=color, activeforeground='white')
            btn.pack(side=tk.LEFT, padx=5)
        
        # Hotkeys info
        hotkey_label = tk.Label(control_frame, 
                               text="HOTKEYS: SPACE=Shoot | R=Reload | H=Heal | G=Grenade | ESC=Run | P=Pause",
                               font=("Arial", 9), fg=self.colors['text'], bg=self.colors['panel'])
        hotkey_label.pack(pady=(0, 10))
        
    def setup_side_panels(self, parent):
        # Right panel for inventory and zombie info
        right_panel = tk.Frame(parent, bg=self.colors['panel'], relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        
        # Inventory
        tk.Label(right_panel, text="INVENTORY", font=("Arial", 12, "bold"), 
                fg=self.colors['text'], bg=self.colors['panel']).pack(pady=10)
        
        self.inventory_frame = tk.Frame(right_panel, bg=self.colors['panel'])
        self.inventory_frame.pack(fill=tk.X, padx=10)
        
        self.update_inventory_display()
        
        # Current zombie info
        tk.Label(right_panel, text="CURRENT THREAT", font=("Arial", 12, "bold"), 
                fg=self.colors['danger'], bg=self.colors['panel']).pack(pady=(20, 10))
        
        self.zombie_info_frame = tk.Frame(right_panel, bg=self.colors['panel'])
        self.zombie_info_frame.pack(fill=tk.X, padx=10)
        
        self.zombie_info_label = tk.Label(self.zombie_info_frame, text="No zombie present", 
                                         font=("Arial", 10), fg=self.colors['text'], 
                                         bg=self.colors['panel'], wraplength=150)
        self.zombie_info_label.pack()
        
    def setup_keybindings(self):
        self.root.bind('<space>', lambda e: self.shoot_zombie())
        self.root.bind('<Key-r>', lambda e: self.reload_weapon())
        self.root.bind('<Key-h>', lambda e: self.heal_player())
        self.root.bind('<Key-g>', lambda e: self.throw_grenade())
        self.root.bind('<Escape>', lambda e: self.run_away())
        self.root.bind('<Key-p>', lambda e: self.toggle_pause())
        self.root.focus_set()
        
    def start_game_loop(self):
        self.display_message("🎮 GAME STARTED! Survive the zombie apocalypse!")
        self.display_message("💡 Use hotkeys for faster combat or type commands!")
        self.start_wave()
        self.game_loop()
        
    def game_loop(self):
        if not self.game_over and not self.game_paused:
            self.update_game_state()
            self.update_visuals()
            
        self.root.after(50, self.game_loop)  # 20 FPS
        
    def update_game_state(self):
        # Handle reload timer
        if self.is_reloading:
            self.reload_time -= 1
            if self.reload_time <= 0:
                self.is_reloading = False
                self.display_message("🔄 Reload complete!")
                
        # Handle zombie attack timer
        if self.current_zombie and self.zombie_attack_timer > 0:
            self.zombie_attack_timer -= 1
            if self.zombie_attack_timer <= 0:
                self.zombie_attack()
                self.zombie_attack_timer = 60  # Reset timer
                
        # Check wave completion
        if self.zombies_killed_this_wave >= self.zombies_in_wave and not self.current_zombie:
            self.complete_wave()
            
    def update_visuals(self):
        # Update canvas animations
        self.canvas.delete("all")
        
        # Draw background
        self.canvas.create_rectangle(0, 0, 800, 400, fill='#0a0a0a', outline='')
        
        # Draw ground
        self.canvas.create_rectangle(0, 350, 800, 400, fill='#2d2d2d', outline='')
        
        # Draw player
        player_x = 100
        player_y = 300
        if self.screen_shake > 0:
            player_x += random.randint(-3, 3)
            player_y += random.randint(-3, 3)
            self.screen_shake -= 1
            
        self.canvas.create_oval(player_x-20, player_y-20, player_x+20, player_y+20, 
                               fill='#4CAF50', outline='white', width=2)
        self.canvas.create_text(player_x, player_y, text="🎯", font=("Arial", 16))
        
        # Draw current zombie
        if self.current_zombie:
            zombie_x = 600
            zombie_y = 300
            
            # Zombie health bar
            bar_width = 80
            bar_height = 8
            health_percent = self.current_zombie['health'] / self.current_zombie['max_health']
            
            self.canvas.create_rectangle(zombie_x-40, zombie_y-40, zombie_x+40, zombie_y-30, 
                                       fill='#333333', outline='white')
            self.canvas.create_rectangle(zombie_x-40, zombie_y-40, 
                                       zombie_x-40 + (bar_width * health_percent), zombie_y-30,
                                       fill='#ff4444', outline='')
            
            # Zombie sprite
            zombie_color = self.get_zombie_color(self.current_zombie['name'])
            self.canvas.create_oval(zombie_x-25, zombie_y-25, zombie_x+25, zombie_y+25, 
                                   fill=zombie_color, outline='#666666', width=2)
            self.canvas.create_text(zombie_x, zombie_y, text="🧟", font=("Arial", 20))
            
            # Zombie info
            self.canvas.create_text(zombie_x, zombie_y+40, 
                                   text=f"{self.current_zombie['name']}", 
                                   font=("Arial", 12, "bold"), fill='white')
            
        # Draw muzzle flash
        if self.muzzle_flash:
            self.canvas.create_oval(120, 290, 140, 310, fill='yellow', outline='orange', width=3)
            self.muzzle_flash = False
            
        # Draw blood splatter
        for splatter in self.blood_splatter[:]:
            splatter['life'] -= 1
            if splatter['life'] <= 0:
                self.blood_splatter.remove(splatter)
            else:
                self.canvas.create_oval(splatter['x']-5, splatter['y']-5, 
                                       splatter['x']+5, splatter['y']+5, 
                                       fill='red', outline='')
                
    def get_zombie_color(self, zombie_type):
        colors = {
            'Crawler': '#8B4513',
            'Walker': '#696969',
            'Runner': '#FF6347',
            'Brute': '#8B0000',
            'Spitter': '#9ACD32',
            'Screamer': '#FF69B4'
        }
        return colors.get(zombie_type, '#666666')
        
    def start_wave(self):
        self.zombies_in_wave = self.wave_number * 3 + random.randint(1, 3)
        self.zombies_killed_this_wave = 0
        self.display_message(f"🌊 WAVE {self.wave_number} BEGINS!")
        self.display_message(f"🧟 {self.zombies_in_wave} zombies incoming!")
        self.spawn_zombie()
        
    def complete_wave(self):
        self.wave_number += 1
        bonus_xp = self.wave_number * 50
        self.experience += bonus_xp
        self.display_message(f"🎉 WAVE {self.wave_number - 1} COMPLETE!")
        self.display_message(f"💰 Bonus XP: {bonus_xp}")
        
        # Give rewards
        self.health_kits += 1
        self.ammo_clips += 2
        if self.wave_number % 3 == 0:
            self.grenades += 1
            
        self.check_level_up()
        self.update_inventory_display()
        
        # Start next wave after delay
        self.root.after(3000, self.start_wave)
        
    def spawn_zombie(self):
        if self.game_over or self.current_zombie:
            return
            
        # More zombie types with wave scaling
        zombie_types = [
            {"name": "Crawler", "health": 15 + self.wave_number * 5, "damage": 8 + self.wave_number, "speed": 2},
            {"name": "Walker", "health": 25 + self.wave_number * 8, "damage": 12 + self.wave_number * 2, "speed": 3},
            {"name": "Runner", "health": 20 + self.wave_number * 6, "damage": 10 + self.wave_number, "speed": 5},
            {"name": "Brute", "health": 40 + self.wave_number * 15, "damage": 20 + self.wave_number * 3, "speed": 1},
            {"name": "Spitter", "health": 18 + self.wave_number * 7, "damage": 15 + self.wave_number * 2, "speed": 3},
            {"name": "Screamer", "health": 12 + self.wave_number * 4, "damage": 6 + self.wave_number, "speed": 4}
        ]
        
        # Higher wave numbers unlock stronger zombies
        available_zombies = zombie_types[:min(len(zombie_types), 2 + self.wave_number // 3)]
        
        self.current_zombie = random.choice(available_zombies).copy()
        self.current_zombie['max_health'] = self.current_zombie['health']
        self.zombie_attack_timer = 60
        
        self.display_message(f"🧟 A {self.current_zombie['name']} appears!")
        self.update_zombie_info()
        
    def update_zombie_info(self):
        if self.current_zombie:
            info = f"{self.current_zombie['name']}\n"
            info += f"HP: {self.current_zombie['health']}/{self.current_zombie['max_health']}\n"
            info += f"DMG: {self.current_zombie['damage']}\n"
            info += f"SPD: {self.current_zombie['speed']}"
            self.zombie_info_label.config(text=info)
        else:
            self.zombie_info_label.config(text="No zombie present")
            
    def process_command(self, event=None):
        command = self.command_entry.get().lower().strip()
        self.command_entry.delete(0, tk.END)
        
        if command and not self.game_over and not self.game_paused:
            self.execute_command(command)
            
    def execute_command(self, command):
        commands = {
            'shoot': self.shoot_zombie,
            's': self.shoot_zombie,
            'reload': self.reload_weapon,
            'r': self.reload_weapon,
            'heal': self.heal_player,
            'h': self.heal_player,
            'grenade': self.throw_grenade,
            'g': self.throw_grenade,
            'run': self.run_away,
            'escape': self.run_away,
            'stats': self.show_stats,
            'inventory': self.show_inventory,
            'help': self.show_help
        }
        
        if command in commands:
            commands[command]()
        else:
            self.display_message("❌ Unknown command! Type 'help' for commands.")
            
    def shoot_zombie(self):
        if self.is_reloading:
            self.display_message("🔄 Still reloading...")
            return
            
        if self.player_ammo <= 0:
            self.display_message("🔫 No ammo! Need to reload!")
            return
            
        if not self.current_zombie:
            self.display_message("🎯 No target!")
            return
            
        self.player_ammo -= 1
        self.muzzle_flash = True
        self.screen_shake = 5
        
        # Calculate hit and damage
        hit_chance = 75 + (self.level * 2)  # Improve with level
        critical_hit = random.randint(1, 100) <= self.critical_chance
        
        if random.randint(1, 100) <= hit_chance:
            damage = self.weapon_damage + random.randint(-5, 5)
            if critical_hit:
                damage *= 2
                self.display_message(f"💥 CRITICAL HIT! {damage} damage!")
            else:
                self.display_message(f"🎯 HIT! {damage} damage!")
                
            self.current_zombie['health'] -= damage
            
            # Add blood splatter
            self.blood_splatter.append({
                'x': 600 + random.randint(-20, 20),
                'y': 300 + random.randint(-20, 20),
                'life': 30
            })
            
            if self.current_zombie['health'] <= 0:
                self.kill_zombie()
        else:
            self.display_message("❌ MISS!")
            
        self.update_stats()
        self.update_zombie_info()
        
    def kill_zombie(self):
        zombie_name = self.current_zombie['name']
        xp_gained = self.current_zombie['max_health'] // 2
        
        self.display_message(f"💀 {zombie_name} eliminated! +{xp_gained} XP")
        self.zombies_killed += 1
        self.zombies_killed_this_wave += 1
        self.experience += xp_gained
        
        # Chance for loot
        if random.randint(1, 100) <= 40:
            self.find_loot()
            
        self.current_zombie = None
        self.check_level_up()
        
        # Spawn next zombie if wave not complete
        if self.zombies_killed_this_wave < self.zombies_in_wave:
            self.root.after(2000, self.spawn_zombie)
            
    def find_loot(self):
        loot_types = ['health', 'ammo', 'grenade', 'armor']
        loot = random.choice(loot_types)
        
        if loot == 'health':
            self.health_kits += 1
            self.display_message("🎁 Found health kit!")
        elif loot == 'ammo':
            self.ammo_clips += 1
            self.display_message("🎁 Found ammo clip!")
        elif loot == 'grenade':
            self.grenades += 1
            self.display_message("🎁 Found grenade!")
        elif loot == 'armor':
            self.armor += 10
            self.display_message("🎁 Found armor plating!")
            
        self.update_inventory_display()
        
    def check_level_up(self):
        xp_needed = self.level * 100
        if self.experience >= xp_needed:
            self.level += 1
            self.experience -= xp_needed
            self.weapon_damage += 5
            self.critical_chance += 2
            self.player_max_health += 10
            self.player_health = min(self.player_max_health, self.player_health + 20)
            
            self.display_message(f"⭐ LEVEL UP! Now level {self.level}!")
            self.display_message(f"💪 Damage increased to {self.weapon_damage}!")
            
    def reload_weapon(self):
        if self.ammo_clips <= 0:
            self.display_message("📦 No ammo clips!")
            return
            
        if self.player_ammo >= self.player_max_ammo:
            self.display_message("🔫 Already fully loaded!")
            return
            
        if self.is_reloading:
            self.display_message("🔄 Already reloading!")
            return
            
        self.ammo_clips -= 1
        self.is_reloading = True
        self.reload_time = 60  # 3 seconds at 20 FPS
        self.player_ammo = self.player_max_ammo
        self.display_message("🔄 Reloading...")
        
    def heal_player(self):
        if self.health_kits <= 0:
            self.display_message("💊 No health kits!")
            return
            
        if self.player_health >= self.player_max_health:
            self.display_message("❤️ Already at full health!")
            return
            
        self.health_kits -= 1
        heal_amount = random.randint(40, 60)
        self.player_health = min(self.player_max_health, self.player_health + heal_amount)
        self.display_message(f"💊 Healed {heal_amount} HP!")
        
    def throw_grenade(self):
        if self.grenades <= 0:
            self.display_message("💣 No grenades!")
            return
            
        if not self.current_zombie:
            self.display_message("🎯 No target!")
            return
            
        self.grenades -= 1
        damage = random.randint(80, 120)
        self.screen_shake = 10
        
        self.display_message(f"💥 GRENADE! {damage} damage!")
        self.current_zombie['health'] -= damage
        
        # More blood splatter for grenade
        for _ in range(5):
            self.blood_splatter.append({
                'x': 600 + random.randint(-30, 30),
                'y': 300 + random.randint(-30, 30),
                'life': 40
            })
            
        if self.current_zombie['health'] <= 0:
            self.kill_zombie()
            
        self.update_zombie_info()
        
    def run_away(self):
        if not self.current_zombie:
            self.display_message("🏃 Nothing to run from!")
            return
            
        escape_chance = 70 - (self.current_zombie['speed'] * 5)
        if random.randint(1, 100) <= escape_chance:
            self.display_message("🏃 Escaped successfully!")
            self.current_zombie = None
            self.root.after(4000, self.spawn_zombie)
        else:
            self.display_message("😱 Failed to escape!")
            self.zombie_attack()
            
    def zombie_attack(self):
        if not self.current_zombie:
            return
            
        base_damage = self.current_zombie['damage']
        damage = random.randint(base_damage - 3, base_damage + 3)
        
        # Armor reduces damage
        if self.armor > 0:
            armor_block = min(self.armor, damage // 2)
            damage -= armor_block
            self.armor -= armor_block
            self.display_message(f"🛡️ Armor blocked {armor_block} damage!")
            
        self.player_health -= damage
        self.screen_shake = 8
        
        self.display_message(f"🩸 {self.current_zombie['name']} attacks for {damage} damage!")
        
        if self.player_health <= 0:
            self.game_over = True
            self.display_message("💀 GAME OVER!")
            self.display_message(f"🏆 Final Score: Wave {self.wave_number}, {self.zombies_killed} kills")
            messagebox.showinfo("Game Over", f"You survived to wave {self.wave_number} with {self.zombies_killed} kills!")
            
        self.update_stats()
        self.update_inventory_display()
        
    def toggle_pause(self):
        self.game_paused = not self.game_paused
        if self.game_paused:
            self.display_message("⏸️ GAME PAUSED")
        else:
            self.display_message("▶️ GAME RESUMED")
            
    def show_stats(self):
        stats = f"""
📊 DETAILED STATISTICS:
❤️ Health: {self.player_health}/{self.player_max_health}
🔫 Ammo: {self.player_ammo}/{self.player_max_ammo}
🌊 Wave: {self.wave_number}
💀 Kills: {self.zombies_killed}
⭐ Level: {self.level}
💰 Experience: {self.experience}
💪 Weapon Damage: {self.weapon_damage}
🎯 Critical Chance: {self.critical_chance}%
🛡️ Armor: {self.armor}
        """
        self.display_message(stats)
        
    def show_inventory(self):
        inv = f"""
🎒 INVENTORY:
💊 Health Kits: {self.health_kits}
📦 Ammo Clips: {self.ammo_clips}
💣 Grenades: {self.grenades}
🛡️ Armor Points: {self.armor}
        """
        self.display_message(inv)
        
    def show_help(self):
        help_text = """
🎮 CONTROLS & COMMANDS:
🔫 shoot/s - Fire your weapon (SPACE)
🔄 reload/r - Reload weapon (R key)
💊 heal/h - Use health kit (H key)
💣 grenade/g - Throw grenade (G key)
🏃 run/escape - Try to escape (ESC key)
⏸️ pause - Pause game (P key)
📊 stats - Show detailed stats
🎒 inventory - Show inventory
❓ help - Show this help

🎯 GAMEPLAY TIPS:
• Use grenades on tough zombies like Brutes
• Armor reduces incoming damage
• Level up to increase damage and crit chance
• Each wave gets progressively harder
• Find loot by killing zombies
• Watch your ammo - reload strategically!
        """
        self.display_message(help_text)
        
    def update_stats(self):
        # Update health bar
        health_percent = (self.player_health / self.player_max_health) * 100
        self.health_bar['value'] = health_percent
        
        # Update labels with color coding
        self.health_label.config(text=f"{self.player_health}/{self.player_max_health}")
        if self.player_health < 30:
            self.health_label.config(fg=self.colors['danger'])
        elif self.player_health < 60:
            self.health_label.config(fg=self.colors['warning'])
        else:
            self.health_label.config(fg=self.colors['health'])
            
        self.ammo_label.config(text=f"{self.player_ammo}/{self.player_max_ammo}")
        if self.player_ammo < 5:
            self.ammo_label.config(fg=self.colors['danger'])
        else:
            self.ammo_label.config(fg=self.colors['ammo'])
            
        self.wave_label.config(text=str(self.wave_number))
        self.kills_label.config(text=str(self.zombies_killed))
        self.level_label.config(text=str(self.level))
        
    def update_inventory_display(self):
        # Clear existing inventory display
        for widget in self.inventory_frame.winfo_children():
            widget.destroy()
            
        # Create new inventory display
        items = [
            (f"💊 Health Kits: {self.health_kits}", self.colors['health']),
            (f"📦 Ammo Clips: {self.ammo_clips}", self.colors['ammo']),
            (f"💣 Grenades: {self.grenades}", self.colors['warning']),
            (f"🛡️ Armor: {self.armor}", self.colors['text'])
        ]
        
        for item_text, color in items:
            tk.Label(self.inventory_frame, text=item_text, 
                    font=("Arial", 10), fg=color, bg=self.colors['panel']).pack(anchor=tk.W)
            
    def display_message(self, message):
        self.game_text.config(state=tk.NORMAL)
        self.game_text.insert(tk.END, message + "\n")
        self.game_text.see(tk.END)
        self.game_text.config(state=tk.DISABLED)
        
        # Add color coding for different message types
        if "CRITICAL" in message:
            self.game_text.tag_add("critical", "end-2l", "end-1l")
            self.game_text.tag_config("critical", foreground="#ff6b6b")
        elif "LEVEL UP" in message:
            self.game_text.tag_add("levelup", "end-2l", "end-1l")
            self.game_text.tag_config("levelup", foreground="#51cf66")
        elif "WAVE" in message:
            self.game_text.tag_add("wave", "end-2l", "end-1l")
            self.game_text.tag_config("wave", foreground="#ffd43b")

def main():
    root = tk.Tk()
    game = ZombieSurvivalGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()