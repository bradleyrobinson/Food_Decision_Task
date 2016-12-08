import pygame
import review
import timing
import makedata
import os
import csv
import random
from pygame.locals import *
import serial
pygame.init()


""" TODO:
- List the markers here!
- Add the resting state
- Make sure that the data is recording properly

 Marker:1 = Start rest
 Marker:0 = End rest
 Marker:2 = Start rating task
 Marker:C = End rating task
 Marker:D = Start prep_screen
 Marker:3 choice start
 Marker:4 = Cooperate
 Marker:5 = Defect
 Marker:6 = No decision
 Marker:7 = Reward
 Marker:8 = Sucker
 Marker:9 =  Temptation
 Marker:A = Punishment
"""


""" ---------------------------------------------------------------------------------------------------------------
Here be constants
-------------------------------------------------------------------------------------------------------------------"""
font = pygame.font.SysFont("arial", 34)
bold_font = pygame.font.SysFont("arial", 46)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
# And here be the images that we'll be rating
file_foods = {}
with open('fooditems.csv') as csvfile:
    food_reader = csv.DictReader(csvfile, delimiter=',', quotechar='|')
    for row in food_reader:
        file_foods[row['title'].title()] = row['file']

# This creates lists for the opponent decisions, then populates and shuffles them to randomize computer response
opponent_a = []
opponent_b = []
opponent_c = []
practice_opponent = ['c', 'c','d','c', 'c']


def make_opponent(trials, cooperation_rate, opponent):
    for cooperate in range(0, cooperation_rate):
        opponent.append('c')
    for defect in range(0, (trials - cooperation_rate)):
        opponent.append('d')

make_opponent(24, 8, opponent_c)
make_opponent(24, 12, opponent_b)
make_opponent(24, 16, opponent_a)
random.shuffle(opponent_a)
random.shuffle(opponent_b)
random.shuffle(opponent_c)


class RatedFood:
    def __init__(self, food, rating):
        self.food = food
        self.rating = rating

    def get_rating(self):
        return self.rating

    def get_food(self):
        return self.rating


class Participant:
    def __init__(self, data_cols):
        # This calls a function that allows us to put in the participant name in a GUI window
        self.app = review.getParticipant()
        self.participant_num = self.app.getName()
        self.date = self.app.getDate()
        # We need to connect with the Emotiv software, and to do so we need to connect with the port.
        # The experimenter enters the port number (on the opposite end of the port that Emotiv uses)
        self.port_name = self.app.get_port()
        self.port = serial.Serial(self.port_name, 38400)

        # After getting that info, let's make sure that we know what type of data we'll record,
        # passed by the user, reaction time must be called "RT"
        self.data_cols = data_cols
        self.fileID = self.date + self.participant_num

        # Now, let's pass the information to the data file that we will write
        self.file = makedata.DataSheet(self.data_cols, self.participant_num, self.fileID)

        # Money amount at the beginning of the study:
        self.money = 50.00
        # Creates an object that allows us to get the reaction time, updated each trial
        self.experiment_rt = timing.stimTime()

        self.rated_list = []

        # A dictionary that allows us to store the participants ratings of each object
        self.food_ratings = {}

        # Multiple lists of FoodRating objects
        self.food_objects = []

        # Categories of food objects for the decision task
        self.categories = []
        self.category_size = 0

        # AI position in the decision array
        self.ai_position = 0
        # Stores the computer's decision that we can get the next trial
        self.ai_decision = None

        # Stores the player's last decision
        self.my_decision = None

        self.last_trial = None

    # The next two functions allow us to get data needed for the reaction time
    def stim_start(self, marker=None):
        self.experiment_rt.stim_start()
        if marker is not None:
            self.port.write(marker)

    def stim_end(self, marker=None):
        self.experiment_rt.stim_end()
        if marker is not None:
            self.port.write(marker)

    # This can be called at the end of each trial, which helps make up a list that is put into the csv file after the
    #
    def record_trial(self, data_record):
        this_rt = self.experiment_rt.get_rt()
        data_record['Participant'] = self.participant_num
        data_record['RT'] = this_rt
        self.file.writeSection(data_record)

    def record_data(self):
        self.file.writeSection(self.rated_list)

    def rated_food(self, food, rating):
        food_rated = RatedFood(food, rating)
        self.food_objects.append(food_rated)

    def opponent_decision(self, opponent, my_decision):
        if self.ai_position >= len(opponent):
            self.ai_position = 0
        self.ai_decision = opponent[self.ai_position]
        self.ai_position += 1
        self.my_decision = my_decision
        self.trial_result()

    def trial_result(self):
        result = self.my_decision + self.ai_decision
        if result == 'Cc':
            self.last_trial = 'R'
            self.money -= 6.00
        elif result == 'Cd':
            self.last_trial = 'S'
            self.money -= 9.00
        elif result == 'Dc':
            self.last_trial = 'T'
            self.money -= 9.00
        elif result == 'Dd':
            self.last_trial = 'P'
            self.money -= 12.00
        else:
            print "Something went terribly wrong, master!"

    # This is called after the training trials.
    def set_amount(self):
        self.money = 200.00

    def sort_ratings(self):
        # First sort the list of food objects
        self.food_objects.sort(key=lambda x: x.rating, reverse=True)
        # Now we need three categories, so we should figure out how many lists we need, using int division
        self.category_size = len(self.food_objects)/3

        for i in range(0, 3):
            category = []
            for j in range(0, self.category_size):
                category.append(self.food_objects.pop())
            self.categories.append(category)


