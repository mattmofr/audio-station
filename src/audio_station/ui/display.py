from PIL import Image, ImageDraw, ImageFont

from audio_station.core.station import StationState

SCREEN_SIZE = (320, 240)


def status_text(state: StationState) -> str:
    if state.alarm_ringing:
        return "Réveil en cours"
    if state.standby:
        return "Veille"
    return "Lecture" if state.playback.playing else "Pause"


def render_demo(state: StationState) -> Image.Image:
    frame = Image.new("RGB", SCREEN_SIZE, "#131b20")
    draw = ImageDraw.Draw(frame)
    small = ImageFont.load_default(size=14)
    medium = ImageFont.load_default(size=20)
    large = ImageFont.load_default(size=32)
    draw.text((20, 18), "Audio Station", font=medium, fill="#f5f6f6")
    draw.text((300, 23), "DEMO", font=small, anchor="rt", fill="#99aaa9")
    draw.line((20, 53, 299, 53), fill="#455459")
    draw.text((20, 78), status_text(state), font=medium, fill="#a4dcd0")
    if not state.standby or state.alarm_ringing:
        draw.text((20, 109), state.playback.title, font=large, fill="#f5f6f6")
        draw.text((20, 174), f"Volume {state.playback.volume} %", font=small, fill="#f5f6f6")
        draw.rectangle((20, 202, 299, 205), fill="#455459")
        bar_width = 280 * state.playback.volume // 100
        if bar_width:
            draw.rectangle((20, 202, 19 + bar_width, 205), fill="#a4dcd0")
    return frame
