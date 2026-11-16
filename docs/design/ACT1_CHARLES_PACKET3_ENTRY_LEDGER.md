# Act I, packet 3: the complete entry and priority ledger

Companion to [the receipt](ACT1_CHARLES_PACKET3_RECEIPT.md). This replaces the packet 2 ledger as the current one. Every line of talk in `assets/incoming/act1/story/talk/` as it now stands in the `tlm-talk-2` format: whether it is an entry, its priority before and after, and its conditions. Generated from the files; the labels themselves were assigned by hand in the migration and are for independent review.

"Was" and "at 4b77df4" are the values of the integration commit, which already held the nine guard repairs. "Leads here" lists the lines with a button that leads on to the line. It is information for the reader; no label was computed from it.

## Totals

| | Lines |
|---|---|
| Entries | 129 |
| Continuations | 86 |
| Asides (no `entry`; not part of selection) | 12 |
| All | 227 |
| Of the entries, also the target of a button | 6 |
| Continuations that carry a condition, asked after the button's effects | 22 |
| Entries whose priority is new (no existing number was changed) | 12 |

## Each speaker's entries, highest first

This is the order in which a speaker's greetings are tried. No two entries of one speaker share a number anywhere in the folder.

### belden

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 40 | 40 | `belden_offer` | tlm_mq03 | mq03 done 10; mq03 notdone 40 |  |
| 31 | 31 | `belden_greenwater_relief` | tlm_mq02b | mq02b done 44; alive belden |  |
| 30 | 30 | `belden_greenwater_relief_fire` | tlm_mq02b | mq02b done 43; alive belden |  |
| 0 | 0 | `belden_default` | tlm_mq03 | (none) |  |

### brigg

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `brigg_rifles` | tlm_mq03 | mq03 done 40; mq03 done 43; mq03 notdone 41; mq03 notdone 42; mq03 notdone 44; mq03 notdone 70; alive brigg |  |
| 85 | 85 | `brigg_holds` | tlm_mq03 | mq03 done 70 |  |
| 65 | 65 | `brigg_demand` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard; alive threefords |  |
| 64 | 64 | `brigg_demand_talbot` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot; alive threefords |  |
| 63 | 63 | `brigg_demand_no_whitcomb` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; dead whitcomb; alive threefords |  |
| 62 | 62 | `brigg_demand_no_belden` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; dead belden; alive threefords |  |
| 61 | 61 | `brigg_demand_no_grey` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; dead grey; alive threefords |  |
| 60 | 60 | `brigg_demand_no_officer` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; dead talbot; alive threefords |  |
| 59 | new | `brigg_demand_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 58 | new | `brigg_demand_talbot_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 57 | new | `brigg_demand_no_whitcomb_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; dead whitcomb; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 56 | new | `brigg_demand_no_belden_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; dead belden; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 55 | new | `brigg_demand_no_grey_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; dead grey; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 54 | new | `brigg_demand_no_officer_courier_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; dead talbot; dead threefords | New. Six dead-courier copies at 59 down to 54, directly under the six living-courier orders at 65 to 60, whose numbers are not moved. All twelve are above his offer (40) and below his later replies |
| 40 | 40 | `brigg_offer` | tlm_mq03 | mq03 done 10; mq03 notdone 40 |  |
| 0 | 0 | `brigg_default` | tlm_mq03 | (none) |  |

### cutter

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 60 | 60 | `cutter_rope` | tlm_mq02c | mq02c done 10; dead dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome isnot missed |  |
| 59 | 59 | `cutter_rope_missed` | tlm_mq02c | mq02c done 10; dead dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome is missed |  |

### dole

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 50 | 50 | `dole_sermon` | tlm_mq02a | mq02a done 40; mq02a notdone 41; mq02a notdone 42; mq02a notdone 43; mq02a notdone 44 |  |
| 0 | 0 | `dole_default` | tlm_mq02a | (none) |  |

### dorn

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 60 | 60 | `dorn_door` | tlm_mq02c | mq02c done 45; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 56 |  |
| 0 | 0 | `dorn_default` | tlm_mq02c | (none) |  |

### dunmore

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 60 | 60 | `dunmore_rope` | tlm_mq02c | mq02c done 10; alive dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome isnot missed |  |
| 59 | 59 | `dunmore_rope_missed` | tlm_mq02c | mq02c done 10; alive dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome is missed |  |
| 40 | 40 | `dunmore_freed` | tlm_mq02c | mq02c done 11; alive dunmore |  |
| 39 | 39 | `dunmore_freed_fine` | tlm_mq02c | mq02c done 12; alive dunmore |  |