# Inter-stimuli interval, which is played for a set amount of time
def isi(length, participant, screen, size, mark_start=False, mark_end=False, jitter=False, jitter_beg=0):
    c = timing.stimTime()
    time_passed = 0
    x = size[0]/2
    y = size[1]/2
    if mark_start:
        participant.stim_start(marker="1")
    j_length = length
    if jitter == True:
        j_length = random.randrange(jitter_beg, length)
        
    while time_passed < j_length:
        temp, end = get_decision()
        if end == 'end':
            pygame.quit()
        c.stim_end()
        time_passed = c.get_rt()
        # This is simply the + sign
        text = font.render("+", 1, BLACK)
        screen.fill(WHITE)
        screen.blit(text, [x, y])
        pygame.display.flip()
        
    if mark_end:
        participant.stim_end(marker="0")


def get_rating():
    response = 0
    done = False
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                response = 1
                done = True
            elif event.key == pygame.K_2:
                response = 2
                done = True
            elif event.key == pygame.K_3:
                response = 3
                done = True
            elif event.key == pygame.K_4:
                response = 4
                done = True
            elif event.key == pygame.K_5:
                response = 5
                done = True
            elif event.key == pygame.K_6:
                response = 6
                done = True
            elif event.key == pygame.K_6:
                response = 6
                done = True
            elif event.key == pygame.K_7:
                response = 7
                done = True
            elif event.key == pygame.K_8:
                response = 8
                done = True
            elif event.key == pygame.K_9:
                response = 9
                done = True
            elif event.key == pygame.K_ESCAPE:
                return 'end'
    return response, done


# Since the image names are the same, but sizes are different depending on the task, they are separated by folder
# This function allows us to get the proper path for the task.
def get_path(task, file_name):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_directory, task, file_name)


def rating_task(participant, screen, size):
    # Gets the center
    x = size[0] / 2
    # Marker:2 = Start rating task
    participant.stim_start(marker="2")
    for key in file_foods:
        done = False
        text = font.render(key, 1, BLACK)
        response = 0
        
        while not done:
            # This gets the user's response
            response, done = get_rating()
            if response == 'end':
                pygame.quit()
            if done:
                participant.stim_end()
            screen.fill(WHITE)
            # We create the image based on the list of foods
            picture = pygame.image.load(get_path("rating", file_foods[key])).convert()
            rating_image = pygame.image.load("ratingtable.jpg").convert()
            # Get the image position
            image_rect = picture.get_rect()
            x_pos1 = x - image_rect[2]/2
            # Get the text position based on its size
            x_pos2 = x - font.size(key)[0]/2
            # Get the position of the rating_image
            x_pos3 = x - (rating_image.get_rect()[2]) / 2
            y_pos = 80 + image_rect[3]
            # Now blit the images and text
            screen.blit(rating_image, [x_pos3, y_pos])
            screen.blit(text, (x_pos2, (image_rect[3] + 45)))
            screen.blit(picture, (x_pos1, 30))
            pygame.display.flip()
        # Here we send the results of the trial to the participant object, which then records it to the data file
        decision = {"Food Rated": key, "Food Rating": response, "Trial Food C": "NA", "Trial Food D": "NA",
                    "Decision": "NA", "Opponent Decision": "NA"}
        participant.record_trial(decision)
        participant.rated_food(key, response)
    # Marker:C = End rating task
    participant.stim_start(marker="C")
    # When we're done rating the objects, we need to sort the ratings into different groups, depending on how high
    # the ratings are.
    participant.sort_ratings()


