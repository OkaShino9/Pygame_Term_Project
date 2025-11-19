import pygame, sys, random, time, math
from transitions import curtain_transition
from board_generator import generate_space_board_assets

# --- CONFIGURATION ---
SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
BOARD_POS = (80, 80)
CLASSIC_BOARD_SIZE = (600, 600)
SPACE_BOARD_SIZE = (640, 640)
DICE_POS = (990, 250)
TURN_TEXT_POS = (950, 500)
FONT_COLOR = (255, 255, 255)

# --- UTILITY FUNCTIONS ---
def load_image(path, size=None):
    """Loads an image, converts it for performance, and optionally rescales it."""
    img = pygame.image.load(path).convert_alpha()
    if size:
        img = pygame.transform.smoothscale(img, size)
    return img

# --- PLAYER CLASS ---
class Player:
    """Represents a player in the game, handling their position, movement, and appearance."""
    def __init__(self, image_path, start_pos):
        self.image = load_image(image_path, (80, 80))
        self.pos = 1  # Current tile number (1-100).
        self.rect = self.image.get_rect(center=start_pos)
        self.move_path = []  # A list of screen coordinates to follow.
        self.is_moving = False
        self.move_speed = 10 # Pixels per frame.

    def draw(self, screen):
        """Draws the player's avatar on the screen."""
        screen.blit(self.image, self.rect)

    def move_along_path(self, path):
        """Sets the movement path for the player to follow."""
        self.move_path = path
        if path:
            self.is_moving = True

    def update(self):
        """Updates the player's position if they are currently moving."""
        if not self.is_moving:
            return

        if not self.move_path:
            self.is_moving = False
            return

        # Move towards the next point in the path.
        target_pos = self.move_path[0]
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist < self.move_speed:
            # Snap to the target if close enough.
            self.rect.center = target_pos
            self.move_path.pop(0)
        else:
            # Move at a constant speed.
            self.rect.centerx += (dx / dist) * self.move_speed
            self.rect.centery += (dy / dist) * self.move_speed

