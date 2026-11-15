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

Maya captured the actual native before/after on 2026-11-15 using the exact
generated startup writes, before demo setup (`begun=False`, MQ01stage10=False).
The private archived logs are `work/runs/fresh-baseline-20261115/native-before.log`
and `native-after.log`; after capture ran 09:08:42–09:08:51. Batch SHA256:
`77B4D90066ADA12AD2B53F7BEFBA2C0D44A93627875E0268E0137FEA2CC75E68`.

| Native reading | Before | After |
|---|---|---|
| Level | 1 | 1 |
| Seven SPECIAL, base/current | 1 each | 4 each |
| Health, base/current | 85 | 100 |
| AP, base/current | 70 | 100 |
| Caps/Stimpak/.44/ammo/transit-pass counts | 0 each | 0 each |
| Total inventory item count | 2 | 2 |
| Active base-game perk forms (innate included) | 5 | 5 |
| Actor-base Essential/Invulnerable | false/false | false/false |

Health/AP 100 are observed engine results, not constants written by the preset.
Perk points and god mode remain UNKNOWN; no such command was issued. The full
production runner's launch/close/recovery path remains to be exercised separately.
Then verify normal revolver/six-round discovery and completion. Capture
a progressed/resumed character separately without the bootstrap and show no
stat reset or repeated item grants. A SET UP report is never a gameplay pass.
Root-owned private probes may supply native evidence; no physical controller
press or completed new preset playthrough is claimed here.

Rollback: revert this runner-only change. It cannot migrate an already-saved
character's stats and contains no automatic save migration.

## Optional personal F4SE launch

`Play-Act1.ps1 -UseF4SE` forwards through Update-And-Run and Run-FirstBuild to
Run-Scenarios. Default is off, including scored tests. With the explicit switch,
the launcher is the managed game's existing `f4se_loader.exe`; the expected game
process/path remains that same `Fallout4.exe`. The known managed pair is checked:
game 1.10.163.0, loader resource 0.0.6.23, and matching runtime DLL present.
Missing/unreadable/unverified pairs stop before launch. No installer, download,
authentication, automatic mod enablement or extra settings change is introduced.
This supports the owner's personal UI mods; the project keeps vanilla Papyrus
APIs and does not require F4SE for its ordinary demo or tests.