def prep_screen(screen, size, c_food, d_food, participant, training=False):
    # Declaration of string variables
    cooperate = "Cost: 3.00"
    c_button = "Press 1"
    defect = "Cost: 6.00"
    d_button = "Press 0"
    money = "Account Balance: " + str(participant.money)
    wait = "WAIT..."
    # Declaration of images
    pict1 = pygame.image.load(get_path("decision", file_foods[c_food.title()]))
    pict2 = pygame.image.load(get_path("decision", file_foods[d_food.title()]))
    # Images of buttons:
    button_image_0 = pygame.image.load("button_0.png")
    button_image_1 = pygame.image.load("button_1.png")
    # Declaration of text
    food_text_1 = font.render(c_food.title(), 1, BLACK)
    c_description = font.render(cooperate, 1, BLACK)
    c_press = font.render(c_button, 1, BLACK)
    food_text_2 = font.render(d_food.title(), 1, BLACK)
    d_description = font.render(defect, 1, BLACK)
    d_press = font.render(d_button, 1, BLACK)
    money_text = font.render(money, 1, BLACK)
    wait_text = bold_font.render(wait, 1, RED)
    # Declaration of location variables
    x = size[0] - pict2.get_rect()[2] - 100
    t_1pos = [(50 + (pict1.get_rect()[2] - font.size(c_food)[0]) / 2), pict1.get_rect()[3] + 100]
    t_cpos = [(50 + (pict1.get_rect()[2] - font.size(cooperate)[0]) / 2), t_1pos[1] - 40]
    t_1b = [(50 + (pict1.get_rect()[2] - font.size(c_button)[0]) / 2), t_1pos[1] + 40]
    t_2pos = [(x + (pict2.get_rect()[2] - font.size(d_food)[0]) / 2), pict2.get_rect()[3] + 100]
    t_dpos = [(x + (pict2.get_rect()[2] - font.size(defect)[0]) / 2), t_2pos[1] - 40]
    t_2b = [(x + (pict2.get_rect()[2] - font.size(c_button)[0]) / 2), t_2pos[1] + 40]
    wait_pos = [(size[0] - font.size(wait)[0])/2, size[1]/2]
    # Timing variables
    c = timing.stimTime()
    time_passed = 0

    # Marker:D = Start prep_screen
    if not training:
        participant.stim_start(marker="D")

    # Loops for given time so the participant sees the choice they will have
    while time_passed < 4000:
        c.stim_end()
        time_passed = c.get_rt()
        end_experiment = get_decision()
        if end_experiment == 'end':
            pygame.quit()
        screen.fill(WHITE)
        screen.blit(pict1, [100, 50])
        screen.blit(food_text_1, t_1pos)
        screen.blit(c_description, t_cpos)
        screen.blit(c_press, t_1b)
        screen.blit(button_image_1, [t_1b[0], t_1b[1] + 40])
        screen.blit(pict2, [x, 50])
        screen.blit(food_text_2, t_2pos)
        screen.blit(d_press, t_2b)
        screen.blit(button_image_0, [t_2b[0], t_2b[1] + 40])
        screen.blit(d_description, t_dpos)
        screen.blit(money_text, [((size[0]/2) - (font.size(money)[0]/2)), 10])
        screen.blit(wait_text, wait_pos)
        pygame.display.flip()
    return t_1b[0], t_2b[0]


