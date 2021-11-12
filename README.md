# Tales of an Endless Journey (TEJ)
_Automated, progress quest-inspired procedural adventuring_

## What is this project?
Journey is the result of many, many attempts at making some form of D&D inspired computer program. The scope of this project has, over the years, variously shifted from a text adventure game to a fairly faithful recreation of 5e to a full text adventure scripting engine powered by Markdown to a world simulation that also allowed you to explore it (the last is the Civsim project). It's current party-focused instantiation  owes itself to inspiration from games such as [Dungeon Campaign](https://www.mobygames.com/game/dungeon-campaign) (Although its graphics are, if possible, even worse) as well as automated simulators such as [Progress Quest](http://progressquest.com/), which has just received a CLI release. Oh, also automated roguelikes like [Roguathia](https://seiyria.com/Roguathia/).

## How do I "play" TEJ?
1. Download all files.
2. Install the `pyyaml` module for python using `pip install pyyaml`.
3. Run `main.py`.
4. Sit back and relax, the journey has begun.

## Ok, but seriously, how do I "play" TEJ?
When TEJ is created, a party of random characters is generated and go through their lives before adventuring. Being strong willed adventurers, they come with minds of their own, and are naturally reluctant to follow any commands. Indeed, they will insist on making all decisions by themselves, either through collective voting or selfishly, leaving you (the player) with little to do except watch their exploits play out. You can leave the window in the background, and if (when) these adventurers fall you will receive your highscore - my current highscore is 2599.

## How does TEJ work?
TEJ works using a system of markov chains containing various nodes. For example, the wilderness node can either link to itself (going from one spot in the wild to another), to a travel encounter, to a town, or to a dungeon. Each node also has an associated event, which sometimes gives the characters some control over where they end up through skill checks, voting, or similar mechanisms.

Characters can also have encounters with other creatures, which have different power levels and are not generated to be a "fair fight". Based on the power disparity between the groups and fear and aggression in the party, adventurers can choose to fight, flight, or parley. Of course, if they come to blows and adventurers die, the party is diminished. When the party is lost to traps, exhaustion, or foes, the game is over... (You can sometimes recruit party members in town, no fear, and surviving dungeons levels party members up!)

## I want more biomes/monsters/unique encounters/X feature!
You're in luck! TEJ is designed to be pretty extensible, and I'm looking forward to reworking the codebase to make it even more extensible! To add a new node in the markov chain, simply edit the list of possible outcomes for each node in `generic_adventure.yaml` and then the function in the `Adv` class in `generic_adventure.py`. Be warned that some nodes specify what outcome they link to using special methods in the function rather than "choosing" from the markov chain options. Monsters are simply a name, a vertical bar `|`, and a power number added to the list in `generic_encounters.yaml`. If you want a monster to have special behaviour, I've written up an example of a special enemy (the venomous adder) in `generic_adventure.py`. Any subclasses for `Enemy` you add using this format are automatically detected and will replace the relevant bestiary entry. When naming the subclass, be sure to name it exactly the same as the bestiary entry, except replacing ` ` with `_`.

## Any last words?
Have fun!
