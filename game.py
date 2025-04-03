import pygame
import random
import json

# Initialize pygame
pygame.init()

# Load sound files
bounce_sound = pygame.mixer.Sound("bounce.wav")  # Sound when the ball hits the paddle or brick
pygame.mixer.music.load("background_music.mp3")  # Background music
game_over_sound = pygame.mixer.Sound("game_over.wav")  # Game over sound

# Timer setup
timer = pygame.time.Clock()
fps = 60
white = (255, 255, 255)
black = (0, 0, 0)
gray = (128, 128, 128)
red = (255, 0, 0)
orange = (255, 128, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
purple = (255, 0, 255)
player_speed = 8
WIDTH = 500
HEIGHT = 900
player_x = 190
player_direction = 0
ball_x = WIDTH / 2
ball_y = HEIGHT - 30
ball_x_direction = 0
ball_y_direction = 0
ball_x_speed = 5
ball_y_speed = 5
board = []
create_new = True
colors = [red, orange, green, blue, purple]
screen = pygame.display.set_mode([WIDTH, HEIGHT])
active = False
score = 0
points = 0  # Points for the shop
unlocked_themes = ["classic"]  # Default unlocked theme
high_score = 0  # High score

# Load saved data
try:
    with open("save.json", "r") as file:
        data = json.load(file)
        points = data["points"]
        unlocked_themes = data["unlocked_themes"]
        high_score = data["high_score"]
except FileNotFoundError:
    pass

font = pygame.font.Font('freesansbold.ttf', 30)

# Start the background music in a loop
pygame.mixer.music.play(-1, 0.0)

# Variables to track the game state
game_state = "start"  # Can be "start", "settings", "game", "gameover", "shop"
volume_level = 0.5  # Default volume level
theme = "classic"  # Default theme

# Set initial volume levels
pygame.mixer.music.set_volume(volume_level)
bounce_sound.set_volume(volume_level)
game_over_sound.set_volume(volume_level)

# Define themes
themes = {
    "classic": {
        "background": gray,
        "paddle": black,
        "ball": white,
        "bricks": [red, orange, green, blue, purple],
        "text_color": white,
    },
    "dark": {
        "background": (30, 30, 30),
        "paddle": (50, 50, 50),
        "ball": (200, 200, 200),
        "bricks": [(100, 100, 100), (150, 150, 150), (200, 200, 200), (250, 250, 250), (0, 255, 255)],
        "text_color": white,
    },
    "neon": {
        "background": (0, 0, 0),
        "paddle": (0, 255, 255),
        "ball": (255, 0, 255),
        "bricks": [(255, 0, 255), (0, 255, 255), (255, 255, 0), (0, 255, 0), (255, 0, 0)],
        "text_color": (255, 255, 255),
    },
}

# Apply current theme colors
current_theme = themes[theme]

# Define power-ups with their costs and effects
powerups = {
    "Extra Life": {"cost": 100, "effect": "extra_life"},
    "Speed Boost": {"cost": 150, "effect": "speed_boost"},
    "Ball Split": {"cost": 200, "effect": "ball_split"},
}

# List to track purchased power-ups
purchased_powerups = []

# List of motivational messages
motivational_messages = [
    "Great effort! Try again!",
    "You can do it! Keep practicing!",
    "Don't give up! Every attempt makes you better!",
    "You're doing amazing! Just keep trying!",
    "Remember, practice makes perfect!",
]

def create_new_board():
    board = []
    rows = random.randint(4, 8)
    for i in range(rows):
        row = []
        for j in range(5):
            row.append(random.randint(1, 5))
        board.append(row)
    return board

def draw_board(board):
    board_squares = []
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] > 0:
                piece = pygame.draw.rect(screen, current_theme["bricks"][(board[i][j]) - 1], [j * 100, i * 40, 98, 38], 0, 5)
                pygame.draw.rect(screen, black, [j * 100, i * 40, 98, 38], 5, 5)
                top = pygame.rect.Rect((j * 100, i * 40), (98, 1))
                bot = pygame.rect.Rect((j * 100, (i * 40) + 37), (98, 1))
                left = pygame.rect.Rect((j * 100, i * 40), (37, 1))
                right = pygame.rect.Rect(((j * 100) + 97, i * 40), (37, 1))
                board_squares.append([top, bot, left, right, (i, j)])
    return board_squares