# --- GAME CLASS ---
class SnakeLaddersGame:
    """Manages the main game logic, state, and rendering for Snakes and Ladders."""
    def __init__(self, screen, players, mode="classic"):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Pixeltype', 48)
        self.mode_font = pygame.font.SysFont('Pixeltype', 32)
        self.bg = load_image("assets/bg/bg_play.png", (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.board_size = CLASSIC_BOARD_SIZE
        self.board = load_image("assets/board/Board_with_number.png", self.board_size)
        self.mode = mode

        # Dice assets
        self.dice_imgs = []
        self.current_dice = None

        # Game state
        self.tiles = self.generate_tiles(10, 10, BOARD_POS, self.board_size)
        self.players = [Player(p["avatar"], self.tiles[1]) for p in players]
        self.current_turn = 0
        self.dice_rolling = False
        self.player_moving = False
        self.roll_time = 0
        self.roll_value = 1
        self.after_move_check = False # Flag to check for snakes/ladders after a move.
        self.game_over = False
        self.winner = None

        # Classic board snakes and ladders
        self.ladders = { 17: 36, 35: 67, 40: 42, 58: 76, 59: 80, 71: 89 }
        self.snakes  = { 31: 14, 48: 28, 56: 22, 73: 21, 82: 42, 92: 75, 98: 66 }

        # Configure board and assets based on game mode.
        self._configure_layouts()
        if not self.dice_imgs:
            self.dice_imgs = self._load_dice_images()
        self.current_dice = self.dice_imgs[0]
        self.board_rect = self.board.get_rect(topleft=BOARD_POS)

        # UI Elements
        self.back_button_img = load_image("assets/button/back.png", (100, 75))
        self.back_button_rect = self.back_button_img.get_rect(topleft=(20, 5))

        # Sound Effects
        self.dice_sound = None
        try:
            self.dice_sound = pygame.mixer.Sound("assets/audio/shuffle.mp3")
            self.dice_sound.set_volume(0.7)
        except pygame.error:
            self.dice_sound = None

        self.win_sound = None
        try:
            self.win_sound = pygame.mixer.Sound("assets/audio/winner.mp3")
            self.win_sound.set_volume(0.8)
        except pygame.error:
            self.win_sound = None

    def _configure_layouts(self):
        """Prepares board assets and layout based on the selected game mode."""
        if self.mode != "special":
            # Use the standard classic board.
            self.board_size = CLASSIC_BOARD_SIZE
            self.board = load_image("assets/board/Board_with_number.png", self.board_size)
            self.tiles = self.generate_tiles(10, 10, BOARD_POS, self.board_size)
            for player in self.players:
                player.rect.center = self.tiles[player.pos]
            self.dice_imgs = self._load_dice_images()
            return

        # For "special" mode, generate a new board layout.
        self.board_size = SPACE_BOARD_SIZE
        try:
            board_surface, snakes_map, ladders_map, grid_map = generate_space_board_assets()
            src_size = board_surface.get_size()
            self.board = pygame.transform.smoothscale(board_surface, self.board_size)
            if snakes_map: self.snakes = snakes_map
            if ladders_map: self.ladders = ladders_map
            if grid_map:
                self.tiles = self._tiles_from_generator(grid_map, src_size)
            else: # Fallback if grid map is missing
                self.tiles = self.generate_tiles(10, 10, BOARD_POS, self.board_size)
            for player in self.players:
                player.rect.center = self.tiles[player.pos]
        except Exception:
            # Fallback to the default classic board if generation fails.
            self.board_size = CLASSIC_BOARD_SIZE
            self.board = load_image("assets/board/Board_with_number.png", self.board_size)
            self.tiles = self.generate_tiles(10, 10, BOARD_POS, self.board_size)
            for player in self.players:
                player.rect.center = self.tiles[player.pos]
        self.dice_imgs = self._load_dice_images()

    def _tiles_from_generator(self, grid_map, source_size):
        """Converts grid coordinates from the generator into screen tile centers."""
        src_w, src_h = source_size
        scale_x = self.board_size[0] / src_w
        scale_y = self.board_size[1] / src_h
        tiles = {}
        for cell, (x, y) in grid_map.items():
            tiles[cell] = (BOARD_POS[0] + x * scale_x, BOARD_POS[1] + y * scale_y)
        return tiles

    def regenerate_snakes_and_ladders(self):
        """In 'special' mode, regenerates the board layout for a new game."""
        if self.mode != "special":
            return
        try:
            board_surface, snakes_map, ladders_map, grid_map = generate_space_board_assets()
            src_size = board_surface.get_size()
            self.board = pygame.transform.smoothscale(board_surface, self.board_size)
            if snakes_map: self.snakes = snakes_map
            if ladders_map: self.ladders = ladders_map
            if grid_map: self.tiles = self._tiles_from_generator(grid_map, src_size)
        except Exception:
            # Fallback to default if generation fails.
            self.board_size = CLASSIC_BOARD_SIZE
            self.board = load_image("assets/board/Board_with_number.png", self.board_size)
            self.tiles = self.generate_tiles(10, 10, BOARD_POS, self.board_size)
            self.snakes  = { 31: 14, 48: 28, 56: 22, 73: 21, 82: 42, 92: 75, 98: 66 }
            self.ladders = { 17: 36, 35: 67, 40: 42, 58: 76, 59: 80, 71: 89 }

    def _load_dice_images(self):
        """Loads the isometric dice images used for the rolling animation."""
        return [load_image(f"assets/Dice/Isometric/dice_{i}_iso.png", (150, 150)) for i in range(1, 7)]

    def generate_tiles(self, cols, rows, start, size):
        """Generates a dictionary of tile centers (1-100) for a standard board layout."""
        tiles = {}
        w, h = size[0] // cols, size[1] // rows
        x0, y0 = start
        num = 1
        for row in range(rows):
            # Y-coordinate is flipped to match board layout (1 at bottom-left).
            y = y0 + size[1] - h * (row + 0.5) - 25
            # Alternate row direction to create the serpentine path.
            row_indices = range(cols) if row % 2 == 0 else range(cols - 1, -1, -1)
            for col in row_indices:
                x = x0 + w * (col + 0.5)
                tiles[num] = (x, y)
                num += 1
        return tiles

    def roll_dice(self):
        """Initiates the dice roll sequence."""
        self.regenerate_snakes_and_ladders() # Regenerate board in special mode.
        self.dice_rolling = True
        self.roll_time = time.time()
        self.roll_value = random.randint(1, 6)
        if self.dice_sound:
            self.dice_sound.stop()
            self.dice_sound.play()

    def update(self):
        """Main game state update logic, called every frame."""
        if self.game_over:
            return
            
        # Update all player animations.
        for p in self.players:
            p.update()

        # Handle the dice rolling animation.
        if self.dice_rolling:
            current_time = time.time()
            if current_time - self.roll_time > 1:  # Animation duration of 1 second.
                self.dice_rolling = False
                self.current_dice = self.dice_imgs[self.roll_value - 1]

                player = self.players[self.current_turn]
                path = []
                start_pos = player.pos
                potential_pos = player.pos + self.roll_value

                # Handle board wrap-around (overshooting 100).
                if potential_pos > 100:
                    overshoot = potential_pos - 100
                    end_pos = 100 - overshoot
                    # Create path to 100 and then back.
                    path.extend(self.tiles[i] for i in range(start_pos + 1, 101))
                    path.extend(self.tiles[i] for i in range(99, end_pos - 1, -1))
                else:
                    end_pos = potential_pos
                    # Create a simple forward path.
                    path.extend(self.tiles[i] for i in range(start_pos + 1, end_pos + 1))

                player.pos = end_pos
                player.move_along_path(path)
                self.player_moving = True
                self.after_move_check = True # Flag to check for snakes/ladders after move.
            else:
                # Show a random dice face for the rolling effect.
                if current_time - getattr(self, 'last_dice_frame', 0) > 0.05:
                    self.last_dice_frame = current_time
                    self.current_dice = random.choice(self.dice_imgs)

        # Handle post-movement logic.
        elif self.player_moving:
            player = self.players[self.current_turn]
            if not player.is_moving:
                if self.after_move_check:
                    self.after_move_check = False # Consume the flag.
                    
                    # Check for win condition.
                    if player.pos == 100:
                        self.game_over = True
                        self.winner = self.current_turn
                        if self.win_sound: self.win_sound.play()
                        return

                    # Check for ladders and snakes.
                    if player.pos in self.ladders:
                        new_pos = self.ladders[player.pos]
                        player.move_along_path([self.tiles[new_pos]])
                        player.pos = new_pos
                        return # Keep the turn until the final position is reached.
                    elif player.pos in self.snakes:
                        new_pos = self.snakes[player.pos]
                        player.move_along_path([self.tiles[new_pos]])
                        player.pos = new_pos
                        return # Keep the turn.

                # If no snake/ladder, end the turn.
                self.player_moving = False
                self.current_turn = (self.current_turn + 1) % len(self.players)

    def draw(self):
        """Draws all game elements to the screen."""
        self.screen.blit(self.bg, (0, 0))
        self.screen.blit(self.board, self.board_rect)
        
        # Display game mode.
        mode_text = "Mode: Special" if self.mode == "special" else "Mode: Classic"
        mode_label = self.mode_font.render(mode_text, True, FONT_COLOR)
        self.screen.blit(mode_label, (BOARD_POS[0] + 45, BOARD_POS[1] - 45))

        # Draw the dice.
        self.screen.blit(self.current_dice, self.current_dice.get_rect(center=DICE_POS))

        # Draw all players.
        for p in self.players:
            p.draw(self.screen)

        # --- Turn Indicator Panel ---
        panel_rect = pygame.Rect(825, 450, 450, 200)
        
        # Display all player avatars in the panel.
        num_players = len(self.players)
        max_panel_width = 440 # Panel padding.
        spacing = 10
        avatar_size = (max_panel_width - (num_players - 1) * spacing) / num_players if num_players > 0 else 0
        avatar_size = int(min(avatar_size, 150)) # Cap avatar size.

        total_width = num_players * avatar_size + (num_players - 1) * spacing
        start_x = panel_rect.centerx - total_width / 2

        for i, player in enumerate(self.players):
            avatar_scaled = pygame.transform.scale(player.image, (avatar_size, avatar_size))
            
            # Dim the avatars of players whose turn it is not.
            if i != self.current_turn:
                avatar_scaled.set_alpha(100)

            avatar_x = start_x + i * (avatar_size + spacing)
            avatar_rect = avatar_scaled.get_rect(center=(avatar_x, panel_rect.centery - 20))
            self.screen.blit(avatar_scaled, avatar_rect)

        # Display "Player X's Turn" text.
        turn_text = self.font.render(f"Player {self.current_turn + 1}'s Turn", True, FONT_COLOR)
        text_rect = turn_text.get_rect(center=(panel_rect.left + 170, panel_rect.bottom - 220))
        self.screen.blit(turn_text, text_rect)

        # Display winner text if the game is over.
        if self.game_over:
            win_font = pygame.font.SysFont('Pixeltype', 100)
            win_text = win_font.render(f"Player {self.winner + 1} Wins!", True, (255, 215, 0))
            win_rect = win_text.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2))
            self.screen.blit(win_text, win_rect)
        
        self.screen.blit(self.back_button_img, self.back_button_rect)

    def handle_event(self, event):
        """Handles user input events."""
        if self.game_over:
            return None

        if event.type == pygame.MOUSEBUTTONDOWN:
            dice_rect = self.current_dice.get_rect(center=DICE_POS)
            # Allow dice roll only if it's the player's turn and no animations are active.
            if dice_rect.collidepoint(event.pos) and not self.dice_rolling and not self.player_moving:
                self.roll_dice()
            
            if self.back_button_rect.collidepoint(event.pos):
                return "back"
        return None

    def run(self):
        """The main game loop."""
        running = True
        return_value = None
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                action = self.handle_event(event)
                if action == "back":
                    return_value = "back"
                    running = False
            
            if not running:
                break

            self.update()
            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

            # After the game ends, show winner screen and transition out.
            if self.game_over:
                pygame.time.wait(1000)  # Show winner text for 1 second.
                game_over_snapshot = self.screen.copy()
                black_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                black_surface.fill((0,0,0))
                curtain_transition(self.screen, game_over_snapshot, black_surface, "assets/bg/transitions.png")
                running = False
        return return_value

# --- ENTRY POINT ---
def run_game(screen, player_infos, mode="classic"):
    """Initializes and runs the Snake & Ladders game session."""
    pygame.display.set_caption("ComSci Snakes & Ladders")
    game = SnakeLaddersGame(screen, player_infos, mode=mode)
    return game.run()


