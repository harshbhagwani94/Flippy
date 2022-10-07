import random, sys, pygame, time, copy
from pygame.locals import *
from configparser import ConfigParser

from constants import window_width, board_width, text_color, text_bg_color_2, board_height, window_height, \
    text_bg_color_1

config = ConfigParser()
config.read('config.ini')

def main():
    global MAINCLOCK, DISPLAYSURF, FONT, BIGFONT, BGIMAGE

    pygame.init()
    MAINCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((config.getint('int_var',window_width), config.getint('int_var',window_height)))
    pygame.display.set_caption('Flippy')
    FONT = pygame.font.Font('freesansbold.ttf', 16)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 32)

    board_image = pygame.image.load('flippyboard.png')
    board_image = pygame.transform.smoothscale(board_image, (config.getint('int_var',board_width) * config.getint('int_var','SPACESIZE'), config.getint('int_var',board_height) * config.getint('int_var','SPACESIZE')))
    board_image_rect = board_image.get_rect()
    board_image_rect.topleft = (eval(config.get('int_var','XMARGIN')), eval(config.get('int_var','YMARGIN')))
    BGIMAGE = pygame.image.load('flippybackground.png')
    BGIMAGE = pygame.transform.smoothscale(BGIMAGE, (config.getint('int_var',window_width), config.getint('int_var',window_height)))
    BGIMAGE.blit(board_image, board_image_rect)

    while True:
        if run_game() == False:
            break


def start_game(main_board, player_tile=None, computer_tile=None):
    show_hints = False
    turn = random.choice(['computer', 'player'])

    new_game_surf = FONT.render('New Game', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_2,'r'),config.getint(text_bg_color_2,'g'),config.getint(text_bg_color_2,'b')))
    new_game_rect = new_game_surf.get_rect()
    new_game_rect.topright = (config.getint('int_var',window_width) - 8, 10)

    hints_surf = FONT.render('Hints', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_2,'r'),config.getint(text_bg_color_2,'g'),config.getint(text_bg_color_2,'b')))
    hints_rect = hints_surf.get_rect()
    hints_rect.topright = (config.getint('int_var',window_width) - 8, 40)

    while True:
        if turn == 'player':
            if get_valid_moves(main_board, player_tile) == []:
                break
            movexy = None
            while movexy == None:

                if show_hints:
                    boardToDraw = get_board_with_valid_moves(main_board, player_tile)
                else:
                    boardToDraw = main_board

                check_for_quit()
                for event in pygame.event.get(): # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        mousex, mousey = event.pos
                        if new_game_rect.collidepoint( (mousex, mousey) ):
                            return True
                        elif hints_rect.collidepoint( (mousex, mousey) ):
                            show_hints = not show_hints
                        movexy = get_spaced_clicked(mousex, mousey)
                        if movexy != None and not is_valid_move(main_board, player_tile, movexy[0], movexy[1]):
                            movexy = None

                draw_board(boardToDraw)
                draw_info(boardToDraw, player_tile, computer_tile, turn)

                DISPLAYSURF.blit(new_game_surf, new_game_rect)
                DISPLAYSURF.blit(hints_surf, hints_rect)

                MAINCLOCK.tick(config.getint('int_var','FPS'))
                pygame.display.update()

            make_move(main_board, player_tile, movexy[0], movexy[1], True)
            if get_valid_moves(main_board, computer_tile):
                turn = 'computer'

        else:
            if not get_valid_moves(main_board, computer_tile):
                break

            draw_board(main_board)
            draw_info(main_board, player_tile, computer_tile, turn)

            DISPLAYSURF.blit(new_game_surf, new_game_rect)
            DISPLAYSURF.blit(hints_surf, hints_rect)

            pause_until = time.time() + random.randint(5, 15) * 0.1
            while time.time() < pause_until:
                pygame.display.update()

            x, y = getComputerMove(main_board, computer_tile)
            make_move(main_board, computer_tile, x, y, True)
            if get_valid_moves(main_board, player_tile):
                turn = 'player'


