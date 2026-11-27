# Repair log

Study group: ______________________   Members: ______________________________________________

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
| 1 | KeyError | `features_stage` used `t["depth"]`, but the column is `depth_km` (add file/line) | Changed to `t["depth_km"]` | `test_features.py::test_features_stage_runs`, `test_features.py::test_depth_classes` | @gillianmaxine18 (Gillian Maxine) | 
| 2 | Event timestamps were shifted by 8 hours (14:37 instead of 22:37 Manila time) | quakewatch.py, features_stage(), line 174; t["time"].dt.tz_localize(None).dt.tz_localize("Asia/Manila") stripped UTC and relabeled it as Manila time without converting | Replaced with t["time"].dt.tz_convert("Asia/Manila") | test_features.py::test_strongest_event_is_at_night_in_manila | @hansadrianlaudato-oss Hans | | | | | | |
| 3 | 
| 4 | Events were matched to the wrong nearest city | quakewatch.py, nearest_city(), line 134; passed events["longitude"] and events["latitude"] into haversine_km() in reverse order | Swapped arguments to pass events["latitude"] first, then events["longitude"] | test_integrate.py::test_nearest_city *(verify exact test name in test_integrate.py)* | @kaycelyntigas (Kaycelyn Tigas) |
| 5 | Duplicate earthquake records were fetched and saved on subsequent load_new() calls | quakewatch.py, load_new(), line 95; always passed FIRST_DAY to fetch_range() and ignored watermark() | Checked watermark() and started at (wm + pd.Timedelta(milliseconds=1)).isoformat() when existing data is present | test_acquire.py::test_second_load_adds_nothing, test_acquire.py::test_ids_stay_unique_after_two_loads | @hansadrianlaudato-oss (Hans Laudato) and @gillianmaxine18 (Gillian Maxine) | | | | | | |
| 6 | | | | | |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| | | | | |
| | | | | |
| | | | | |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
| | | | |
| | | | |
| | | | |

## One thing we learned about debugging

(two or three sentences)