def get_decision():
    end = False
    response = 'none'
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                response = 'C'
                end = True
            elif event.key == pygame.K_0:
                response = 'D'
                end = True
            elif event.key == pygame.K_ESCAPE:
                response = 'end'
    return end, response


# Simply says: 'choose', giving the participant 2 seconds to respond based on the previous image
def choice_screen(screen, size, participant, c_food, d_food, button_pos_1, button_pos_0, length=2000, training=False):
    end = False
    decision = "none"
    y = size[1] / 2
    # Marker:3 choice start
    if not training:
        participant.stim_start(marker="3")
    while decision == "none":
        c = timing.stimTime()
        time_passed = 0
        while time_passed < length and not end:
            c.stim_end()
            time_passed = c.get_rt()
            screen.fill(WHITE)

            text = bold_font.render("CHOOSE", 1, GREEN)
            button_0 = font.render("Press 0", 1, BLACK)
            button_1 = font.render("Press 1", 1, BLACK)

            # This gives us the actual center position for the text we want to print
            x = (size[0] - font.size("Choose")[0])/2
            screen.blit(text, [x, y])
            screen.blit(button_0, [button_pos_0, y])
            screen.blit(button_1, [button_pos_1, y])
            pygame.display.flip()
            end, decision = get_decision()
        if decision == "none" and not training:
            describe_task(["No response was received. Please try again"], screen, size)
            prep_screen(screen, size, c_food, d_food, participant)
        elif decision == "none" and training:
            decision = ' '
    if training:
        participant.opponent_decision(opponent_a, decision)
    elif not training:
        participant.opponent_decision(opponent_a, decision)
        trial_result = {"Food Rated": "NA", "Food Rating": "NA", "Trial Food C": c_food, "Trial Food D": d_food,
                        "Decision": decision, "Opponent Decision": participant.ai_decision}
        # Marker:4 = Cooperate
        # Marker:5 = Defect
        # Marker:6 = No decision
        if decision == 'C':
            marker = "4"
        elif decision == 'D':
            marker = "5"
        else:
            marker = "6"
        participant.stim_end(marker=marker)
        participant.record_trial(trial_result)

def get_outcome_marker(participant):
    # Marker:7 = Reward
    # Marker:8 = Sucker
    # Marker:9 =  Temptation
    # Marker:A = Punishment
    if participant.last_trial == 'R':
        marker = "7"
    elif participant.last_trial == 'S':
        marker = "8"
    elif participant.last_trial == 'T':
        marker = "9"
    elif participant.last_trial == 'P':
        marker = "A"
    return marker

# This prints the outcome of the trial onto the screen, as well as sending the proper marker record the outcome of the trial.
def outcome_screen(screen, size, participant, c_food, d_food, training=False):
    if not training:
        participant.stim_start(marker=get_outcome_marker(participant))
    cost = 0
    if participant.last_trial == 'S' or participant.last_trial == 'T':
        cost = 9.00
    elif participant.last_trial == 'R':
        cost = 6.00
    elif participant.last_trial == 'P':
        cost = 12.00
    if participant.ai_decision == 'c':
        describe_task(["Your opponent chose the less expensive option: " + c_food +
                       ". ~n The total cost this trial was: $" + str(cost) +
                       " ~n The current amount of money left in the account is $" + str(participant.money)], screen, size)
    else:
        describe_task(["Your opponent chose the more expensive option: " + d_food +
                       ". ~n The total cost this trial was: $" + str(cost) +
                       " ~n The current amount of money left in the account is $" + str(participant.money)], screen, size)



# This randomly selects an item off the list, and returns it
def get_decision_foods(participant, position):
    # Random choice of which category to select from
    which_category_a = random.choice([0, 1])
    which_category_b = 2
    if which_category_a == 0:
        which_category_b = random.choice([1, 2])

    c_food = participant.categories[which_category_a][position].food.title()
    d_food = participant.categories[which_category_b][position].food.title()

    return c_food, d_food