### flint

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 80 | 80 | `flint_roof` | tlm_mq03 | mq03 done 50 |  |
| 75 | new | `flint_courier_no_brigg_living` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive flint; dead pritchard; dead talbot; alive threefords | New. Above her lines at the shooting match (50, 60); below the roof at 80, which is a later state |
| 74 | new | `flint_courier_no_brigg_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive flint; dead pritchard; dead talbot; dead threefords | New. Above her lines at the shooting match (50, 60); below the roof at 80, which is a later state |
| 60 | 60 | `flint_beaten` | tlm_mq03 | mq03 done 21; mq03 notdone 40 |  |
| 50 | 50 | `flint_line` | tlm_mq03 | mq03 done 20; mq03 notdone 21; mq03 notdone 22; mq03 notdone 40 |  |
| 0 | 0 | `flint_default` | tlm_mq03 | (none) |  |

### granger

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 70 | 70 | `granger_rope` | tlm_mq04 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  |

### greer

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 46 | 46 | `greer_first_heard` | tlm_mq02c | mq02c done 30; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 56 |  |
| 45 | 45 | `greer_first` | tlm_mq02c | mq02c done 20; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 30; mq02c notdone 56 |  |
| 0 | 0 | `greer_default` | tlm_mq02c | (none) |  |

### grey

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 40 | 40 | `grey_offer` | tlm_mq03 | mq03 done 10; mq03 notdone 40 |  |
| 0 | 0 | `grey_default` | tlm_mq03 | (none) |  |

### haskell

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `haskell_after_rope` | tlm_mq04 | mq04 done 64; mq04 notdone 100 |  |
| 40 | 40 | `haskell_sheet` | tlm_mq04 | mq04 done 10; mq04 notdone 100 |  |
| 0 | 0 | `haskell_default` | tlm_mq04 | (none) |  |

### hatcher

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 50 | 50 | `hatcher_table` | tlm_mq02b | mq02b done 30; mq02b notdone 41; mq02b notdone 42; mq02b notdone 43; mq02b notdone 44 |  |
| 0 | 0 | `hatcher_default` | tlm_mq02b | (none) |  |

### lockridge

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `lockridge_after_sold` | tlm_mq02a | mq02a done 43 |  |
| 85 | 85 | `lockridge_hymnal` | tlm_mq02a | mq02a done 55; mq02a notdone 61; mq02a notdone 62; mq02a notdone 63 |  |
| 71 | 71 | `lockridge_after_ran` | tlm_mq02a | mq02a done 41; mq02a notdone 60 |  |
| 70 | 70 | `lockridge_after_dole` | tlm_mq02a | mq02a done 42; mq02a notdone 55 |  |
| 61 | 61 | `lockridge_gate_alerted` | tlm_mq02a | mq02a done 10; flag yard_alerted; mq02a notdone 20 |  |
| 60 | 60 | `lockridge_gate_sold` | tlm_mq02a | mq02a done 10; ledger is sold; mq02a notdone 20 |  |
| 40 | 40 | `lockridge_gate` | tlm_mq02a | mq02a done 10; mq02a notdone 20 |  |
| 0 | 0 | `lockridge_default` | tlm_mq02a | (none) |  |

### nell

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 60 | 60 | `nell_porch` | tlm_mq04 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  |

### pike

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 40 | 40 | `pike_line` | tlm_mq03 | mq03 done 10; mq03 notdone 40; mq03 notdone 20 |  |

### pritchard

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 95 | 95 | `pritchard_after_rope` | tlm_mq04 | mq04 done 64; alive pritchard |  |
| 90 | 90 | `pritchard_case` | tlm_mq03 | mq03 done 60; mq03 notdone 100 |  |
| 85 | 85 | `pritchard_porch` | tlm_mq04 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  |
| 75 | new | `pritchard_courier_no_brigg_living` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive pritchard; alive threefords | New. Above everything he would otherwise say while the courier's fate is open (his roads, reports, the fair, the warrant, 66 at most); below the porch at 85. The living-courier line first; the two cannot hold together |
| 74 | new | `pritchard_courier_no_brigg_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive pritchard; dead threefords | New. Above everything he would otherwise say while the courier's fate is open (his roads, reports, the fair, the warrant, 66 at most); below the porch at 85. The living-courier line first; the two cannot hold together |
| 66 | 66 | `pritchard_hears_rail` | tlm_mq02 | mq02 done 20; mq02 notdone 60; mq02 notdone 100; flag silver_rail |  |
| 65 | 65 | `pritchard_hears_rail_unknown` | tlm_mq02 | mq02 done 20; mq02 notdone 60; mq02 notdone 100; notflag silver_rail |  |
| 64 | 64 | `pritchard_hears_river` | tlm_mq02 | mq02 done 30; mq02 notdone 60; mq02 notdone 100; flag silver_river |  |
| 63 | 63 | `pritchard_hears_river_unknown` | tlm_mq02 | mq02 done 30; mq02 notdone 60; mq02 notdone 100; notflag silver_river |  |
| 62 | 62 | `pritchard_hears_pike` | tlm_mq02 | mq02 done 40; mq02 notdone 60; mq02 notdone 100; flag silver_mine |  |
| 61 | 61 | `pritchard_hears_pike_unknown` | tlm_mq02 | mq02 done 40; mq02 notdone 60; mq02 notdone 100; notflag silver_mine |  |
| 52 | 52 | `pritchard_warrant` | tlm_mq04 | mq04 done 10; mq04 notdone 30 |  |
| 50 | 50 | `pritchard_fair` | tlm_mq03 | mq03 done 10; mq03 notdone 40 |  |
| 40 | 40 | `pritchard_three_tokens` | tlm_mq02 | mq01 done 100; mq02 notdone 50; mq02 notdone 60 |  |
| 17 | 17 | `pritchard_three_tokens_later` | tlm_mq02 | mq02 done 100; mq02 notdone 20; mq02 notdone 30; mq02 notdone 40 |  |
| 16 | 16 | `pritchard_three_tokens_later_rail_river` | tlm_mq02 | mq02 done 100; mq02 notdone 20; mq02 notdone 30; mq02 done 40 |  |
| 15 | 15 | `pritchard_three_tokens_later_rail_pike` | tlm_mq02 | mq02 done 100; mq02 notdone 20; mq02 done 30; mq02 notdone 40 |  |
| 14 | 14 | `pritchard_three_tokens_later_river_pike` | tlm_mq02 | mq02 done 100; mq02 done 20; mq02 notdone 30; mq02 notdone 40 |  |
| 13 | 13 | `pritchard_three_tokens_later_rail` | tlm_mq02 | mq02 done 100; mq02 notdone 20; mq02 done 30; mq02 done 40 |  |
| 12 | 12 | `pritchard_three_tokens_later_river` | tlm_mq02 | mq02 done 100; mq02 done 20; mq02 notdone 30; mq02 done 40 |  |
| 11 | 11 | `pritchard_three_tokens_later_pike` | tlm_mq02 | mq02 done 100; mq02 done 20; mq02 done 30; mq02 notdone 40 |  |
| 8 | 8 | `pritchard_report_menu_kkk` | tlm_mq02 | mq02 done 100; flag silver_rail; flag silver_river; flag silver_mine |  |
| 7 | 7 | `pritchard_report_menu_kku` | tlm_mq02 | mq02 done 100; flag silver_rail; flag silver_river; notflag silver_mine |  |
| 6 | 6 | `pritchard_report_menu_kuk` | tlm_mq02 | mq02 done 100; flag silver_rail; notflag silver_river; flag silver_mine |  |
| 5 | 5 | `pritchard_report_menu_kuu` | tlm_mq02 | mq02 done 100; flag silver_rail; notflag silver_river; notflag silver_mine |  |
| 4 | 4 | `pritchard_report_menu_ukk` | tlm_mq02 | mq02 done 100; notflag silver_rail; flag silver_river; flag silver_mine |  |
| 3 | 3 | `pritchard_report_menu_uku` | tlm_mq02 | mq02 done 100; notflag silver_rail; flag silver_river; notflag silver_mine |  |
| 2 | 2 | `pritchard_report_menu_uuk` | tlm_mq02 | mq02 done 100; notflag silver_rail; notflag silver_river; flag silver_mine |  |
| 1 | 1 | `pritchard_report_menu_uuu` | tlm_mq02 | mq02 done 100; notflag silver_rail; notflag silver_river; notflag silver_mine |  |
| 0 | 0 | `pritchard_default` | tlm_mq02 | (none) |  |

