class Oscillator:
    def __init__(self,
                 min_val:float=-40.0,
                 max_val:float=40.0,
                 spring_rigidity:float=1,
                 damping:float=0.95,
                 out_of_bounds_bounce_effectiveness:float=0.3) -> None:

        self.value = 0.0
        self.velocity = 0.0
        self.min_val = min_val
        self.max_val = max_val
        self.spring_rigidity = spring_rigidity
        self.damping = damping  # % of speed conserved each second
        self.out_of_bounds_bounce_effectiveness = out_of_bounds_bounce_effectiveness  # if value is oob, bounce

    def update(self, delta: float) -> None:
        # Spring force pulls value back toward 0
        spring_force = -self.value * self.spring_rigidity
        self.velocity += spring_force * delta

        # Apply damping
        self.velocity *= (self.damping ** delta)

        # Integrate position
        self.value += self.velocity * delta

        # Boundary bounce
        if self.value < self.min_val:
            self.value = self.min_val
            if self.velocity < 0:
                self.velocity *= -self.out_of_bounds_bounce_effectiveness
        elif self.value > self.max_val:
            self.value = self.max_val
            if self.velocity > 0:
                self.velocity *= -self.out_of_bounds_bounce_effectiveness

    def impulse(self, velocity: float):
        self.velocity += velocity