def decision_task(screen, size, participant, training=False, trials=20):
    position = 0
    for i in range(0, trials):
        if position >= participant.category_size:
            position = 0
        if participant.money < 0:
            break

        # Get the food items
        c_food, d_food = get_decision_foods(participant, position)
        # 2-second ISI
        isi(2000, participant, screen, size, jitter=True, jitter_beg=1000)
        # 6-second window prep screen (what do you want to choose),
        button_pos_1, button_pos_0 = prep_screen(screen, size, c_food, d_food, participant, training=training)
        # Short ISI
        # TODO: Make sure markers are correct here!!!
        isi(500, participant, screen, size, jitter=True, jitter_beg=250)
        # A choice screen, where they have 2 s, progresses when they press the button
        choice_screen(screen, size, participant, c_food, d_food, button_pos_1, button_pos_0, training=training)
        # 2-second ISI
        isi(2000, participant, screen, size)
        # Outcome screen
        outcome_screen(screen, size, participant, c_food, d_food, training=training)
        position += 1
    else:
        if participant.money < 0:
            isi(2000, participant, screen, size)
            describe_task(["You are out of money!"], screen, size)


# This tells us how high the text list will be, so we can make sure that it is centered
def get_top(txt_list):
    height = 0
    for txt in txt_list:
        height += font.size(txt)[1]
    return height


def word_wrap(txt, screen_width):
    words = txt.split()
    current_line = ""
    line_width = 0
    txt_list = []
    for word in words:
        if word == '~n':
            txt_list.append(current_line)
            txt_list.append(' ')
            current_line = ""
            line_width = 0
        else:
            if (line_width + font.size(str(word))[0]) >= (screen_width - 300):
                txt_list.append(current_line)
                current_line = word
                line_width = font.size(str(word))[0]
            else:
                current_line = current_line + " " + str(word)
                line_width += font.size(str(word))[0]
    txt_list.append(current_line)
    txt_list.append(' ')
    return txt_list


def image_description(screen, size, food_image, description):
    end = False
    x = size[0]/2
    y = size[1]/2
    while not end:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                end = True
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
        picture = pygame.image.load(food_image)
        text = font.render(description, 1, BLACK)
        # Get the image position
        image_rect = picture.get_rect()
        x_pos1 = x - image_rect[2] / 2
        y_pos1 = y - image_rect[3] / 2
        # Get the text position based on its size
        x_pos2 = x - font.size(description)[0] / 2
        y_pos2 = y_pos1 + image_rect[3] + 20
        # Blit the images now
        screen.blit(picture, (x_pos1, y_pos1))
        screen.blit(text, [x_pos2, y_pos2])

        pygame.display.flip()


def describe_task(instruction_list, screen, size):
    x = size[0] / 2
    y = size[1] / 2
    for instruction in instruction_list:
        done = False
        while not done:
            # Whenever the participant presses a key we move to the next screen
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    done = True
            # now we create a list containing each line of this instruction screen
            full_text = word_wrap(instruction, size[0])
            full_text.append('Press any key to continue.')
            # Now there are a bunch of variables we need to set for the loop
            height = y - get_top(full_text)/2
            index = 0
            text = []
            screen.fill(WHITE)
            for line in full_text:
                width = font.size(line)[0]
                pos = [x - width/2, height]
                text.append(font.render(line, 1, BLACK))
                screen.blit(text[index], pos)
                # Then adjust the height
                height += text[index].get_height()
                index += 1
            pygame.display.flip()