### pruitt

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 60 | 60 | `pruitt_chain` | tlm_mq02b | mq02b done 30; mq02b notdone 41; mq02b notdone 42; mq02b notdone 43; mq02b notdone 44 |  |
| 40 | 40 | `pruitt_skiff` | tlm_mq02b | mq02b done 20; mq02b notdone 30 |  |
| 0 | 0 | `pruitt_default` | tlm_mq02b | (none) |  |

### quill

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 70 | 70 | `quill_after_shot` | tlm_mq02c | mq02c done 11 |  |
| 60 | 60 | `quill_after_drop` | tlm_mq02c | mq02c done 14 |  |
| 55 | 55 | `quill_court_docket` | tlm_mq02c | mq02c done 10; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; flag docket_2298_held |  |
| 50 | 50 | `quill_court` | tlm_mq02c | mq02c done 10; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14 |  |
| 0 | 0 | `quill_default` | tlm_mq02c | (none) |  |

### roark

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 91 | 91 | `roark_after_fire` | tlm_mq02c | mq02c done 53 |  |
| 90 | 90 | `roark_after_deadline` | tlm_mq02c | mq02c done 56 |  |
| 71 | 71 | `roark_after_line` | tlm_mq02c | mq02c done 51 |  |
| 70 | 70 | `roark_after_break` | tlm_mq02c | mq02c done 52 |  |
| 50 | 50 | `roark_mouth` | tlm_mq02c | mq02c done 20; mq02c notdone 40; mq02c notdone 53; mq02c notdone 56 |  |
| 0 | 0 | `roark_default` | tlm_mq02c | (none) |  |

### starnes

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 80 | 80 | `starnes_after_hanging` | tlm_mq02b | mq02b done 60 |  |
| 74 | 74 | `starnes_after_won` | tlm_mq02b | mq02b done 41; mq02b notdone 60; mq02b notdone 61; alive hatcher |  |
| 73 | 73 | `starnes_won_hatcher_dead` | tlm_mq02b | mq02b done 41; dead hatcher |  |
| 72 | 72 | `starnes_after_chute` | tlm_mq02b | mq02b done 42 |  |
| 71 | 71 | `starnes_after_fire` | tlm_mq02b | mq02b done 43 |  |
| 70 | 70 | `starnes_after_share` | tlm_mq02b | mq02b done 44 |  |
| 40 | 40 | `starnes_first` | tlm_mq02b | mq02b done 10; mq02b notdone 20 |  |
| 0 | 0 | `starnes_default` | tlm_mq02b | (none) |  |

### talbot

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 75 | new | `talbot_courier_no_brigg_living` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive talbot; dead pritchard; alive threefords | New. Above his only other conditional greeting (30). Same two numbers as Pritchard's, for a different speaker |
| 74 | new | `talbot_courier_no_brigg_dead` | tlm_mq03 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive talbot; dead pritchard; dead threefords | New. Above his only other conditional greeting (30). Same two numbers as Pritchard's, for a different speaker |
| 30 | 30 | `talbot_going_out` | tlm_mq02 | mq02 done 10; mq02 notdone 50; mq02 notdone 60 |  |
| 0 | 0 | `talbot_default` | tlm_mq02 | (none) |  |

### tarrow

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `tarrow_walking` | tlm_mq02a | mq02a done 43 |  |
| 80 | 80 | `tarrow_in_cut` | tlm_mq02a | mq02a done 40; mq02a notdone 41; mq02a notdone 42; mq02a notdone 43; mq02a notdone 44 |  |
| 71 | 71 | `tarrow_ran` | tlm_mq02a | mq02a done 41 |  |
| 70 | 70 | `tarrow_backed` | tlm_mq02a | mq02a done 44 |  |
| 40 | 40 | `tarrow_footplate` | tlm_mq02a | mq02a done 20; mq02a notdone 40 |  |
| 0 | 0 | `tarrow_default` | tlm_mq02a | (none) |  |

### threefords

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `threefords_dying` | tlm_mq03 | mq03 done 42; mq03 notdone 100; alive threefords |  |
| 0 | 0 | `threefords_default` | tlm_mq03 | (none) |  |

### vane

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 90 | 90 | `vane_porch` | tlm_mq04 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  |
| 70 | 70 | `vane_two_books_kind` | tlm_mq04 | mq04 done 10; outcome is exploited; method is deal; mq04 notdone 30 |  |
| 50 | 50 | `vane_two_books` | tlm_mq04 | mq04 done 10; mq04 notdone 30 |  |
| 0 | 0 | `vane_default` | tlm_mq04 | (none) |  |

### vickers

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 80 | 80 | `vickers_door` | tlm_mq04 | mq04 done 30; mq04 notdone 41; mq04 notdone 42 |  |
| 0 | 0 | `vickers_default` | tlm_mq04 | (none) |  |

### whitcomb

| Priority | Was | Line | File | Conditions | Why the number |
|---|---|---|---|---|---|
| 40 | 40 | `whitcomb_offer` | tlm_mq03 | mq03 done 10; mq03 notdone 40 |  |
| 0 | 0 | `whitcomb_default` | tlm_mq03 | (none) |  |

## Every line

