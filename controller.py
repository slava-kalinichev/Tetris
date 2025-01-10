class Controller:
    def __init__(self):
        self.STATES = {
            0: 'main menu',
            1: 'map',
            2: 'level',
        }

        self.state = self.STATES[0]

    def go_to_main_menu(self):
        pass

    def go_to_map(self):
        pass

    def go_to_level(self):
        pass