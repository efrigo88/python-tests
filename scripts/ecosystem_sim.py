import random


class Entity:
    def __init__(self, x, y, energy):
        self.x = x
        self.y = y
        self.energy = energy

    def move(self, world_width, world_height):
        dx = random.randint(-1, 1)
        dy = random.randint(-1, 1)
        self.x = max(0, min(self.x + dx, world_width - 1))
        self.y = max(0, min(self.y + dy, world_height - 1))
        self.energy -= 1  # Moving costs energy

    def is_alive(self):
        return self.energy > 0


class Plant(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 100)
        self.growth_rate = 5

    def grow(self):
        self.energy += self.growth_rate

    def update(self, world_width, world_height):
        self.grow()
        # Plants don't move


class Herbivore(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 50)
        self.sight_radius = 5
        self.eating_rate = 10
        self.reproduction_threshold = 75

    def find_food(self, plants):
        closest_plant = None
        min_distance = float("inf")
        for plant in plants:
            distance = (
                (self.x - plant.x) ** 2 + (self.y - plant.y) ** 2
            ) ** 0.5
            if distance < min_distance and distance <= self.sight_radius:
                min_distance = distance
                closest_plant = plant
        return closest_plant

    def eat(self, plant):
        self.energy += plant.energy
        plant.energy = 0  # Plant is eaten

    def reproduce(self):
        if self.energy >= self.reproduction_threshold:
            self.energy //= 2  # Split energy with offspring
            return Herbivore(self.x, self.y)
        return None

    def update(self, plants, world_width, world_height):
        plant = self.find_food(plants)
        if plant and plant.is_alive():
            self.eat(plant)
        else:
            self.move(world_width, world_height)
        offspring = self.reproduce()
        return offspring


class Carnivore(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, 75)
        self.sight_radius = 7
        self.eating_rate = 15
        self.reproduction_threshold = 100

    def find_prey(self, herbivores):
        closest_herbivore = None
        min_distance = float("inf")
        for herbivore in herbivores:
            distance = (
                (self.x - herbivore.x) ** 2 + (self.y - herbivore.y) ** 2
            ) ** 0.5
            if distance < min_distance and distance <= self.sight_radius:
                min_distance = distance
                closest_herbivore = herbivore
        return closest_herbivore

    def eat(self, herbivore):
        self.energy += herbivore.energy
        herbivore.energy = 0

    def reproduce(self):
        if self.energy >= self.reproduction_threshold:
            self.energy //= 2
            return Carnivore(self.x, self.y)
        return None

    def update(self, herbivores, world_width, world_height):
        herbivore = self.find_prey(herbivores)
        if herbivore and herbivore.is_alive():
            self.eat(herbivore)
        else:
            self.move(world_width, world_height)
        offspring = self.reproduce()
        return offspring


class Ecosystem:
    def __init__(
        self,
        width,
        height,
        initial_plants,
        initial_herbivores,
        initial_carnivores,
    ):
        self.width = width
        self.height = height
        self.plants = [
            Plant(random.randint(0, width - 1), random.randint(0, height - 1))
            for _ in range(initial_plants)
        ]
        self.herbivores = [
            Herbivore(
                random.randint(0, width - 1), random.randint(0, height - 1)
            )
            for _ in range(initial_herbivores)
        ]
        self.carnivores = [
            Carnivore(
                random.randint(0, width - 1), random.randint(0, height - 1)
            )
            for _ in range(initial_carnivores)
        ]
        self.timestep = 0

    def update(self):
        new_plants = []
        new_herbivores = []
        new_carnivores = []

        # Update plants
        for plant in self.plants:
            if plant.is_alive():
                plant.update(self.width, self.height)
                new_plants.append(plant)

        # Update herbivores
        for herbivore in self.herbivores:
            if herbivore.is_alive():
                offspring = herbivore.update(
                    self.plants, self.width, self.height
                )
                if offspring:
                    new_herbivores.append(offspring)
                new_herbivores.append(herbivore)

        # Update carnivores
        for carnivore in self.carnivores:
            if carnivore.is_alive():
                offspring = carnivore.update(
                    self.herbivores, self.width, self.height
                )
                if offspring:
                    new_carnivores.append(offspring)
                new_carnivores.append(carnivore)

        self.plants = new_plants
        self.herbivores = new_herbivores
        self.carnivores = new_carnivores

        self.timestep += 1

    def display(self):
        # Simple text-based display (can be replaced with a graphical one)
        grid = [["." for _ in range(self.width)] for _ in range(self.height)]
        for plant in self.plants:
            grid[plant.y][plant.x] = "P"
        for herbivore in self.herbivores:
            grid[herbivore.y][herbivore.x] = "H"
        for carnivore in self.carnivores:
            grid[carnivore.y][carnivore.x] = "C"

        for row in grid:
            print("".join(row))
        print(f"Timestep: {self.timestep}")
        print(
            f"Plants: {len(self.plants)}, Herbivores: {len(self.herbivores)}, Carnivores: {len(self.carnivores)}"
        )
        print("-" * 20)


# Simulation parameters
width = 40
height = 20
initial_plants = 50
initial_herbivores = 20
initial_carnivores = 5

# Create the ecosystem
ecosystem = Ecosystem(
    width, height, initial_plants, initial_herbivores, initial_carnivores
)

# Run the simulation for a number of timesteps
for _ in range(100):
    ecosystem.update()
    ecosystem.display()