| File | Line | Speaker | Label | Priority | Conditions | Leads here | Origin | Conditions at 4b77df4, if different |
|---|---|---|---|---|---|---|---|---|
| tlm_mq02 | `pritchard_default` | pritchard | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens` | pritchard | **entry** | 40 | mq01 done 100; mq02 notdone 50; mq02 notdone 60 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later` | pritchard | **entry** | 17 | mq02 done 100; mq02 notdone 20; mq02 notdone 30; mq02 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_rail_river` | pritchard | **entry** | 16 | mq02 done 100; mq02 notdone 20; mq02 notdone 30; mq02 done 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_rail_pike` | pritchard | **entry** | 15 | mq02 done 100; mq02 notdone 20; mq02 done 30; mq02 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_rail` | pritchard | **entry** | 13 | mq02 done 100; mq02 notdone 20; mq02 done 30; mq02 done 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_river_pike` | pritchard | **entry** | 14 | mq02 done 100; mq02 done 20; mq02 notdone 30; mq02 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_river` | pritchard | **entry** | 12 | mq02 done 100; mq02 done 20; mq02 notdone 30; mq02 done 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_three_tokens_later_pike` | pritchard | **entry** | 11 | mq02 done 100; mq02 done 20; mq02 done 30; mq02 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_road_rail` | pritchard | continuation | 0 | (none) | `pritchard_three_tokens`, `pritchard_three_tokens_later`, `pritchard_three_tokens_later_rail`, `pritchard_three_tokens_later_rail_pike`, `pritchard_three_tokens_later_rail_river` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_road_river` | pritchard | continuation | 0 | (none) | `pritchard_three_tokens`, `pritchard_three_tokens_later`, `pritchard_three_tokens_later_rail_river`, `pritchard_three_tokens_later_river`, `pritchard_three_tokens_later_river_pike` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_road_pike` | pritchard | continuation | 0 | (none) | `pritchard_three_tokens`, `pritchard_three_tokens_later`, `pritchard_three_tokens_later_pike`, `pritchard_three_tokens_later_rail_pike`, `pritchard_three_tokens_later_river_pike` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_docket_context` | pritchard | continuation | 0 | (none) | `pritchard_road_pike` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_sends_talbot` | pritchard | continuation | 0 | (none) | `pritchard_three_tokens` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_rail` | pritchard | **entry** | 66 | mq02 done 20; mq02 notdone 60; mq02 notdone 100; flag silver_rail |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_rail_unknown` | pritchard | **entry** | 65 | mq02 done 20; mq02 notdone 60; mq02 notdone 100; notflag silver_rail |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_river` | pritchard | **entry** | 64 | mq02 done 30; mq02 notdone 60; mq02 notdone 100; flag silver_river |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_river_unknown` | pritchard | **entry** | 63 | mq02 done 30; mq02 notdone 60; mq02 notdone 100; notflag silver_river |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_pike` | pritchard | **entry** | 62 | mq02 done 40; mq02 notdone 60; mq02 notdone 100; flag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_pike_unknown` | pritchard | **entry** | 61 | mq02 done 40; mq02 notdone 60; mq02 notdone 100; notflag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_calls_fair` | pritchard | continuation | 0 | (none) | `pritchard_hears_pike`, `pritchard_hears_pike_unknown`, `pritchard_hears_rail`, `pritchard_hears_rail_unknown`, `pritchard_hears_river`, `pritchard_hears_river_unknown` | as at 4b77df4 |  |
| tlm_mq02 | `talbot_default` | talbot | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02 | `talbot_going_out` | talbot | **entry** | 30 | mq02 done 10; mq02 notdone 50; mq02 notdone 60 |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_rail_after_fair` | pritchard | continuation, guarded | 0 | mq02 done 100; flag silver_rail | `pritchard_report_menu_kkk`, `pritchard_report_menu_kku`, `pritchard_report_menu_kuk`, `pritchard_report_menu_kuu` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_rail_after_fair_unknown` | pritchard | continuation, guarded | 0 | mq02 done 100; notflag silver_rail | `pritchard_report_menu_ukk`, `pritchard_report_menu_uku`, `pritchard_report_menu_uuk`, `pritchard_report_menu_uuu` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_river_after_fair` | pritchard | continuation, guarded | 0 | mq02 done 100; flag silver_river | `pritchard_report_menu_kkk`, `pritchard_report_menu_kku`, `pritchard_report_menu_ukk`, `pritchard_report_menu_uku` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_river_after_fair_unknown` | pritchard | continuation, guarded | 0 | mq02 done 100; notflag silver_river | `pritchard_report_menu_kuk`, `pritchard_report_menu_kuu`, `pritchard_report_menu_uuk`, `pritchard_report_menu_uuu` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_pike_after_fair` | pritchard | continuation, guarded | 0 | mq02 done 100; flag silver_mine | `pritchard_report_menu_kkk`, `pritchard_report_menu_kuk`, `pritchard_report_menu_ukk`, `pritchard_report_menu_uuk` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_hears_pike_after_fair_unknown` | pritchard | continuation, guarded | 0 | mq02 done 100; notflag silver_mine | `pritchard_report_menu_kku`, `pritchard_report_menu_kuu`, `pritchard_report_menu_uku`, `pritchard_report_menu_uuu` | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_kkk` | pritchard | **entry** | 8 | mq02 done 100; flag silver_rail; flag silver_river; flag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_kku` | pritchard | **entry** | 7 | mq02 done 100; flag silver_rail; flag silver_river; notflag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_kuk` | pritchard | **entry** | 6 | mq02 done 100; flag silver_rail; notflag silver_river; flag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_kuu` | pritchard | **entry** | 5 | mq02 done 100; flag silver_rail; notflag silver_river; notflag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_ukk` | pritchard | **entry** | 4 | mq02 done 100; notflag silver_rail; flag silver_river; flag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_uku` | pritchard | **entry** | 3 | mq02 done 100; notflag silver_rail; flag silver_river; notflag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_uuk` | pritchard | **entry** | 2 | mq02 done 100; notflag silver_rail; notflag silver_river; flag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_menu_uuu` | pritchard | **entry** | 1 | mq02 done 100; notflag silver_rail; notflag silver_river; notflag silver_mine |  | as at 4b77df4 |  |
| tlm_mq02 | `pritchard_report_open_roads` | pritchard | continuation, guarded | 0 | mq02 done 100 | `pritchard_three_tokens_later`, `pritchard_three_tokens_later_pike`, `pritchard_three_tokens_later_rail`, `pritchard_three_tokens_later_rail_pike`, `pritchard_three_tokens_later_rail_river`, `pritchard_three_tokens_later_river`, `pritchard_three_tokens_later_river_pike` | new: supplied whole by packet 3 |  |
| tlm_mq02 | `pritchard_report_open_rail` | pritchard | continuation, guarded | 0 | mq02 done 100 | `pritchard_report_open_roads` | new: supplied whole by packet 3 |  |
| tlm_mq02 | `pritchard_report_open_river` | pritchard | continuation, guarded | 0 | mq02 done 100 | `pritchard_report_open_roads` | new: supplied whole by packet 3 |  |
| tlm_mq02 | `pritchard_report_open_pike` | pritchard | continuation, guarded | 0 | mq02 done 100 | `pritchard_report_open_roads` | new: supplied whole by packet 3 |  |
| tlm_mq02a | `lockridge_default` | lockridge | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_gate` | lockridge | **entry** | 40 | mq02a done 10; mq02a notdone 20 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_gate_alerted` | lockridge | **entry** | 61 | mq02a done 10; flag yard_alerted; mq02a notdone 20 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_gate_sold` | lockridge | **entry** | 60 | mq02a done 10; ledger is sold; mq02a notdone 20 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_dole` | lockridge | continuation | 0 | (none) | `lockridge_gate`, `lockridge_gate_sold` | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_rails` | lockridge | continuation | 0 | (none) | `lockridge_after_ran`, `lockridge_gate`, `lockridge_gate_alerted` | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_hired` | lockridge | continuation | 0 | (none) | `lockridge_gate`, `lockridge_gate_alerted`, `lockridge_gate_sold` | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_default` | tarrow | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_footplate` | tarrow | **entry** | 40 | mq02a done 20; mq02a notdone 40 |  | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_cut_before` | tarrow | continuation | 0 | (none) | `tarrow_footplate` | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_in_cut` | tarrow | **entry**, and a button's target | 80 | mq02a done 40; mq02a notdone 41; mq02a notdone 42; mq02a notdone 43; mq02a notdone 44 | `dole_sermon`, `dole_share` | as at 4b77df4 |  |
| tlm_mq02a | `dole_default` | dole | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02a | `dole_sermon` | dole | **entry**, and a button's target | 50 | mq02a done 40; mq02a notdone 41; mq02a notdone 42; mq02a notdone 43; mq02a notdone 44 | `tarrow_in_cut` | as at 4b77df4 |  |
| tlm_mq02a | `dole_name` | dole | continuation | 0 | (none) | `dole_sermon` | as at 4b77df4 |  |
| tlm_mq02a | `dole_silver` | dole | continuation | 0 | (none) | `dole_name` | as at 4b77df4 |  |
| tlm_mq02a | `dole_share` | dole | continuation | 0 | (none) | `dole_name`, `dole_sermon`, `dole_silver` | as at 4b77df4 |  |
| tlm_mq02a | `dole_face` | dole | continuation | 0 | (none) | `dole_name`, `dole_sermon`, `dole_share`, `dole_silver` | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_ran` | tarrow | **entry**, and a button's target | 71 | mq02a done 41 | `tarrow_in_cut` | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_backed` | tarrow | **entry**, and a button's target | 70 | mq02a done 44 | `tarrow_in_cut` | as at 4b77df4 |  |
| tlm_mq02a | `tarrow_walking` | tarrow | **entry** | 90 | mq02a done 43 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_after_ran` | lockridge | **entry** | 71 | mq02a done 41; mq02a notdone 60 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_after_dole` | lockridge | **entry** | 70 | mq02a done 42; mq02a notdone 55 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_after_sold` | lockridge | **entry** | 90 | mq02a done 43 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_hymnal` | lockridge | **entry** | 85 | mq02a done 55; mq02a notdone 61; mq02a notdone 62; mq02a notdone 63 |  | as at 4b77df4 |  |
| tlm_mq02a | `lockridge_stamp` | lockridge | continuation | 0 | (none) | `lockridge_hymnal` | as at 4b77df4 |  |
| tlm_mq02b | `starnes_default` | starnes | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_first` | starnes | **entry** | 40 | mq02b done 10; mq02b notdone 20 |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_wants` | starnes | continuation | 0 | (none) | `starnes_first` | as at 4b77df4 |  |
| tlm_mq02b | `starnes_guns` | starnes | continuation | 0 | (none) | `starnes_first` | as at 4b77df4 |  |
| tlm_mq02b | `starnes_bowl` | starnes | continuation | 0 | (none) | `starnes_first` | as at 4b77df4 |  |
| tlm_mq02b | `pruitt_default` | pruitt | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02b | `pruitt_skiff` | pruitt | **entry** | 40 | mq02b done 20; mq02b notdone 30 |  | as at 4b77df4 |  |
| tlm_mq02b | `pruitt_confess` | pruitt | continuation | 0 | (none) | `pruitt_skiff` | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_default` | hatcher | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_table` | hatcher | **entry**, and a button's target | 50 | mq02b done 30; mq02b notdone 41; mq02b notdone 42; mq02b notdone 43; mq02b notdone 44 | `hatcher_paid` | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_lost` | hatcher | continuation | 0 | (none) | `hatcher_table` | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_won` | hatcher | continuation | 0 | (none) | `hatcher_table` | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_share` | hatcher | continuation | 0 | (none) | `hatcher_table`, `hatcher_won` | as at 4b77df4 |  |
| tlm_mq02b | `hatcher_paid` | hatcher | continuation | 0 | (none) | `hatcher_table` | as at 4b77df4 |  |
| tlm_mq02b | `pruitt_chain` | pruitt | **entry** | 60 | mq02b done 30; mq02b notdone 41; mq02b notdone 42; mq02b notdone 43; mq02b notdone 44 |  | as at 4b77df4 |  |
| tlm_mq02b | `pruitt_ran` | pruitt | continuation, guarded | 0 | alive pruitt | `pruitt_chain` | as at 4b77df4 | (none) |
| tlm_mq02b | `pruitt_burned` | pruitt | continuation | 0 | (none) | `pruitt_chain` | as at 4b77df4 |  |
| tlm_mq02b | `starnes_after_won` | starnes | **entry** | 74 | mq02b done 41; mq02b notdone 60; mq02b notdone 61; alive hatcher |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_won_hatcher_dead` | starnes | **entry** | 73 | mq02b done 41; dead hatcher |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_denied` | starnes | continuation | 0 | (none) | `starnes_after_won` | as at 4b77df4 |  |
| tlm_mq02b | `starnes_after_chute` | starnes | **entry** | 72 | mq02b done 42 |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_after_fire` | starnes | **entry** | 71 | mq02b done 43 |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_after_share` | starnes | **entry** | 70 | mq02b done 44 |  | as at 4b77df4 |  |
| tlm_mq02b | `starnes_after_hanging` | starnes | **entry** | 80 | mq02b done 60 |  | as at 4b77df4 |  |
| tlm_mq02b | `belden_greenwater_relief` | belden | **entry** | 31 | mq02b done 44; alive belden |  | as at 4b77df4 |  |
| tlm_mq02b | `belden_greenwater_relief_fire` | belden | **entry** | 30 | mq02b done 43; alive belden |  | as at 4b77df4 |  |
| tlm_mq02c | `quill_default` | quill | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02c | `quill_court` | quill | **entry** | 50 | mq02c done 10; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14 |  | as at 4b77df4 |  |
| tlm_mq02c | `quill_court_docket` | quill | **entry** | 55 | mq02c done 10; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; flag docket_2298_held |  | as at 4b77df4 |  |
| tlm_mq02c | `quill_fine` | quill | continuation | 0 | (none) | `quill_court`, `quill_court_docket` | as at 4b77df4 |  |
| tlm_mq02c | `quill_shamed` | quill | continuation, guarded | 0 | mq02c done 13 | `quill_court_docket` | as at 4b77df4 |  |
| tlm_mq02c | `quill_after_shot` | quill | **entry** | 70 | mq02c done 11 |  | as at 4b77df4 |  |
| tlm_mq02c | `quill_after_drop` | quill | **entry** | 60 | mq02c done 14 |  | as at 4b77df4 |  |
| tlm_mq02c | `dunmore_rope` | dunmore | **entry** | 60 | mq02c done 10; alive dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome isnot missed |  | as at 4b77df4 |  |
| tlm_mq02c | `dunmore_rope_missed` | dunmore | **entry** | 59 | mq02c done 10; alive dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome is missed |  | as at 4b77df4 |  |
| tlm_mq02c | `dunmore_tells` | dunmore | continuation | 0 | (none) | `dunmore_rope` | as at 4b77df4 |  |
| tlm_mq02c | `cutter_rope` | cutter | **entry** | 60 | mq02c done 10; dead dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome isnot missed |  | as at 4b77df4 |  |
| tlm_mq02c | `cutter_rope_missed` | cutter | **entry** | 59 | mq02c done 10; dead dunmore; mq02c notdone 11; mq02c notdone 12; mq02c notdone 13; mq02c notdone 14; outcome is missed |  | as at 4b77df4 |  |
| tlm_mq02c | `dunmore_freed` | dunmore | **entry** | 40 | mq02c done 11; alive dunmore |  | as at 4b77df4 |  |
| tlm_mq02c | `dunmore_freed_fine` | dunmore | **entry** | 39 | mq02c done 12; alive dunmore |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_default` | roark | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_mouth` | roark | **entry** | 50 | mq02c done 20; mq02c notdone 40; mq02c notdone 53; mq02c notdone 56 |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_deadline_warning` | roark | continuation | 0 | (none) | `roark_mouth` | as at 4b77df4 |  |
| tlm_mq02c | `roark_why` | roark | continuation | 0 | (none) | `roark_mouth` | as at 4b77df4 |  |
| tlm_mq02c | `roark_back` | roark | continuation | 0 | (none) | `roark_mouth` | as at 4b77df4 |  |
| tlm_mq02c | `roark_cage` | roark | continuation | 0 | (none) | `roark_deadline_warning` | as at 4b77df4 |  |
| tlm_mq02c | `greer_default` | greer | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02c | `greer_first` | greer | **entry** | 45 | mq02c done 20; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 30; mq02c notdone 56 |  | as at 4b77df4 |  |
| tlm_mq02c | `greer_first_heard` | greer | **entry** | 46 | mq02c done 30; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 56 |  | as at 4b77df4 |  |
| tlm_mq02c | `greer_knock` | greer | continuation | 0 | (none) | `greer_first`, `greer_first_heard` | as at 4b77df4 |  |
| tlm_mq02c | `greer_lamp` | greer | continuation | 0 | (none) | `greer_first`, `greer_first_heard` | as at 4b77df4 |  |
| tlm_mq02c | `dorn_default` | dorn | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq02c | `dorn_door` | dorn | **entry** | 60 | mq02c done 45; mq02c notdone 51; mq02c notdone 52; mq02c notdone 53; mq02c notdone 56 |  | as at 4b77df4 |  |
| tlm_mq02c | `dorn_terms` | dorn | continuation | 0 | (none) | `dorn_door` | as at 4b77df4 |  |
| tlm_mq02c | `dorn_who` | dorn | continuation | 0 | (none) | `dorn_door` | as at 4b77df4 |  |
| tlm_mq02c | `dorn_no_head` | dorn | continuation | 0 | (none) | `dorn_terms` | as at 4b77df4 |  |
| tlm_mq02c | `dorn_sworn` | dorn | continuation | 0 | (none) | `dorn_no_head`, `dorn_terms` | as at 4b77df4 |  |
| tlm_mq02c | `dorn_lamp` | dorn | continuation | 0 | (none) | `dorn_door` | as at 4b77df4 |  |
| tlm_mq02c | `roark_after_line` | roark | **entry** | 71 | mq02c done 51 |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_after_break` | roark | **entry** | 70 | mq02c done 52 |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_after_fire` | roark | **entry** | 91 | mq02c done 53 |  | as at 4b77df4 |  |
| tlm_mq02c | `roark_after_deadline` | roark | **entry** | 90 | mq02c done 56 |  | as at 4b77df4 |  |
| tlm_mq03 | `pritchard_fair` | pritchard | **entry** | 50 | mq03 done 10; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `whitcomb_default` | whitcomb | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `whitcomb_offer` | whitcomb | **entry** | 40 | mq03 done 10; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `whitcomb_rates` | whitcomb | continuation | 0 | (none) | `whitcomb_offer` | as at 4b77df4 |  |
| tlm_mq03 | `whitcomb_big` | whitcomb | continuation | 0 | (none) | `whitcomb_offer` | as at 4b77df4 |  |
| tlm_mq03 | `brigg_default` | brigg | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `brigg_offer` | brigg | **entry** | 40 | mq03 done 10; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `brigg_dissent` | brigg | continuation | 0 | (none) | `brigg_offer` | as at 4b77df4 |  |
| tlm_mq03 | `brigg_price` | brigg | continuation | 0 | (none) | `brigg_offer` | as at 4b77df4 |  |
| tlm_mq03 | `brigg_quill` | brigg | continuation | 0 | (none) | `brigg_offer` | as at 4b77df4 |  |
| tlm_mq03 | `belden_default` | belden | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `belden_offer` | belden | **entry** | 40 | mq03 done 10; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `belden_dissent` | belden | continuation | 0 | (none) | `belden_offer` | as at 4b77df4 |  |
| tlm_mq03 | `belden_list` | belden | continuation | 0 | (none) | `belden_offer` | as at 4b77df4 |  |
| tlm_mq03 | `belden_leave` | belden | continuation | 0 | (none) | `belden_offer` | as at 4b77df4 |  |
| tlm_mq03 | `grey_default` | grey | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `grey_offer` | grey | **entry** | 40 | mq03 done 10; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `grey_dissent` | grey | continuation | 0 | (none) | `grey_offer` | as at 4b77df4 |  |
| tlm_mq03 | `grey_cost` | grey | continuation | 0 | (none) | `grey_offer` | as at 4b77df4 |  |
| tlm_mq03 | `grey_train` | grey | continuation | 0 | (none) | `grey_offer` | as at 4b77df4 |  |
| tlm_mq03 | `pike_line` | pike | **entry** | 40 | mq03 done 10; mq03 notdone 40; mq03 notdone 20 |  | as at 4b77df4 |  |
| tlm_mq03 | `pike_flint` | pike | continuation | 0 | (none) | `pike_line` | as at 4b77df4 |  |
| tlm_mq03 | `flint_default` | flint | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `flint_line` | flint | **entry** | 50 | mq03 done 20; mq03 notdone 21; mq03 notdone 22; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `flint_beaten` | flint | **entry** | 60 | mq03 done 21; mq03 notdone 40 |  | as at 4b77df4 |  |
| tlm_mq03 | `threefords_default` | threefords | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq03 | `threefords_dying` | threefords | **entry** | 90 | mq03 done 42; mq03 notdone 100; alive threefords |  | as at 4b77df4 | mq03 done 42; mq03 notdone 100 |
| tlm_mq03 | `flint_roof` | flint | **entry** | 80 | mq03 done 50 |  | as at 4b77df4 |  |
| tlm_mq03 | `flint_who` | flint | continuation | 0 | (none) | `flint_roof` | as at 4b77df4 |  |
| tlm_mq03 | `flint_hat` | flint | continuation | 0 | (none) | `flint_roof` | as at 4b77df4 |  |
| tlm_mq03 | `brigg_rifles` | brigg | **entry**, and a button's target | 90 | mq03 done 40; mq03 done 43; mq03 notdone 41; mq03 notdone 42; mq03 notdone 44; mq03 notdone 70; alive brigg | `brigg_truce_concession_pritchard`, `brigg_truce_concession_talbot` | as at 4b77df4 |  |
| tlm_mq03 | `brigg_holds` | brigg | **entry** | 85 | mq03 done 70 |  | as at 4b77df4 |  |
| tlm_mq03 | `pritchard_case` | pritchard | **entry** | 90 | mq03 done 60; mq03 notdone 100 |  | as at 4b77df4 |  |
| tlm_mq03 | `brigg_demand` | brigg | **entry** | 65 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard |
| tlm_mq03 | `brigg_demand_courier_dead` | brigg | **entry** | 59 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard; dead threefords |  | new: copy of `brigg_demand` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `brigg_demand_talbot` | brigg | **entry** | 64 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot |
| tlm_mq03 | `brigg_demand_talbot_courier_dead` | brigg | **entry** | 58 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot; dead threefords |  | new: copy of `brigg_demand_talbot` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `brigg_demand_no_whitcomb` | brigg | **entry** | 63 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; dead whitcomb; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; dead whitcomb |
| tlm_mq03 | `brigg_demand_no_whitcomb_courier_dead` | brigg | **entry** | 57 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; dead whitcomb; dead threefords |  | new: copy of `brigg_demand_no_whitcomb` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `brigg_demand_no_belden` | brigg | **entry** | 62 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; dead belden; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; dead belden |
| tlm_mq03 | `brigg_demand_no_belden_courier_dead` | brigg | **entry** | 56 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; dead belden; dead threefords |  | new: copy of `brigg_demand_no_belden` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `brigg_demand_no_grey` | brigg | **entry** | 61 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; dead grey; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; dead grey |
| tlm_mq03 | `brigg_demand_no_grey_courier_dead` | brigg | **entry** | 55 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; dead grey; dead threefords |  | new: copy of `brigg_demand_no_grey` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `brigg_demand_no_officer` | brigg | **entry** | 60 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; dead talbot; alive threefords |  | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; dead talbot |
| tlm_mq03 | `brigg_demand_no_officer_courier_dead` | brigg | **entry** | 54 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; dead talbot; dead threefords |  | new: copy of `brigg_demand_no_officer` for a dead courier, without the button to stay with her |  |
| tlm_mq03 | `whitcomb_truce` | whitcomb | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard | `brigg_demand`, `brigg_demand_courier_dead` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard |
| tlm_mq03 | `belden_truce` | belden | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard | `whitcomb_truce` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard |
| tlm_mq03 | `grey_truce` | grey | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard | `belden_truce` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard |
| tlm_mq03 | `pritchard_truce` | pritchard | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard | `grey_truce` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard |
| tlm_mq03 | `whitcomb_truce_talbot` | whitcomb | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard | `brigg_demand_talbot`, `brigg_demand_talbot_courier_dead` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard |
| tlm_mq03 | `belden_truce_talbot` | belden | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard | `whitcomb_truce_talbot` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard |
| tlm_mq03 | `grey_truce_talbot` | grey | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard | `belden_truce_talbot` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard |
| tlm_mq03 | `talbot_truce` | talbot | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard | `grey_truce_talbot` | as at 4b77df4 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; alive brigg; alive whitcomb; alive belden; alive grey; alive talbot; dead pritchard |
| tlm_mq03 | `brigg_truce_concession_pritchard` | brigg | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; alive pritchard | `pritchard_truce` | new: supplied whole by packet 3 |  |
| tlm_mq03 | `brigg_truce_concession_talbot` | brigg | continuation, guarded | 0 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; alive brigg; alive whitcomb; alive belden; alive grey; dead pritchard; alive talbot | `talbot_truce` | new: supplied whole by packet 3 |  |
| tlm_mq03 | `pritchard_courier_no_brigg_living` | pritchard | **entry** | 75 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive pritchard; alive threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq03 | `pritchard_courier_no_brigg_dead` | pritchard | **entry** | 74 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive pritchard; dead threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq03 | `talbot_courier_no_brigg_living` | talbot | **entry** | 75 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive talbot; dead pritchard; alive threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq03 | `talbot_courier_no_brigg_dead` | talbot | **entry** | 74 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive talbot; dead pritchard; dead threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq03 | `flint_courier_no_brigg_living` | flint | **entry** | 75 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive flint; dead pritchard; dead talbot; alive threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq03 | `flint_courier_no_brigg_dead` | flint | **entry** | 74 | mq03 done 40; mq03 notdone 41; mq03 notdone 42; mq03 notdone 43; mq03 notdone 44; mq03 notdone 70; mq03 notdone 100; dead brigg; alive flint; dead pritchard; dead talbot; dead threefords |  | new: supplied whole by packet 3 |  |
| tlm_mq04 | `pritchard_warrant` | pritchard | **entry** | 52 | mq04 done 10; mq04 notdone 30 |  | as at 4b77df4 |  |
| tlm_mq04 | `pritchard_guilty` | pritchard | continuation | 0 | (none) | `pritchard_warrant` | as at 4b77df4 |  |
| tlm_mq04 | `vane_default` | vane | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq04 | `vane_two_books` | vane | **entry** | 50 | mq04 done 10; mq04 notdone 30 |  | as at 4b77df4 |  |
| tlm_mq04 | `vane_two_books_kind` | vane | **entry** | 70 | mq04 done 10; outcome is exploited; method is deal; mq04 notdone 30 |  | as at 4b77df4 |  |
| tlm_mq04 | `vane_refuses` | vane | continuation | 0 | (none) | `vane_two_books` | as at 4b77df4 |  |
| tlm_mq04 | `vane_opens` | vane | continuation | 0 | (none) | `vane_two_books_kind` | as at 4b77df4 |  |
| tlm_mq04 | `vane_silver_early` | vane | continuation | 0 | (none) | `vane_two_books`, `vane_two_books_kind` | as at 4b77df4 |  |
| tlm_mq04 | `vickers_default` | vickers | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq04 | `vickers_door` | vickers | **entry** | 80 | mq04 done 30; mq04 notdone 41; mq04 notdone 42 |  | as at 4b77df4 |  |
| tlm_mq04 | `vickers_yields` | vickers | continuation | 0 | (none) | `vickers_door` | as at 4b77df4 |  |
| tlm_mq04 | `vickers_holds` | vickers | continuation | 0 | (none) | `vickers_door` | as at 4b77df4 |  |
| tlm_mq04 | `vickers_glove` | vickers | continuation | 0 | (none) | `vickers_door` | as at 4b77df4 |  |
| tlm_mq04 | `vane_porch` | vane | **entry** | 90 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  | as at 4b77df4 |  |
| tlm_mq04 | `pritchard_porch` | pritchard | **entry** | 85 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  | as at 4b77df4 |  |
| tlm_mq04 | `granger_rope` | granger | **entry** | 70 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  | as at 4b77df4 |  |
| tlm_mq04 | `nell_porch` | nell | **entry** | 60 | mq04 done 50; mq04 notdone 61; mq04 notdone 62; mq04 notdone 63; mq04 notdone 64 |  | as at 4b77df4 |  |
| tlm_mq04 | `vane_after_read` | vane | continuation | 0 | (none) | `vane_porch` | as at 4b77df4 |  |
| tlm_mq04 | `vane_after_sign` | vane | continuation | 0 | (none) | `vane_porch` | as at 4b77df4 |  |
| tlm_mq04 | `vane_after_hire` | vane | continuation | 0 | (none) | `vane_porch` | as at 4b77df4 |  |
| tlm_mq04 | `vane_names` | vane | continuation | 0 | (none) | `vane_after_read`, `vane_after_sign` | as at 4b77df4 |  |
| tlm_mq04 | `pritchard_after_rope` | pritchard | **entry** | 95 | mq04 done 64; alive pritchard |  | as at 4b77df4 | mq04 done 64 |
| tlm_mq04 | `haskell_default` | haskell | **entry**: default | 0 | (none) |  | as at 4b77df4 |  |
| tlm_mq04 | `haskell_sheet` | haskell | **entry** | 40 | mq04 done 10; mq04 notdone 100 |  | as at 4b77df4 |  |
| tlm_mq04 | `haskell_tells` | haskell | continuation | 0 | (none) | `haskell_sheet` | as at 4b77df4 |  |
| tlm_mq04 | `haskell_after_rope` | haskell | **entry** | 90 | mq04 done 64; mq04 notdone 100 |  | as at 4b77df4 |  |
| town | `granger_ballad_saved` | granger | aside | 20 | outcome is saved |  | as at 4b77df4 |  |
| town | `granger_ballad_walked` | granger | aside | 20 | outcome is evaded |  | as at 4b77df4 |  |
| town | `granger_ballad_missed` | granger | aside | 20 | outcome is missed |  | as at 4b77df4 |  |
| town | `granger_ballad_deal` | granger | aside | 20 | outcome is exploited; method is deal |  | as at 4b77df4 |  |
| town | `granger_ballad_betrayal` | granger | aside | 20 | outcome is exploited; method is betrayal |  | as at 4b77df4 |  |
| town | `talbot_tarrow_aside` | talbot | aside | 30 | flag mail_through; mq02a done 41 |  | as at 4b77df4 |  |
| town | `pike_mould_aside` | pike | aside | 40 | mq03 done 50 |  | as at 4b77df4 |  |
| town | `nell_soup_aside` | nell | aside | 30 | flag grain_sold; alive nell |  | as at 4b77df4 |  |
| town | `vane_ledger_aside` | vane | aside | 30 | ledger is sold; mq04 notdone 10 |  | as at 4b77df4 |  |
| town | `vane_mail_aside` | vane | aside | 35 | flag mail_sold; mq04 notdone 10 |  | as at 4b77df4 |  |
| town | `keene_fever_aside` | keene | aside | 35 | flag mail_through |  | as at 4b77df4 |  |
| town | `keene_no_physic_aside` | keene | aside | 45 | flag mail_sold |  | as at 4b77df4 |  |

## Lines of 4b77df4 no longer present

None.
