import os
import pickle
import random

import pygame as pg
import neat
from shooter import Shooter
from bullet import Bullet

pg.init()

WIDTH = 1000
HEIGHT = 600
WIN = pg.display.set_mode((WIDTH, HEIGHT))
FPS = 120
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
MAX_BULLETS = 1
NUMBER_OF_PLAYERS = 2
FONT = pg.font.Font('freesansbold.ttf', 20)


shooter1 = Shooter(100, HEIGHT // 2, 30, 20, speed=7, color=GREEN)
shooter2 = Shooter(900, HEIGHT // 2, 30, 20, speed=7, color=BLUE)

shooters = [shooter1, shooter2]
ammoCounts = [MAX_BULLETS, MAX_BULLETS]
cd = [0, 0]
bullets = [[], []]
hits = [0, 0]
misses = [0, 0]
attempts = [0, 0]
wall_hugs = [0, 0]              # AI loves to do this, lets punish
best_hitman = None


def manage_cd(cds):
    for i, cd in enumerate(cds):
        if cd < 30:
            cds[i] += 1


def ai_movement(shooters, bullets, nets):
    for i, net in enumerate(nets):
        other_i = abs(i - 1)

        try:
            get_output = net.activate((shooters[i].y / 100, abs(shooters[i].x - bullets[other_i][0].x) / 100, abs(shooters[i].y - bullets[other_i][0].y) / 100, abs(shooters[i].y - shooters[other_i].y) / 100))
        except IndexError:      # if no bullets
            get_output = net.activate((shooters[i].y / 100, 0, 0, abs(shooters[i].y - shooters[other_i].y) / 100))

        # try:          #THE OLD INPUTS, FOR V2
        #     get_output = net.activate((shooters[i].y, shooters[other_i].y, abs(shooters[i].x - bullets[other_i][0].x), abs(shooters[i].y - shooters[other_i].y)))
        # except IndexError:      # if no bullets
        #     get_output = net.activate((shooters[i].y, shooters[other_i].y, 0, abs(shooters[i].y - shooters[other_i].y)))

        state = get_output.index(max(get_output))
        shooters[i].what_to_do(state)


def player_movement(s1):
    keys = pg.key.get_pressed()

    if keys[pg.K_UP]:
        s1.what_to_do(0)
    if keys[pg.K_DOWN]:
        s1.what_to_do(1)
    if keys[pg.K_SPACE]:
        s1.what_to_do(2)


def shoot(shooter, index, bullets, attempts):
    if shooter.color == GREEN:
        speed = 25
    else:
        speed = -25
    new_bullet = Bullet(shooter.x, shooter.y + (shooter.height//2), 10, 5, speed, RED)
    bullets[index].append(new_bullet)
    attempts[index] += 1


def handle_collision(bullets, ammo, shooters, hits, misses):
    for i, bullet_group in enumerate(bullets):
        for j, bullet in enumerate(bullet_group):
            if bullet.x + bullet.width < 0 or bullet.x > WIDTH or bullet.y + bullet.height > HEIGHT or bullet.y < 0:
                bullets[i].pop(j)
                ammo[i] += 1
                misses[i] += 0.5
            new_i = abs(i-1)
            if bullet.x + bullet.width > shooters[new_i].x and bullet.x < shooters[new_i].x + shooters[new_i].width and bullet.y + bullet.height > shooters[new_i].y and bullet.y < shooters[new_i].y + shooters[new_i].height:
                bullets[i].pop(j)
                hits[i] += 10
                attempts[new_i] -= 8
                ammo[i] += 1

    for i, shooter in enumerate(shooters):
        if shooter.y + shooter.height >= HEIGHT:
            shooter.y = HEIGHT - shooter.height
            wall_hugs[i] += 0.03
        if shooter.y <= 0:
            shooter.y = 0
            wall_hugs[i] += 0.03


def draw(win, shooters, bullets, score_texts, id_texts):
    win.fill(BLACK)
    for text_group in score_texts:
        win.blit(text_group[0], text_group[1])
    try:
        for id_text_group in id_texts:
            win.blit(id_text_group[0], id_text_group[1])
    except TypeError:
        var = None
    for shooter in shooters:
        shooter.draw(win)
    for bullet_group in bullets:
        for bullet in bullet_group:
            bullet.draw(win)
    pg.display.update()


def reset(hits, attempts, misses, wall_hugs, shooters, bullets, ammo):
    for i in range(NUMBER_OF_PLAYERS):
        hits[i] = 0
        attempts[i] = 0
        misses[i] = 0
        wall_hugs[i] = 0
        ammoCounts[i] = 1

    for shooter in shooters:
        shooter.x = shooter.orX
        shooter.y = shooter.orY

    for i, bullet_group in enumerate(bullets):
        for j, bullet in enumerate(bullet_group):
            if bullets[i][j]:
                bullets[i].pop(j)


def start_training(config, genomes, genome_ids):
    nets = [neat.nn.FeedForwardNetwork.create(genomes[0], config),
            neat.nn.FeedForwardNetwork.create(genomes[1], config)]

    run = True

    count = 0
    while run:
        pg.time.Clock().tick(FPS)

        manage_cd(cd)

        ai_movement(shooters, bullets, nets)

        for i, shooter in enumerate(shooters):
            if shooter.shoot:
                if ammoCounts[i] > 0 and cd[i] >= 30:
                    shoot(shooter, i, bullets, attempts)
                    ammoCounts[i] -= 1
                    cd[i] = 0
                shooter.shoot = False

        for bullet_group in bullets:
            for bullet in bullet_group:
                bullet.move()

        handle_collision(bullets, ammoCounts, shooters, hits, misses)

        score1 = FONT.render(hits[0].__str__(), True, WHITE)
        score2 = FONT.render(hits[1].__str__(), True, WHITE)
        id1 = FONT.render("ID: " + genome_ids[0].__str__(), True, WHITE)
        id2 = FONT.render("ID: " + genome_ids[1].__str__(), True, WHITE)
        score1Rect = score1.get_rect()
        score2Rect = score2.get_rect()
        id1Rect = id1.get_rect()
        id2Rect = id2.get_rect()
        score1Rect.center = (WIDTH // 2 - 100, 50)
        score2Rect.center = (WIDTH // 2 + 100, 50)
        id1Rect.center = (shooters[0].x, 50)
        id2Rect.center = (shooters[1].x, 50)

        score_texts = [[score1, score1Rect], [score2, score2Rect]]
        id_texts = [[id1, id1Rect], [id2, id2Rect]]

        draw(WIN, shooters, bullets, score_texts, id_texts)

        count += 1

        if count > 200:
            for i, genome in enumerate(genomes):
                genome.fitness += hits[i]
                genome.fitness += attempts[i] if attempts[i] > 0 else -10
                genome.fitness -= misses[i]
                genome.fitness -= wall_hugs[i]

            reset(hits, attempts, misses, wall_hugs, shooters, bullets, ammoCounts)
            break

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


def train_against_best(config, genomes, genome_ids):
    nets = [neat.nn.FeedForwardNetwork.create(genomes[0], config),
            neat.nn.FeedForwardNetwork.create(genomes[1], config)]

    run = True

    count = 0
    while run:
        pg.time.Clock().tick(FPS)

        manage_cd(cd)

        ai_movement(shooters, bullets, nets)

        for i, shooter in enumerate(shooters):
            if shooter.shoot:
                if ammoCounts[i] > 0 and cd[i] >= 30:
                    shoot(shooter, i, bullets, attempts)
                    ammoCounts[i] -= 1
                    cd[i] = 0
                shooter.shoot = False

        for bullet_group in bullets:
            for bullet in bullet_group:
                bullet.move()

        handle_collision(bullets, ammoCounts, shooters, hits, misses)

        score1 = FONT.render(hits[0].__str__(), True, WHITE)
        score2 = FONT.render(hits[1].__str__(), True, WHITE)
        id1 = FONT.render("ID: " + genome_ids[0].__str__(), True, WHITE)
        id2 = FONT.render("ID: " + genome_ids[1].__str__(), True, WHITE)
        score1Rect = score1.get_rect()
        score2Rect = score2.get_rect()
        id1Rect = id1.get_rect()
        id2Rect = id2.get_rect()
        score1Rect.center = (WIDTH // 2 - 100, 50)
        score2Rect.center = (WIDTH // 2 + 100, 50)
        id1Rect.center = (shooters[0].x, 50)
        id2Rect.center = (shooters[1].x, 50)

        score_texts = [[score1, score1Rect], [score2, score2Rect]]
        id_texts = [[id1, id1Rect], [id2, id2Rect]]

        draw(WIN, shooters, bullets, score_texts, id_texts)

        count += 1

        if count > 200:
            genomes[0].fitness += hits[0]
            genomes[0].fitness += attempts[0] if attempts[0] > 0 else -10
            genomes[0].fitness -= misses[0]
            genomes[0].fitness -= wall_hugs[0]

            reset(hits, attempts, misses, wall_hugs, shooters, bullets, ammoCounts)
            break

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


def tester(config, hitman):
    net = neat.nn.FeedForwardNetwork.create(hitman, config)

    run = True

    while run:
        pg.time.Clock().tick(FPS)

        manage_cd(cd)

        try:
            get_output = net.activate((shooters[0].y, shooters[1].y, abs(shooters[0].x - bullets[1][0].x),
                                       abs(shooters[1].y - shooters[0].y)))
        except IndexError:
            get_output = net.activate(
                (shooters[0].y, shooters[1].y, 0, abs(shooters[0].y - shooters[1].y)))

        state = get_output.index(max(get_output))
        shooters[0].what_to_do(state)

        player_movement(shooters[1])

        for i, shooter in enumerate(shooters):
            if shooter.shoot:
                if ammoCounts[i] > 0 and cd[i] >= 30:
                    shoot(shooter, i, bullets, attempts)
                    ammoCounts[i] -= 1
                    cd[i] = 0
                shooter.shoot = False

        for bullet_group in bullets:
            for bullet in bullet_group:
                bullet.move()

        handle_collision(bullets, ammoCounts, shooters, hits, misses)

        score1 = FONT.render(hits[0].__str__(), True, WHITE)
        score2 = FONT.render(hits[1].__str__(), True, WHITE)
        score1Rect = score1.get_rect()
        score2Rect = score2.get_rect()
        score1Rect.center = (WIDTH // 2 - 100, 50)
        score2Rect.center = (WIDTH // 2 + 100, 50)
        score_texts = [[score1, score1Rect], [score2, score2Rect]]

        keys = pg.key.get_pressed()
        if keys[pg.K_r]:
            reset(hits, attempts, misses, wall_hugs, shooters, bullets, ammoCounts)

        draw(WIN, shooters, bullets, score_texts, None)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()


def eval_genomes(genomes, config):
    for i, (genome_id1, genome1) in enumerate(genomes):
        if i == len(genomes) - 1:
            break
        genome1.fitness = 0
        for i2, genome2 in genomes[i+1:]:
            genome2.fitness = 0 if genome2.fitness is None else genome2.fitness
            genomesg = [genome1, genome2]
            genome_ids = [genome_id1, i2]
            start_training(config, genomesg, genome_ids)


def special_eval_genomes(genomes, config):
    for genome_id1, genome1 in genomes:
        genome1.fitness = 0
        genomes = [genome1, best_hitman]
        genome_ids = [genome_id1, "999"]
        train_against_best(config, genomes, genome_ids)


def train_ai(config):

    # p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-4')
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    best_one = p.run(eval_genomes, 5)

    with open("hitmanV4.pickle", "wb") as f:
        pickle.dump(best_one, f)


def special_training(config):
    global best_hitman
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    with open("hitmanV2Duplicate.pickle", "rb") as f:
        best_hitman = pickle.load(f)

    best_one = p.run(special_eval_genomes, 50)

    with open("hitmanV4.pickle", "wb") as f:
        pickle.dump(best_one, f)


def test_ai(config):
    # with open("hitman.pickle", "rb") as f:            # HITMAN 1 Tactic - Hug the ground, spam if enemy comes near
    #     hitman = pickle.load(f)

    # with open("hitmanV2.pickle", "rb") as f:          # HITMAN 2 Tactic - Actually is pro
    #     hitman = pickle.load(f)

    # with open("hitmanV3.pickle", "rb") as f:            # HITMAN 3 Tactic - Hug the top, spam (dumb again)
    #     hitman = pickle.load(f)

    with open("hitmanV4.pickle", "rb") as f:            # Garbage
        hitman = pickle.load(f)

    tester(config, hitman)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    # train_ai(config)
    # special_training(config)
    test_ai(config)

