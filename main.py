from tkinter import Canvas, Label, Tk, StringVar, Button, LEFT
from random import choice, randint
import pygame
class GameCanvas(Canvas):
    def clean_line(self, boxes_to_delete):
        for box in boxes_to_delete:
            self.delete(box)
        self.update()

    def drop_boxes(self, boxes_to_drop):
        for box in boxes_to_drop:
            self.move(box, 0, Tetris.BOX_SIZE)
        self.update()

    def completed_lines(self, y_coords):
        cleaned_lines = 0
        y_coords = sorted(y_coords)
        for y in y_coords:
            if sum(1 for box in self.find_withtag('game') if self.coords(box)[3] == y) == \
               ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE):
                self.clean_line([box
                                for box in self.find_withtag('game')
                                if self.coords(box)[3] == y])

                self.drop_boxes([box
                                 for box in self.find_withtag('game')
                                 if self.coords(box)[3] < y])
                cleaned_lines += 1
        return cleaned_lines

    def game_board(self):
        board = [[0] * ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE)\
                 for _ in range(Tetris.GAME_HEIGHT // Tetris.BOX_SIZE)]
        for box in self.find_withtag('game'):
            x, y, _, _ = self.coords(box)
            board[int(y // Tetris.BOX_SIZE)][int(x // Tetris.BOX_SIZE)] = 1
        return board
    def boxes(self):
        return self.find_withtag('game') == self.find_withtag(fill="white")

class Shape():
    def __init__(self, coords = None):
        if not coords:
            self.__coords = choice(Tetris.SHAPES)
        else:
            self.__coords = coords

    @property
    def coords(self):
        return self.__coords

    def rotate(self):
        ro_sound = '.\\music\\rotate.wav'
        rotate_sound = pygame.mixer.Sound(ro_sound)
        rotate_sound.play()
        self.__coords = self.__rotate()

    def rotate_directions(self):
        rotated = self.__rotate()
        directions = [(rotated[i][0] - self.__coords[i][0],
                       rotated[i][1] - self.__coords[i][1]) for i in range(len(self.__coords))]

        return directions

    @property
    def matrix(self):
        return [[1 if (j, i) in self.__coords else 0 \
                 for j in range(max(self.__coords, key=lambda x: x[0])[0] + 1)] \
                 for i in range(max(self.__coords, key=lambda x: x[1])[1] + 1)]

    def drop(self, board, offset):
        # print("\n\n\n")
        # print('\n'.join(''.join(map(str, b)) for b in board))
        # print("\n\n\n")
        off_x, off_y = offset
        # print(off_x,off_y)
        last_level = len(board) - len(self.matrix) + 1
        for level in range(off_y, last_level):
            for i in range(len(self.matrix)):
                for j in range(len(self.matrix[0])):
                    if board[level+i][off_x+j] == 1 and self.matrix[i][j] == 1:
                        return level - 1
        return last_level - 1  

    def __rotate(self):
        max_x = max(self.__coords, key=lambda x:x[0])[0]
        new_original = (max_x, 0)

        rotated = [(new_original[0] - coord[1],
                    new_original[1] + coord[0]) for coord in self.__coords]

        min_x = min(rotated, key=lambda x:x[0])[0]
        min_y = min(rotated, key=lambda x:x[1])[1]
        return [(coord[0] - min_x, coord[1] - min_y) for coord in rotated]

class Piece():
    def __init__(self, canvas, start_point, shape = None):
        self.__shape = shape
        if not shape:
            self.__shape = Shape()
        self.canvas = canvas
        self.boxes = self.__create_boxes(start_point)

    @property
    def shape(self):
        return self.__shape

    def move(self, direction):
        if all(self.__can_move(self.canvas.coords(box), direction) for box in self.boxes):
            x, y = direction
            for box in self.boxes:
                self.canvas.move(box,
                                 x * Tetris.BOX_SIZE,
                                 y * Tetris.BOX_SIZE)
            return True
        fall_sound = '.\\music\\fall.wav'
        dropS = pygame.mixer.Sound(fall_sound)
        dropS.play()
        return False

    def rotate(self):
        directions = self.__shape.rotate_directions()
        if all(self.__can_move(self.canvas.coords(self.boxes[i]), directions[i]) for i in range(len(self.boxes))):
            self.__shape.rotate()
            for i in range(len(self.boxes)):
                x, y = directions[i]
                self.canvas.move(self.boxes[i],
                                 x * Tetris.BOX_SIZE,
                                 y * Tetris.BOX_SIZE)

    @property
    def offset(self):
        return (min(int(self.canvas.coords(box)[0]) // Tetris.BOX_SIZE for box in self.boxes),
                min(int(self.canvas.coords(box)[1]) // Tetris.BOX_SIZE for box in self.boxes))

    def predict_movement(self, board):
        level = self.__shape.drop(board, self.offset)
        min_y = min([self.canvas.coords(box)[1] for box in self.boxes])
        return (0, level - (min_y // Tetris.BOX_SIZE))

    def predict_drop(self, board):
        level = self.__shape.drop(board, self.offset)
        self.remove_predicts()

        min_y = min([self.canvas.coords(box)[1] for box in self.boxes])
        for box in self.boxes:
            x1, y1, x2, y2 = self.canvas.coords(box)
            box = self.canvas.create_rectangle(x1,
                                               level * Tetris.BOX_SIZE + (y1 - min_y),
                                               x2,
                                               (level + 1) * Tetris.BOX_SIZE + (y1 - min_y),
                                               fill="#404040",
                                               tags = "predict")

    def remove_predicts(self):
        for i in self.canvas.find_withtag('predict'):
            self.canvas.delete(i) 
        self.canvas.update()

    def __create_boxes(self, start_point):
        boxes = []
        off_x, off_y = start_point
        for coord in self.__shape.coords:
            x, y = coord
            box = self.canvas.create_rectangle(x * Tetris.BOX_SIZE + off_x,
                                               y * Tetris.BOX_SIZE + off_y,
                                               x * Tetris.BOX_SIZE + Tetris.BOX_SIZE + off_x,
                                               y * Tetris.BOX_SIZE + Tetris.BOX_SIZE + off_y,
                                               fill="#ffffff",
                                               tags="game")
            boxes += [box]

        return boxes

    def __can_move(self, box_coords, new_pos):
        x, y = new_pos
        x = x * Tetris.BOX_SIZE
        y = y * Tetris.BOX_SIZE
        x_left, y_up, x_right, y_down = box_coords

        overlap = set(self.canvas.find_overlapping((x_left + x_right) / 2 + x, 
                                                   (y_up + y_down) / 2 + y, 
                                                   (x_left + x_right) / 2 + x,
                                                   (y_up + y_down) / 2 + y))
        other_items = set(self.canvas.find_withtag('game')) - set(self.boxes)

        if y_down + y > Tetris.GAME_HEIGHT or \
           x_left + x < 0 or \
           x_right + x > Tetris.GAME_WIDTH or \
           overlap & other_items:
            # print("y_down + y > Tetris.GAME_HEIGHT : {}".format(y_down + y > Tetris.GAME_HEIGHT))
            # print("x_left + x < 0                  : {}".format(x_left + x < 0))
            # print("x_right + x > Tetris.GAME_WIDTH : {}".format(x_right + x > Tetris.GAME_WIDTH))
            # print("overlap & other_items           : {}".format(overlap & other_items))
            return False
        return True        

class Tetris():
    SHAPES = ([(0, 0), (1, 0), (0, 1), (1, 1)],     # Square
              [(0, 0), (1, 0), (2, 0), (3, 0)],     # Line
              [(2, 0), (0, 1), (1, 1), (2, 1)],     # Right L
              [(0, 0), (0, 1), (1, 1), (2, 1)],     # Left L
              [(0, 1), (1, 1), (1, 0), (2, 0)],     # Right Z
              [(0, 0), (1, 0), (1, 1), (2, 1)],     # Left Z
              [(1, 0), (0, 1), (1, 1), (2, 1)])     # T

    BOX_SIZE = 20

    GAME_WIDTH = 220
    GAME_HEIGHT = 400
    GAME_START_POINT = (GAME_WIDTH / 2 / BOX_SIZE) * BOX_SIZE - BOX_SIZE

    def __init__(self, predictable = False):
        self._level = 0#levelcount
        self._score = 0
        self._blockcount = 0
        self.speed = 80#
        self.predictable = predictable
        self.linecount=0
        hc = open('.\\highscore.txt')
        text = []
        for line in hc:
            text.append(line)
        self.maxscore=int(text[0])
        hc.close()
        self.last = 'None'
        self.brn=0
        self.tetris_c=0
        self.lccount=0
        
        self.root = Tk()
        self.root.geometry("600x550") 
        self.root.title('CKCSC_Tetris')
        self.root.iconbitmap('.\\icon\\icon.ico')
        self.root.attributes("-topmost", 1)
        self.root.resizable(0,0)
        self.root.config(bg="#000000")
        self.root.bind("<Key>", self.game_control)
#        self.root.bind("<Key>", self.shift)
        self.__game_canvas()
        self.__level_score_label()
        self.__next_piece_canvas()

    def game_control(self, event):
        #print(event.keycode, chr(event.keycode), 'speed:', self.speed)
        if event.keycode in [65, 37]:
            self.current_piece.move((-1, 0))
            self.update_predict()
        elif event.keycode in [68, 39]:
            self.current_piece.move((1, 0))
            self.update_predict()
        elif event.keycode in [32, 83, 40]:
            self.hard_drop()
        elif event.keycode in [87, 38]:
            self.current_piece.rotate()
            self.update_predict()
    def new_game(self):
        self.level = 0#levelcount
        self.score = 0
        self.blockcount = 0
        self.speed = 800
        self.linecount=0
        self.last = 'None'
        self.brn=0
        self.tetris_c=0
        self.lccount=0
        self.pretend_var.set(" ")
        self.status.update()
        bgm = '.\\music\\bgm.mp3'
        
        pygame.mixer.init()
        pygame.mixer.music.load(bgm)
        
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        self.canvas.delete("all")
        self.next_canvas.delete("all")

        self.__draw_canvas_frame()
        self.__draw_next_canvas_frame()

        self.current_piece = None
        self.next_piece = None        

        self.game_board = [[0] * ((Tetris.GAME_WIDTH - 20) // Tetris.BOX_SIZE)\
                           for _ in range(Tetris.GAME_HEIGHT // Tetris.BOX_SIZE)]

        self.update_piece()

    def update_piece(self):
        if not self.next_piece:
            self.next_piece = Piece(self.next_canvas, (20,20))
        self.current_piece = Piece(self.canvas, (Tetris.GAME_START_POINT, 0), self.next_piece.shape)
        self.next_canvas.delete("all")
        self.__draw_next_canvas_frame()
        self.next_piece = Piece(self.next_canvas, (20,20))
        self.update_predict()

    def start(self):
        self.new_game()
        self.update_status()
        self.update_LC()
        self.update_last()
        self.update_sc()
        self.root.after(self.speed, None)
        self.drop()
        self.update_status()
        self.root.mainloop()

    def drop(self):
        if not self.current_piece.move((0,1)):
            self.current_piece.remove_predicts()
            self.completed_lines()
            self.game_board = self.canvas.game_board()
            self.update_piece()

            if self.is_game_over():
                return
            else:
                self._blockcount += 1
        self.root.after(self.speed, self.drop)

    def hard_drop(self):
        self.current_piece.move(self.current_piece.predict_movement(self.game_board))

    def update_predict(self):
        if self.predictable:
            self.current_piece.predict_drop(self.game_board)

    def update_status(self):
        self.status_var.set(f"Score: {self.score}, HighScore: {self.maxscore}")
        self.status.update()
    def update_LC(self):
        levelup = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100, 100, 100, 100, 100, 100, 110, 120, 130, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        self.lc_var.set(f"Level: {self.level}, Line: {self.linecount}, LevelUpLine: {levelup[self.level]}")
        self.status.update()
    def update_last(self):
        #print(self.tetris_c, "/", self.lccount, " ", self.linecount != 0)
        if self.lccount != 0:
            self.last_var.set(f"Last:{self.last}, BRN:{self.brn}, TRT:{(self.tetris_c*100//self.lccount)}%")
        else:
            self.last_var.set(f"Last:{self.last}, BRN:{self.brn}, TRT:0%")
        self.status.update()
    def update_sc(self):
        self.sc_var.set(f"Single:{40*(self.level+1)}\nDouble:{100*(self.level+1)}\nTriple:{300*(self.level+1)}\nTetris:{1200*(self.level+1)}")
        self.constr_var.set(f"Next:")
        self.status.update()

    def is_game_over(self):
        if not self.current_piece.move((0,1)):
            over = '.\\music\\game-over.mp3'
            pygame.mixer.music.load(over)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(1)
            self.play_again_btn = Button(self.root, text="Play Again", command=self.play_again, bg="#000000",fg="#ffffff")
            self.quit_btn = Button(self.root, text="Quit", command=self.quit, bg="#000000",fg="#ffffff") 
            self.play_again_btn.place(x = Tetris.GAME_WIDTH + 146, y = 400, width=100, height=25)
            self.quit_btn.place(x = Tetris.GAME_WIDTH + 146, y = 450, width=100, height=25)
            if self.score >= self.maxscore:
                self.pretend_var.set("You are Master orz")
            else:
                self.pretend_var.set("You Pretend Weak!")
            self.status.update()
            return True
        return False

    def play_again(self):
        self.play_again_btn.destroy()
        self.quit_btn.destroy()
        self.start()

    def quit(self):
        hc=open('.\\highscore.txt', 'w+')
        hc.write(str(self.maxscore)+'\n')
        hc.close()
        pygame.mixer.music.stop()
        self.root.quit()
        pygame.quit()
        self.root.destroy()

    def completed_lines(self):
        levelup = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 100, 100, 100, 100, 100, 100, 110, 120, 130, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
        levelspeed = [800, 716, 633, 550, 466, 383, 300, 216, 133, 100, 83, 83, 83, 66, 66, 66, 50, 50, 50, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 16, 16, 16, 16, 16, 16, 16]
        
        y_coords = [self.canvas.coords(box)[3] for box in self.current_piece.boxes]
        completed_line = self.canvas.completed_lines(y_coords)
        if completed_line != 0:
            #clear = '.\\music\\lineclear.mp3'
            '''
            pygame.mixer.Sound(r'.\\music\\lineclear.mp3')
            pygame.mixer.Sound.play()
            '''
            tetrisclear_sound = '.\\music\\tetrisclear.wav'
            lineclear_sound = '.\\music\\lineclear.wav'
            tet_sound = pygame.mixer.Sound(tetrisclear_sound)
            lc_sound = pygame.mixer.Sound(lineclear_sound)
            if completed_line == 1:
                self.score += 40*(self.level+1)
                self.linecount += 1
                self.last = 'Single'
                self.brn += 1
                self.lccount += 1
                lc_sound.play()
            elif completed_line == 2:
                self.score += 100*(self.level+1)
                self.linecount += 2
                self.last = 'Double'
                self.brn += 2
                self.lccount += 1
                lc_sound.play()
            elif completed_line == 3:
                self.score += 300*(self.level+1)
                self.linecount += 3
                self.last = 'Triple'
                self.brn += 3
                self.lccount += 1
                lc_sound.play()
            elif completed_line >= 4:
                self.score += 1200*(self.level+1)
                self.linecount += 4
                self.last = 'Tetris'
                self.brn = 0
                self.tetris_c += 1
                self.lccount += 1
                tet_sound.play()
            else:
                self.last = 'None'
            if self.linecount >= levelup[self.level]:
                self.linecount -= levelup[self.level]
                self.level += 1
                lu_sound = '.\\music\\levelup.wav'
                levelup_sound = pygame.mixer.Sound(lu_sound)
                levelup_sound.play()
                self.update_sc()
                self.speed = levelspeed[self.level]
            if self.score > self.maxscore:
                self.maxscore = self.score
                self.update_status()
        self.update_LC()
        self.update_last()
        

    def __game_canvas(self):
        self.canvas = GameCanvas(self.root, 
                             width = Tetris.GAME_WIDTH, 
                             height = Tetris.GAME_HEIGHT,bg="#000000")
        self.canvas.pack(padx=5 , pady=10, side=LEFT)



    def __level_score_label(self):
        self.status_var = StringVar()
        self.lc_var = StringVar()
        self.last_var = StringVar()     
        self.sc_var = StringVar()
        self.constr_var = StringVar()
        self.pretend_var = StringVar()
        self.status = Label(self.root, 
                            textvariable=self.status_var,fg="yellow", 
                            font=("Franklin Gothic Medium", 11, "bold"),bg="#000000")
        self.status.pack()
        self.lc = Label(self.root, 
                            textvariable=self.lc_var,fg="yellow", 
                            font=("Arial Black", 10, "bold"),bg="#100000")
        #self.status.place(x = Tetris.GAME_WIDTH + 10, y = 100, width=100, height=25)
        self.lc.pack()
        self.last = Label(self.root, 
                            textvariable=self.last_var,fg="#BABABA", 
                            font=("Copperplate Gothic Bold", 12, "bold"),bg="#000000")
        self.last.pack()
        self.sc = Label(self.root, 
                            textvariable=self.sc_var,fg="#BABABA", 
                            font=("Abadi MT Condensed Light", 15, "bold"),bg="#000000")
        self.sc.pack()
        
        self.pretend =  Label(self.root,
                            textvariable=self.pretend_var, fg="#FF0000", 
                            font=("Comic Sans MS", 22, "bold"),bg="#000000")
        self.pretend.pack()
        self.constr = Label(self.root,
                            textvariable=self.constr_var, fg="white", 
                            font=("Calisto MT", 12, "bold"),bg="#000000")
        self.constr.pack()
    def __next_piece_canvas(self):
        self.next_canvas = Canvas(self.root,
                                 width = 100,
                                 height = 100,bg="#000000")
        self.next_canvas.pack(padx=5 , pady=10)

    def __draw_canvas_frame(self):
        self.canvas.create_line(10, 0, 10, self.GAME_HEIGHT, fill = "white", tags = "line")
        self.canvas.create_line(self.GAME_WIDTH-10, 0, self.GAME_WIDTH-10, self.GAME_HEIGHT, fill = "white", tags = "line")
        self.canvas.create_line(10, self.GAME_HEIGHT, self.GAME_WIDTH-10, self.GAME_HEIGHT, fill = "white", tags = "line")

    def __draw_next_canvas_frame(self):
        self.next_canvas.create_rectangle(10, 10, 90, 90, tags="frame")


    #set & get
    def __get_level(self):
        return self._level

    def __set_level(self, level):
        levelspeed = [800, 716, 633, 550, 466, 383, 300, 216, 133, 100, 83, 83, 83, 66, 66, 66, 50, 50, 50, 33, 33, 33, 33, 33, 33, 33, 33, 33, 33, 16, 16, 16, 16, 16, 16, 16]
        self.speed = levelspeed[self.level]
        self._level = level
        self.update_status()

    def __get_score(self):
        return self._score

    def __set_score(self, score):
        self._score = score
        self.update_status()

    def __get_blockcount(self):
        return self._blockcount



    level = property(__get_level, __set_level)
    score = property(__get_score, __set_score)

if __name__ == '__main__':
    game = Tetris(predictable = True)
    game.start()