# Repair log

Study group: Group 2  
Members: Gillian Maxine Estilloso, Hans Adrian Laudato, Giana Elisha Tuplano, Kaycelyn Tigas

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
| 1 | KeyError | `features_stage` used `t["depth"]`, but the column is `depth_km` (add file/line) | Changed to `t["depth_km"]` | `test_features.py::test_features_stage_runs`, `test_features.py::test_depth_classes` | @gillianmaxine18 (Gillian Maxine) | 
| 2 | Event timestamps were shifted by 8 hours (14:37 instead of 22:37 Manila time) | quakewatch.py, features_stage(), line 174; t["time"].dt.tz_localize(None).dt.tz_localize("Asia/Manila") stripped UTC and relabeled it as Manila time without converting | Replaced with t["time"].dt.tz_convert("Asia/Manila") | test_features.py::test_strongest_event_is_at_night_in_manila | @hansadrianlaudato-oss (Hans Laudato) | | | | | | |
| 3 | Magnitude 6.0 earthquakes were misclassified as "Moderate" instead of "Strong" | quakewatch.py, MAG_BINS, line 32; upper bin edge for "Moderate" was set to 6.05 instead of 5.95 | Changed MAG_BINS upper edge from 6.05 to 5.95 ([4.95, 5.95, 6.95, 7.95, 10]) | test_features.py::test_mag_class_edges, test_features.py::test_strong_or_above_count | @gianaelishatuplano-jpg (Giana Elisha Tuplano) |
| 4 | Events were matched to the wrong nearest city | quakewatch.py, nearest_city(), line 134; passed events["longitude"] and events["latitude"] into haversine_km() in reverse order | Swapped arguments to pass events["latitude"] first, then events["longitude"] | test_integrate.py::test_nearest_city *(verify exact test name in test_integrate.py)* | @kaycelyntigas (Kaycelyn Tigas) |
| 5 | Duplicate earthquake records were fetched and saved on subsequent load_new() calls | quakewatch.py, load_new(), line 95; always passed FIRST_DAY to fetch_range() and ignored watermark() | Checked watermark() and started at (wm + pd.Timedelta(milliseconds=1)).isoformat() when existing data is present | test_acquire.py::test_second_load_adds_nothing, test_acquire.py::test_ids_stay_unique_after_two_loads | @hansadrianlaudato-oss (Hans Laudato) and @gillianmaxine18 (Gillian Maxine) | | | | | | |
| 6 | Invalid rows (e.g., negative depth or duplicate IDs) were kept in clean data instead of rejected | quakewatch.py, split_by_contract(), lines 113–118; wrapped CONTRACT.validate(raw) in try/except Exception: pass and returned all rows as good | Validated with lazy=True, caught pa.errors.SchemaErrors, collected failing indices from err.failure_cases["index"], and split raw into good and rejects | test_integrate.py::test_bad_rows_are_set_aside | @gianaelishatuplano-jpg (Giana Elisha Tuplano) and @kaycelyntigas (Kaycelyn Tigas) |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| `test_mag_class_around_the_strong_boundary` | `@pytest.mark.parametrize` | Magnitudes `6.0` and `6.04` are classified as `"Strong"` rather than `"Moderate"` | Yes | Maxine |
| `test_second_load_asks_only_for_newer_events` | `responses` (fake API) | Calling `load_new()` a second time queries `starttime` after the saved watermark rather than `FIRST_DAY` | Yes | Hans |
| `test_rejected_rows_produce_a_warning` | `caplog` | Invalid rows (like `depth_km = -5.0`) are separated into rejects and trigger a `WARNING` log message | Yes | Elisha |
| `test_two_runs_leave_no_duplicates` | Pipeline integration (`run_pipeline`) | Running the full pipeline twice adds `0` new rows on the second run and leaves no duplicate event IDs | Yes | Kaycelyn |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
| `run.py` (`main` / file handler setup) | `INFO` | Pipeline stage progress and summary counts written to `logs/run.log` | `INFO` records normal operational milestones and execution summaries without cluttering output with debug noise |
| `quakewatch.py` (`split_by_contract`) | `WARNING` | `integrate: rejected %d of %d rows failing schema contract` | `WARNING` flags unexpected bad records that were quarantined while allowing the rest of the pipeline to continue |
| `quakewatch.py` (`get_json`) | `ERROR` / `EXCEPTION` | Logs HTTP/request exceptions with full stack trace before raising | `EXCEPTION` captures the full traceback when an external API call fails so network or endpoint errors can be diagnosed |
| `quakewatch.py` (`split_by_contract` whole-table failure) | `ERROR` / `EXCEPTION` | Logs schema validation exception with stack trace if table-level contract fails | `EXCEPTION` provides full traceback diagnostics when a structural failure prevents row-level splitting |

## One thing we learned about debugging
A pipeline running without crashing does not mean it is working correctly. Silent `try/except: pass` blocks, swapped coordinate arguments, and misapplied timezone methods produced corrupt outputs without raising a single error, showing us why writing targeted regression tests—including boundary checks, mocked API responses, and log assertions—is essential to catch silent bugs early and prove that fixes actually hold.