# Start screen function
def show_start_screen():
    screen.fill(current_theme["background"])
    title_text = font.render('Welcome to Breakout', True, current_theme["text_color"])
    start_text = font.render('Press 1 to Start Game', True, current_theme["text_color"])
    settings_text = font.render('Press 2 for Settings', True, current_theme["text_color"])
    shop_text = font.render('Press 3 for Shop', True, current_theme["text_color"])
    
    screen.blit(title_text, (120, 200))
    screen.blit(start_text, (140, 300))
    screen.blit(settings_text, (140, 350))
    screen.blit(shop_text, (140, 400))
    
    pygame.display.flip()

# Settings screen function with volume control
def show_settings_screen():
    screen.fill(current_theme["background"])
    settings_text = font.render('Settings', True, current_theme["text_color"])
    back_text = font.render('Press B to go back', True, current_theme["text_color"])
    
    # Volume control buttons (Increase and Decrease)
    decrease_button = pygame.draw.rect(screen, red, [150, 300, 50, 30])  # Decrease button
    increase_button = pygame.draw.rect(screen, green, [300, 300, 50, 30])  # Increase button
    
    # Draw the buttons' text
    decrease_text = font.render('-', True, white)
    increase_text = font.render('+', True, white)
    
    screen.blit(decrease_text, (160, 305))
    screen.blit(increase_text, (310, 305))
    
    # Display the volume level
    volume_text = font.render(f'Volume: {int(volume_level * 100)}%', True, current_theme["text_color"])
    screen.blit(volume_text, (200, 350))

    screen.blit(settings_text, (180, 200))
    screen.blit(back_text, (140, 450))
    
    pygame.display.flip()

# Game over screen function
def show_game_over_screen():
    screen.fill(current_theme["background"])
    game_over_text = font.render('Game Over', True, current_theme["text_color"])
    score_text = font.render(f'Final Score: {score}', True, current_theme["text_color"])
    motivational_text = random.choice(motivational_messages)  # Select a random motivational message
    motivational_surface = font.render(motivational_text, True, green)  # Set color to green
    
    restart_text = font.render('Press R to Restart', True, current_theme["text_color"])
    main_screen_text = font.render('Press M for Main Screen', True, current_theme["text_color"])
    quit_text = font.render('Press Q to Quit', True, current_theme["text_color"])
    
    screen.blit(game_over_text, (170, 300))
    screen.blit(score_text, (160, 350))
    screen.blit(motivational_surface, (5, 700))  # Display the motivational message at the bottom
    screen.blit(restart_text, (140, 450))
    screen.blit(main_screen_text, (80, 500))
    screen.blit(quit_text, (140, 550))
    
    pygame.display.flip()

# Shop screen function
def show_shop_screen():
    screen.fill(current_theme["background"])
    shop_text = font.render('Shop', True, current_theme["text_color"])
    points_text = font.render(f'Points: {points}', True, current_theme["text_color"])
    back_text = font.render('Press B to go back', True, current_theme["text_color"])
    
    # Theme purchase options
    classic_button = pygame.draw.rect(screen, (255, 255, 255), [150, 200, 250, 60])  # Classic button
    dark_button = pygame.draw.rect(screen, (50, 50, 50), [150, 270, 250, 60])  # Dark button
    neon_button = pygame.draw.rect(screen, (0, 255, 255), [150, 340, 250, 60])  # Neon button
    
    classic_text = font.render('Classic', True, black)  # Text color changed to black
    dark_text = font.render('Dark (100 P)', True, black)  # Text color changed to black
    neon_text = font.render('Neon (200 P)', True, black)  # Text color changed to black
    
    screen.blit(shop_text, (220, 150))
    screen.blit(points_text, (220, 100))
    screen.blit(back_text, (140, 450))
    
    screen.blit(classic_text, (160, 210))
    screen.blit(dark_text, (160, 280))
    screen.blit(neon_text, (160, 350))
    
    draw_powerup_buttons()
    
    pygame.display.flip()

