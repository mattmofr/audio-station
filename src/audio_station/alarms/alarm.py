class Alarm:
    """État du réveil, déclenché explicitement dans la DEMO S0."""

    def __init__(self) -> None:
        self.ringing = False

    def trigger(self) -> None:
        self.ringing = True

    def stop(self) -> None:
        self.ringing = False