def check_exit(text):
    text_surf = FONT.render(text, True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(config.getint('int_var',window_width) / 2), int(config.getint('int_var',window_height) / 2))
    DISPLAYSURF.blit(text_surf, text_rect)

    text2surf = BIGFONT.render('Play again?', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    text2rect = text2surf.get_rect()
    text2rect.center = (int(config.getint('int_var',window_width) / 2), int(config.getint('int_var',window_height) / 2) + 50)

    yes_surf = BIGFONT.render('Yes', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    yes_rect = yes_surf.get_rect()
    yes_rect.center = (int(config.getint('int_var',window_width) / 2) - 60, int(config.getint('int_var',window_height) / 2) + 90)

    # Make "No" button.
    no_surf = BIGFONT.render('No', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    no_rect = no_surf.get_rect()
    no_rect.center = (int(config.getint('int_var',window_width) / 2) + 60, int(config.getint('int_var',window_height) / 2) + 90)

    while True:
        check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if yes_rect.collidepoint( (mousex, mousey) ):
                    return True
                elif no_rect.collidepoint( (mousex, mousey) ):
                    return False
        DISPLAYSURF.blit(text_surf, text_rect)
        DISPLAYSURF.blit(text2surf, text2rect)
        DISPLAYSURF.blit(yes_surf, yes_rect)
        DISPLAYSURF.blit(no_surf, no_rect)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('int_var','FPS'))


def check_score(scores, player_tile, computer_tile):
    if scores[player_tile] > scores[computer_tile]:
        return 'You beat the computer by %s points! Congratulations!' % \
               (scores[player_tile] - scores[computer_tile])
    elif scores[player_tile] < scores[computer_tile]:
        return 'You lost. The computer beat you by %s points.' % \
               (scores[computer_tile] - scores[player_tile])
    else:
        return 'The game was a tie!'

def run_game():
    main_board = get_new_board()
    resetBoard(main_board)

    draw_board(main_board)
    player_tile, computer_tile = enter_player_tile()

    start_game(main_board, player_tile, computer_tile)

    draw_board(main_board)
    scores = get_score_of_board(main_board)

    text = check_score(scores, player_tile, computer_tile)

    check_exit(text)


def translateBoardToPixelCoord(x, y):
    return eval(config.get('int_var','XMARGIN')) + x * config.getint('int_var','SPACESIZE') + int(config.getint('int_var','SPACESIZE') / 2), eval(config.get('int_var','YMARGIN')) + y * config.getint('int_var','SPACESIZE') + int(config.getint('int_var','SPACESIZE') / 2)


def animateTileChange(tiles_to_flip, tileColor, additionalTile):
    if tileColor == config.get('tiles','WHITE_TILE'):
        additionalTileColor = (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b'))
    else:
        additionalTileColor = (config.getint('GRIDLINECOLOR','r'),config.getint('GRIDLINECOLOR','g'),config.getint('GRIDLINECOLOR','b'))
    additionalTileX, additionalTileY = translateBoardToPixelCoord(additionalTile[0], additionalTile[1])
    pygame.draw.circle(DISPLAYSURF, additionalTileColor, (additionalTileX, additionalTileY), int(config.getint('int_var','SPACESIZE') / 2) - 4)
    pygame.display.update()

    for rgbValues in range(0, 255, int(config.getint('int_var','ANIMATIONSPEED') * 2.55)):
        if rgbValues > 255:
            rgbValues = 255
        elif rgbValues < 0:
            rgbValues = 0

        if tileColor == config.get('tiles','WHITE_TILE'):
            color = tuple([rgbValues] * 3)
        elif tileColor == config.get('tiles','BLACK_TILE'):
            color = tuple([255 - rgbValues] * 3)

        for x, y in tiles_to_flip:
            centerx, centery = translateBoardToPixelCoord(x, y)
            pygame.draw.circle(DISPLAYSURF, color, (centerx, centery), int(config.getint('int_var','SPACESIZE') / 2) - 4)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('int_var','FPS'))
        check_for_quit()


def draw_board(board):
    DISPLAYSURF.blit(BGIMAGE, BGIMAGE.get_rect())

    for x in range(config.getint('int_var',board_width) + 1):
        startx = (x * config.getint('int_var','SPACESIZE')) + eval(config.get('int_var','XMARGIN'))
        starty = eval(config.get('int_var','YMARGIN'))
        endx = (x * config.getint('int_var','SPACESIZE')) + eval(config.get('int_var','XMARGIN'))
        endy = eval(config.get('int_var','YMARGIN')) + (config.getint('int_var',board_height) * config.getint('int_var','SPACESIZE'))
        pygame.draw.line(DISPLAYSURF, (config.getint('GRIDLINECOLOR','r'),config.getint('GRIDLINECOLOR','g'),config.getint('GRIDLINECOLOR','b')), (startx, starty), (endx, endy))
    for y in range(config.getint('int_var',board_height) + 1):
        startx = eval(config.get('int_var','XMARGIN'))
        starty = (y * config.getint('int_var','SPACESIZE')) + eval(config.get('int_var','YMARGIN'))
        endx = eval(config.get('int_var','XMARGIN')) + (config.getint('int_var',board_width) * config.getint('int_var','SPACESIZE'))
        endy = (y * config.getint('int_var','SPACESIZE')) + eval(config.get('int_var','YMARGIN'))
        pygame.draw.line(DISPLAYSURF, (config.getint('GRIDLINECOLOR','r'),config.getint('GRIDLINECOLOR','g'),config.getint('GRIDLINECOLOR','b')), (startx, starty), (endx, endy))

    for x in range(config.getint('int_var',board_width)):
        for y in range(config.getint('int_var',board_height)):
            centerx, centery = translateBoardToPixelCoord(x, y)
            if board[x][y] == config.get('tiles','WHITE_TILE') or board[x][y] == config.get('tiles','BLACK_TILE'):
                if board[x][y] == config.get('tiles','WHITE_TILE'):
                    tileColor = (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b'))
                else:
                    tileColor = (config.getint('GRIDLINECOLOR','r'),config.getint('GRIDLINECOLOR','g'),config.getint('GRIDLINECOLOR','b'))
                pygame.draw.circle(DISPLAYSURF, tileColor, (centerx, centery), int(config.getint('int_var','SPACESIZE') / 2) - 4)
            if board[x][y] == config.get('tiles','HINT_TILE'):
                pygame.draw.rect(DISPLAYSURF, (config.getint('HINTCOLOR','r'),config.getint('HINTCOLOR','g'),config.getint('HINTCOLOR','b')), (centerx - 4, centery - 4, 8, 8))


def get_spaced_clicked(mousex, mousey):
    for x in range(config.getint('int_var',board_width)):
        for y in range(config.getint('int_var',board_height)):
            if x * config.getint('int_var', 'SPACESIZE') + eval(config.get('int_var', 'XMARGIN')) < mousex < (x + 1) * config.getint('int_var', 'SPACESIZE') + eval(config.get('int_var', 'XMARGIN')) and \
                    y * config.getint('int_var', 'SPACESIZE') + eval(config.get('int_var', 'YMARGIN')) < mousey < (
                    y + 1) * config.getint('int_var', 'SPACESIZE') + eval(config.get('int_var', 'YMARGIN')):
                return x, y
    return None


def draw_info(board, player_tile, computer_tile, turn):
    scores = get_score_of_board(board)
    score_surf = FONT.render("Player Score: %s    Computer Score: %s    %s's Turn" % (str(scores[player_tile]), str(scores[computer_tile]), turn.title()), True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')))
    score_rect = score_surf.get_rect()
    score_rect.bottomleft = (10, config.getint('int_var',window_height) - 5)
    DISPLAYSURF.blit(score_surf, score_rect)


def resetBoard(board):
    for x in range(config.getint('int_var',board_width)):
        for y in range(config.getint('int_var',board_height)):
            board[x][y] = config.get('tiles','EMPTY_SPACE')

    board[3][3] = config.get('tiles','WHITE_TILE')
    board[3][4] = config.get('tiles','BLACK_TILE')
    board[4][3] = config.get('tiles','BLACK_TILE')
    board[4][4] = config.get('tiles','WHITE_TILE')


def get_new_board():
    board = []
    for i in range(config.getint('int_var',board_width)):
        board.append([config.get('tiles','EMPTY_SPACE')] * config.getint('int_var',board_height))

    return board


def is_valid_move(board, tile, xstart, ystart):
    if board[xstart][ystart] != config.get('tiles','EMPTY_SPACE') or not is_on_board(xstart, ystart):
        return False

    board[xstart][ystart] = tile

    if tile == config.get('tiles','WHITE_TILE'):
        otherTile = config.get('tiles','BLACK_TILE')
    else:
        otherTile = config.get('tiles','WHITE_TILE')

    tiles_to_flip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if is_on_board(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not is_on_board(x, y):
                continue
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not is_on_board(x, y):
                    break
            if not is_on_board(x, y):
                continue
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    if x == xstart and y == ystart:
                        break
                    tiles_to_flip.append([x, y])

    board[xstart][ystart] = config.get('tiles','EMPTY_SPACE')
    if len(tiles_to_flip) == 0:
        return False
    return tiles_to_flip


def is_on_board(x, y):
    return x >= 0 and x < config.getint('int_var',board_width) and y >= 0 and y < config.getint('int_var',board_height)


def get_board_with_valid_moves(board, tile):
    dupe_board = copy.deepcopy(board)

    for x, y in get_valid_moves(dupe_board, tile):
        dupe_board[x][y] = config.get('tiles','HINT_TILE')
    return dupe_board


def get_valid_moves(board, tile):
    validMoves = []

    for x in range(config.getint('int_var',board_width)):
        for y in range(config.getint('int_var',board_height)):
            if is_valid_move(board, tile, x, y) != False:
                validMoves.append((x, y))
    return validMoves


def get_score_of_board(board):
    xscore = 0
    oscore = 0
    for x in range(config.getint('int_var',board_width)):
        for y in range(config.getint('int_var',board_height)):
            if board[x][y] == config.get('tiles','WHITE_TILE'):
                xscore += 1
            if board[x][y] == config.get('tiles','BLACK_TILE'):
                oscore += 1
    return {config.get('tiles','WHITE_TILE'):xscore, config.get('tiles','BLACK_TILE'):oscore}


def enter_player_tile():
    text_surf = FONT.render('Do you want to be white or black?', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    text_rect = text_surf.get_rect()
    text_rect.center = (int(config.getint('int_var',window_width) / 2), int(config.getint('int_var',window_height) / 2))

    xSurf = BIGFONT.render('White', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    xRect = xSurf.get_rect()
    xRect.center = (int(config.getint('int_var',window_width) / 2) - 60, int(config.getint('int_var',window_height) / 2) + 40)

    oSurf = BIGFONT.render('Black', True, (config.getint(text_color,'r'),config.getint(text_color,'g'),config.getint(text_color,'b')), (config.getint(text_bg_color_1,'r'),config.getint(text_bg_color_1,'g'),config.getint(text_bg_color_1,'b')))
    oRect = oSurf.get_rect()
    oRect.center = (int(config.getint('int_var',window_width) / 2) + 60, int(config.getint('int_var',window_height) / 2) + 40)

    while True:
        check_for_quit()
        for event in pygame.event.get():
            if event.type == MOUSEBUTTONUP:
                mousex, mousey = event.pos
                if xRect.collidepoint( (mousex, mousey) ):
                    return [config.get('tiles','WHITE_TILE'), config.get('tiles','BLACK_TILE')]
                elif oRect.collidepoint( (mousex, mousey) ):
                    return [config.get('tiles','BLACK_TILE'), config.get('tiles','WHITE_TILE')]

        DISPLAYSURF.blit(text_surf, text_rect)
        DISPLAYSURF.blit(xSurf, xRect)
        DISPLAYSURF.blit(oSurf, oRect)
        pygame.display.update()
        MAINCLOCK.tick(config.getint('int_var','FPS'))


def make_move(board, tile, xstart, ystart, realMove=False):
    tiles_to_flip = is_valid_move(board, tile, xstart, ystart)

    if tiles_to_flip == False:
        return False

    board[xstart][ystart] = tile

    if realMove:
        animateTileChange(tiles_to_flip, tile, (xstart, ystart))

    for x, y in tiles_to_flip:
        board[x][y] = tile
    return True


def is_on_corner(x, y):
    return (x == 0 and y == 0) or \
           (x == config.getint('int_var',board_width) and y == 0) or \
           (x == 0 and y == config.getint('int_var',board_height)) or \
           (x == config.getint('int_var',board_width) and y == config.getint('int_var',board_height))


def getComputerMove(board, computer_tile):
    possibleMoves = get_valid_moves(board, computer_tile)

    random.shuffle(possibleMoves)

    for x, y in possibleMoves:
        if is_on_corner(x, y):
            return [x, y]

    bestScore = -1
    for x, y in possibleMoves:
        dupe_board = copy.deepcopy(board)
        make_move(dupe_board, computer_tile, x, y)
        score = get_score_of_board(dupe_board)[computer_tile]
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    return bestMove


def check_for_quit():
    for event in pygame.event.get((QUIT, KEYUP)): # event handling loop
        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()


if __name__ == '__main__':
    main()