def draw_powerup_buttons():
    button_width = 350  # Increased width for better text fitting
    button_height = 80  # Increased height for better text fitting
    button_y_start = 430  # Adjusted starting position for buttons
    for index, (powerup, details) in enumerate(powerups.items()):
        button_x = (WIDTH - button_width) // 2
        button_y = button_y_start + index * (button_height + 15)
        pygame.draw.rect(screen, black, (button_x, button_y, button_width, button_height))  # Draw button
        text_surface = font.render(powerup + f" - {details['cost']} P", True, white)  # Create text surface
        text_rect = text_surface.get_rect(center=(button_x + button_width // 2, button_y + button_height // 2))
        screen.blit(text_surface, text_rect)  # Draw text on button

def save_data():
    data = {
        "points": points,
        "unlocked_themes": unlocked_themes,
        "high_score": high_score
    }
    with open("save.json", "w") as file:
        json.dump(data, file)

run = True
show_start_screen()  # Show the start screen initially

while run:
    timer.tick(fps)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            run = False
        if event.type == pygame.KEYDOWN:
            if game_state == "start":
                if event.key == pygame.K_1:  # Start the game
                    game_state = "game"
                    active = True
                    ball_y_direction = -1
                    ball_x_direction = random.choice([-1, 1])
                    score = 0
                    board = create_new_board()  # Create a new board when the game starts
                elif event.key == pygame.K_2:  # Open settings
                    game_state = "settings"
                    show_settings_screen()
                elif event.key == pygame.K_3:  # Open shop
                    game_state = "shop"
                    show_shop_screen()
            elif game_state == "settings":
                if event.key == pygame.K_b:  # Go back to the main menu
                    game_state = "start"
                    show_start_screen()
            elif game_state == "shop":
                if event.key == pygame.K_b:  # Go back to the main menu
                    game_state = "start"
                    show_start_screen()
            elif game_state == "game":
                if event.key == pygame.K_RIGHT and active:
                    player_direction = 1
                if event.key == pygame.K_LEFT and active:
                    player_direction = -1
            elif game_state == "gameover":
                if event.key == pygame.K_r:  # Restart the game
                    game_state = "game"
                    active = True
                    ball_y_direction = -1
                    ball_x_direction = random.choice([-1, 1])
                    score = 0
                    board = create_new_board()  # Create a new board when the game starts
                elif event.key == pygame.K_m:  # Go back to the main screen
                    game_state = "start"
                    show_start_screen()
                elif event.key == pygame.K_q:  # Quit the game
                    save_data()
                    run = False

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                player_direction = 0
            if event.key == pygame.K_LEFT:
                player_direction = 0

        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == "settings":
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check if the decrease button is clicked
                if 150 <= mouse_x <= 200 and 300 <= mouse_y <= 330:
                    # Decrease volume (with bounds check)
                    volume_level = max(0.0, volume_level - 0.1)
                    pygame.mixer.music.set_volume(volume_level)
                    bounce_sound.set_volume(volume_level)
                    game_over_sound.set_volume(volume_level)
                    show_settings_screen()  # Redraw the settings screen to show updated volume

                # Check if the increase button is clicked
                if 300 <= mouse_x <= 350 and 300 <= mouse_y <= 330:
                    # Increase volume (with bounds check)
                    volume_level = min(1.0, volume_level + 0.1)
                    pygame.mixer.music.set_volume(volume_level)
                    bounce_sound.set_volume(volume_level)
                    game_over_sound.set_volume(volume_level)
                    show_settings_screen()  # Redraw the settings screen to show updated volume

            if game_state == "shop":
                mouse_x, mouse_y = pygame.mouse.get_pos()
                
                # Check if the dark theme button is clicked
                if 150 <= mouse_x <= 400 and 200 <= mouse_y <= 260 and "dark" not in unlocked_themes:
                    if points >= 100:
                        points -= 100
                        unlocked_themes.append("dark")
                        save_data()  # Save data after purchase
                
                # Check if the neon theme button is clicked
                if 150 <= mouse_x <= 400 and 270 <= mouse_y <= 330 and "neon" not in unlocked_themes:
                    if points >= 200:
                        points -= 200
                        unlocked_themes.append("neon")
                        save_data()  # Save data after purchase
                
                # Go back to the main menu
                if 150 <= mouse_x <= 400 and 340 <= mouse_y <= 400:
                    game_state = "start"
                    show_start_screen()

    if game_state == "game":
        screen.fill(current_theme["background"])
        squares = draw_board(board)
        player = pygame.draw.rect(screen, current_theme["paddle"], [player_x, HEIGHT - 20, 120, 15], 0, 3)
        pygame.draw.rect(screen, white, [player_x + 5, HEIGHT - 18, 110, 11], 3, 3)
        ball = pygame.draw.circle(screen, current_theme["ball"], (ball_x, ball_y), 10)
        pygame.draw.circle(screen, black, (ball_x, ball_y), 10, 3)

        if ball_x <= 10 or ball_x >= WIDTH - 10:
            bounce_sound.play()  # Play sound when ball hits the wall
            ball_x_direction *= -1

        for i in range(len(squares)):
            # top, bot, left, right, coords
            if ball.colliderect(squares[i][0]) or ball.colliderect(squares[i][1]):
                bounce_sound.play()  # Play sound when ball hits brick
                ball_y_direction *= -1
                board[squares[i][4][0]][squares[i][4][1]] -= 1
                score += 1
                points += 10  # Earn points for clearing bricks
                if score > high_score:
                    high_score = score
            if (ball.colliderect(squares[i][2]) and ball_x_direction == 1) or \
                    (ball.colliderect(squares[i][3]) and ball_x_direction == -1):
                bounce_sound.play()  # Play sound when ball hits brick
                ball_x_direction *= -1
                board[squares[i][4][0]][squares[i][4][1]] -= 1
                score += 1
                points += 10  # Earn points for clearing bricks
                if score > high_score:
                    high_score = score

        if ball.colliderect(player):
            bounce_sound.play()  # Play sound when ball hits paddle
            if player_direction == ball_x_direction:
                ball_x_speed += 1
            elif player_direction == -ball_x_direction and ball_x_speed > 1:
                ball_x_speed -= 1
            elif player_direction == -ball_x_direction and ball_x_speed == 1:
                ball_x_direction *= -1

            ball_y_direction *= -1

        ball_y += ball_y_direction * ball_y_speed
        ball_x += ball_x_direction * ball_x_speed
        player_x += player_direction * player_speed

        if ball_y <= 10:
            ball_y = 10
            ball_y_direction *= -1

        if ball_y >= HEIGHT - 10 or len(squares) == 0:
            game_state = "gameover"
            active = False
            player_x = 190
            player_direction = 0
            ball_x = WIDTH / 2
            ball_y = HEIGHT - 30
            ball_x_direction = 0
            ball_y_direction = 0
            ball_x_speed = 5
            ball_y_speed = 5
            create_new = True
            game_over_sound.play()  # Play the game over sound when the game ends
            points += 5  # Award bonus points for trying
            show_game_over_screen()  # Display the Game Over screen

    pygame.display.flip()

pygame.quit()