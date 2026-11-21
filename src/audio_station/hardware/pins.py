from collections.abc import Mapping

MINIAMP_PINS = frozenset({16, 18, 19, 20, 21, 26})
SPI0_PINS = frozenset({7, 8, 9, 10, 11})


def validate_control_pins(assignments: Mapping[str, object]) -> dict[str, int]:
    """Vérifie une proposition de GPIO directs sans initialiser de broches."""
    pins: dict[str, int] = {}
    used: dict[int, str] = {}
    for name, pin in assignments.items():
        if type(pin) is not int or not 2 <= pin <= 27:
            raise ValueError(f"{name} doit désigner un GPIO BCM entier de 2 à 27.")
        if pin in MINIAMP_PINS:
            raise ValueError(f"{name} utilise GPIO{pin}, réservé au MiniAmp.")
        if pin in SPI0_PINS:
            raise ValueError(f"{name} utilise GPIO{pin}, réservé au SPI0 dans le projet.")
        if pin in used:
            raise ValueError(f"{name} et {used[pin]} partagent GPIO{pin}.")
        used[pin] = name
        pins[name] = pin
    return pins
