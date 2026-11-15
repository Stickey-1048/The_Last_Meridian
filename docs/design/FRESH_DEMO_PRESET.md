# Fresh development-demo character preset

Development only, 2026-11-15. This implements a neutral starting baseline for
the manual first-section demo; it is not the permanent character creator.
MQ01 T1 still defers full appearance/name/SPECIAL creation. No identity,
background or locked narrative fact is changed.

## Native starting observation

The disposable main-menu COC character was captured with a private read-only
Papyrus helper on 2026-11-15. Its log reports level 1, all seven SPECIAL values 1,
health 85/AP 70, zero caps/Stimpaks/.44/revolver ammunition, two total inventory
items, no transit pass before MQ01 starts, and actor-base Essential/Invulnerable
false. Five Fallout4.esm perk forms were active among 538 inspected; this includes
innate perks and is not a purchased-perk count. Perk points and god mode were
explicitly UNKNOWN because no supported getters were identified. These are
observations of the original disposable character, not values to hardcode.

## Entry and intended behavior

`tools/win/Play-Act1.ps1` already launches a new main-menu COC session through
the test runner with number 900. That session now runs an owned temporary batch:

```
coc qasmoke
player.setav Strength 4
player.setav Perception 4
player.setav Endurance 4
player.setav Charisma 4
player.setav Intelligence 4
player.setav Agility 4
player.setav Luck 4
```

These are the only preset writes. Level already starts at 1, so no level command
is issued. No command changes the five observed perks; no perk/point/caps/inventory/god-mode
command is used. Health/AP are neither set nor forced: the game must calculate
them from its own rules after the SPECIAL changes. T4's separate inventory
proposal is not implemented by this preset. Existing MQ01 heirloom grant and
revolver/six-round discovery are unchanged.

The runner chooses this batch only for fresh play 900. Scored sessions retain
ordinary COC entry, including in a mixed run. No Papyrus Begin, Core, OnLoad,
quest-init or load-game reset was added. Loading or resuming a saved character
without the runner's fresh bootstrap performs no preset write, and progression
is not reset. The batch deliberately creates a new character; never invoke it
manually on an owner's loaded save.

## Ownership and recovery

The runner records its batch path/hash in the existing unfinished-run note
before creating it or changing startup settings. Its name is a unique
`TLM_FreshDemo_<guid>.txt` in the managed game root. CreateNew refuses existing
files. The note starts as Planned; only successful CreateNew changes ownership
to Owned, and that transition is journaled before batch bytes or startup settings
are written. A rejected existing path is explicitly recorded and preserved even
if its bytes match. Planned plus a present file is an ambiguous interrupted
window: cleanup fails closed and keeps the artifact/note for review.

Owned cleanup requires that exact filename pattern, direct game-root parent,
non-link file and recorded SHA256. A changed or out-of-scope file is preserved
and cleanup fails the run; startup settings are still cleared and the recovery
note is retained. A subsequent run cleans a recorded interrupted batch before
making another. No recursive deletion or owner save access is involved.

## Acceptance and evidence limit

PowerShell stand-in tests check the eight-command whitelist, each SPECIAL once,
owned create/remove, collisions, modified/out-of-scope file preservation,
serialized interrupted-run cleanup, unowned collision/finally/restart preservation,
ownership journaling before bytes, ambiguous creation and failure propagation. These test guards
and intended commands; they do not establish the game's native values.

Actual fresh after-capture is still required: level 1, base/current SPECIAL 4,
engine-derived health/AP, unchanged innate-perk count/caps/gear, and no protection
added. Then verify normal revolver/six-round discovery and completion. Capture
a progressed/resumed character separately without the bootstrap and show no
stat reset or repeated item grants. A SET UP report is never a gameplay pass.
Root-owned private probes may supply native evidence; no physical controller
press or completed new preset playthrough is claimed here.

Rollback: revert this runner-only change. It cannot migrate an already-saved
character's stats and contains no automatic save migration.
