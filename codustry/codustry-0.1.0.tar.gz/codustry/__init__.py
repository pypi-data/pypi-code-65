import asyncio
from avajana.bubbling import Bubbling

from halo import Halo

msg = """No job is better than dirty job.
Public contribution is better than private contribution.
Transparent is better than privacy.
Gradient is better than binary.
Systematic solution is better than linear solution.
Fork is better than copy.
User's end goals is better than user's requirements.
The best default should always pair with great alternatives.
Keep in mind, true freedom is not the freedom choose.
But, the power to create new choice.
User Success is the king.
Maintainability is the queen.
Security is the jack.
We are like the Avengers, of digital world.
Individual is selected/unselected because of his/her karma solely.
Not race, sex, and other non-senses.
Anonymous individuals are accepted here.
See you, codeatsecj3ofewyaeywlig32wpcxa436j4anaiqfbbd2e7tkoqzgfyd.onion
Use longitude to adjust wake up time.
Use latitude to customize climate.
Anyway mission come first.
Automation is the ace. Let’s do more of this.
Data & Legal is the jokers. Always pay respect."""

loop = asyncio.get_event_loop()
spinner = Halo(text='', spinner='dots')
bubling = Bubbling(word_per_min=256)
for line in msg.splitlines():
    loop.run_until_complete(
        bubling.act_typing(line, spinner.start, spinner.stop)
    )
    print(line)

