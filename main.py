import pygame
import sys

import nxt.motor
import nxt.locator
import nxt.brick


class NXTCrane:
    def __init__(self):
        self.initialized = False
        self.brick = None
        self.m1 = None
        self.m2 = None
        self.m3 = None

    def is_connected(self):
        return self.initialized

    def connect(self) -> bool:
        if not self.initialized:
            try:
                self.brick = nxt.locator.find()
                if isinstance(self.brick, nxt.brick.Brick):
                    self.m1 = self.brick.get_motor(nxt.motor.Port.A)
                    self.m2 = self.brick.get_motor(nxt.motor.Port.B)
                    self.m3 = self.brick.get_motor(nxt.motor.Port.C)
                self.initialized = True
            except nxt.locator.BrickNotFoundError:
                self.initialized = False
        return self.initialized

    def disconnect(self):
        if self.initialized:
            if isinstance(self.brick, nxt.brick.Brick):
                self.brick.close()
        self.initialized = False

    def turn_motor(self, motor_id: int, direction: bool, power: int):
        if self.initialized:
            match motor_id:
                case 0:
                    motor: nxt.motor.Motor = self.m1
                case 1:
                    motor: nxt.motor.Motor = self.m2
                case 2:
                    motor: nxt.motor.Motor = self.m3
                case _:
                    print(f"Invalid motor id: {motor_id}")
                    return
            a = 1 if direction else -1
            motor.run(a * power)

    def stop_motor(self, motor_id: int):
        if self.initialized:
            match motor_id:
                case 0:
                    if isinstance(self.m1, nxt.motor.Motor):
                        self.m1.brake()
                case 1:
                    if isinstance(self.m2, nxt.motor.Motor):
                        self.m2.brake()
                case 2:
                    if isinstance(self.m3, nxt.motor.Motor):
                        self.m3.brake()

    def stop_all_motors(self):
        for m in range(3):
            self.stop_motor(m)


class Motor:
    def __init__(self, crane: NXTCrane, port_id, keys: tuple, top_left: tuple[int, int], size: tuple[int, int]):
        self.id = port_id
        self.crane = crane
        self.state = 0
        self.power = 50
        self.rect = pygame.Rect(top_left, size)
        self.text = f"Motor {port_id}"
        self.key_up = keys[0]
        self.key_down = keys[1]

        self.color_white = (255, 255, 255)
        self.color_bright = (200, 200, 200)
        self.color_highlighted = (200, 255, 200)

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.key_up:
                self.turn(True)
            elif event.key == self.key_down:
                self.turn(False)
        elif event.type == pygame.KEYUP:
            if event.key == self.key_up or event.key == self.key_down:
                self.stop()

    def turn(self, direction: bool):
        self.state = 1 if direction else 2
        self.crane.turn_motor(self.id, direction, self.power)

    def stop(self):
        self.state = 0
        self.crane.stop_motor(self.id)

    def draw(self, window):
        color = self.color_highlighted if self.state == 1 else self.color_bright
        font = pygame.font.Font(None, 24)
        pygame.draw.rect(window, color, self.rect)
        text = font.render(pygame.key.name(self.key_up), True, self.color_white)
        text_rect = text.get_rect(center=self.rect.center)
        window.blit(text, text_rect)
        color = self.color_highlighted if self.state == 2 else self.color_bright
        pygame.draw.rect(window, color, self.rect.move(0, 100))
        text = font.render(pygame.key.name(self.key_down), True, self.color_white)
        text_rect = text.get_rect(center=self.rect.move(0, 100).center)
        window.blit(text, text_rect)


if __name__ == '__main__':
    pygame.init()
    window_size = (420, 250)
    window = pygame.display.set_mode(window_size)
    pygame.display.set_caption("NXT Crane")

    brick = NXTCrane()
    brick.connect()
    if not brick.is_connected():
        print("Could not connect to NXT")
        sys.exit(-1)
    else:
        print("Connected to NXT")
    motor1 = Motor(brick, 1, (pygame.K_UP, pygame.K_DOWN), (50, 50), (100, 50))
    motor2 = Motor(brick, 2, (pygame.K_LEFT, pygame.K_RIGHT), (160, 50), (100, 50))
    # We reduce the power on extending the arm because it goes too fast otherwise
    motor2.power = 20
    motor3 = Motor(brick, 0, (pygame.K_PAGEUP, pygame.K_PAGEDOWN), (270, 50), (100, 50))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                try:
                    brick.stop_all_motors()
                    brick.disconnect()
                except:
                    pass
                pygame.quit()
                sys.exit()
            motor1.handle_key_event(event)
            motor2.handle_key_event(event)
            motor3.handle_key_event(event)
        window.fill((50, 50, 50))
        motor1.draw(window)
        motor2.draw(window)
        motor3.draw(window)
        pygame.display.flip()