# This is the main loop called, where the order of the stimuli is held
def procedure(screen, size, participant):
    # Here be the instructions for the rating task:
    rating_instructions = ['Welcome to the experiment!',
                           'During the next segment, you will see images representing different food items.',
                           'You will be asked to rate each one based on your general preference for that food item.',
                           'The scale is from one to nine, where one means you do not prefer the food and nine means you highly prefer the food.',
                           'Use the number keys at the top of the keyboard to input your rating.',
                           'The images are to illustrate the food item, however, bear in mind your preference in general for that food.',
                           'For example... ']
    describe_task(rating_instructions, screen, size)
    cake_images = [os.path.join('examples', 'chocolate cake.jpg'), os.path.join('examples', 'cake2.jpg'),
                   os.path.join('examples', 'cake3.jpg')]
    image_description(screen, size, cake_images[0], 'Chocolate Cake')
    describe_task(['Is the same as: '], screen, size)
    image_description(screen, size, cake_images[1], 'Chocolate Cake')
    describe_task(["Or..."], screen, size)
    image_description(screen, size, cake_images[2], 'Chocolate Cake')
    describe_task(['What is important is how you generally like the food.', 'Let the experimenter know if you are ready to continue'], screen, size)
    # ISI
    describe_task(['Before the rating task, we will have a long resting period. Please keep your eyes directed towards the cross. Try to clear your mind. We are ready to begin the expirement, if you have any questions please ask the experimenter now.'], screen, size)
    isi(60000, participant, screen, size, mark_start=True, mark_end=True)
    # Here be the rating task
    rating_task(participant, screen, size)
    # Here be the resting state part:
    
    # Describes the task
    decision_instructions = ["For this next task, you will play with another partner.",
                             "You and your partner receive a gift card that allows you and your partner to buy meals at a food court.",
                             "The card lasts for a limited period of time, after which it will expire and all extra money will be lost. ",
                             "On each trial your partner and you decide one food item to purchase. ",
                             "You will find out what your partner has selected after you both decide.",
                             "Before each trial, your options will be presented for a time, as displayed in the following frame: "]
    describe_task(decision_instructions, screen, size)
    # Display the prep_screen as demonstration of the task
    button_position_1, button_position_0 = prep_screen(screen, size, "apple", "asparagus", participant, training=True)
    # Introduce the choice screen
    describe_task(["During this screen do not press any keys, but decide which item you will choose.",
                   "You will then see the choice screen, where you will be able to enter your choice. ",
                   "Example:"], screen, size)
    # Display the choice screen to demonstrate the task
    choice_screen(screen, size, participant, "apple", "food", button_position_1, button_position_0, training=True)
    # Continue the explanation.
    describe_task(["In the choice screen, you will have 2-3 seconds to decide based on the options given in the previous screen.",
                   'Use 1 or 0 at the top of the keyboard to input your decision.',
                   "Following this screen, your partner's decision and the round's outcome will be displayed.",
                   "The game will continue until the card is out of money or until task completion.",
                   "You want the money to last through all the trials while having as a little as possible left.",
                   "The next five trials will be for practice only. Continue when ready. "],
                  screen, size)
    # Training for the decision task
    decision_task(screen, size, participant, trials=5, training=True)

    # Here, after the practice trials, we will have a resting state.
    describe_task(["That concludes the practice trials.",
                   "During the game there will be 15-25 rounds.",
                   "You have two goals: 1) ~n Don't run out of money, ~n 2) Spend as much money before the last round. ",
                   "If you have any questions, please ask the experimenter now. Continue when ready. ",
                   "We will begin the game with a long resting period. Please keep your eyes directed towards the cross. Try to clear your mind. We are ready to begin the experiment, if you have any questions please ask the experimenter now."], screen, size)
    # Here's where we'll actually record the data
    participant.set_amount()
    decision_task(screen, size, participant, trials=24, training=False)
    isi(3000, participant, screen, size)
    # Rating task again
    describe_task(["The following screen will have you rate food items, as you did before",
                   "Please respond quickly"], screen, size)
    rating_task(participant, screen, size)
    describe_task(["We will now have another resting period. Please keep your eyes directed towards the cross. Try to clear your mind."], screen, size)
    isi(60000, participant, screen, size, mark_start=True, mark_end=True)
    describe_task(["Thanks! That's all!"], screen, size)
    pygame.quit()


# Here be the main thing
def main():
    # Let's find out about the participant, and start pygame
    participant = Participant(["Participant", "Food Rated", "Food Rating", "Trial Food C", "Trial Food D",
                               "Decision", "Opponent Decision", "RT"])
    # Let's get information about the screen and it's size, and get it going
    size = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode(size, FULLSCREEN, 32)
    pygame.display.toggle_fullscreen()

    procedure(screen, size, participant)

if __name__ == '__main__':
    main()
