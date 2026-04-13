from pathlib import Path
import sys

import pandas as pd

# Ensure package imports work when tests are run by path.
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from boris import config, project_functions
from boris.analysis_plugins import latency as plugin


def _df(rows):
    return pd.DataFrame(
        rows,
        columns=[
            "Observation id",
            "Subject",
            "Behavior",
            "Start (s)",
            "Stop (s)",
        ],
    )


def test_run_uses_only_latest_previous_behavior():
    df = _df(
        [
            ("obs1", "No focal subject", "1", 2.242, 2.242),
            ("obs1", "No focal subject", "m", 8.418, 8.418),
            ("obs1", "No focal subject", "1", 9.746, 9.746),
            ("obs1", "No focal subject", "m", 13.586, 13.586),
            ("obs1", "No focal subject", "1", 14.418, 14.418),
            ("obs1", "No focal subject", "m", 17.907, 17.907),
            ("obs1", "No focal subject", "1", 19.346, 19.346),
            ("obs1", "No focal subject", "m", 22.899, 22.899),
            ("obs1", "No focal subject", "1", 25.331, 25.331),
            ("obs1", "No focal subject", "m", 29.475, 29.475),
        ]
    )

    (detail_title, detail_df), (summary_title, summary_df) = plugin.run(df)

    assert detail_title == "Behavior latency - Detail"
    assert summary_title == "Behavior latency - Summary by subject"

    one_to_m = detail_df[(detail_df["Behavior A"] == "1") & (detail_df["Behavior B"] == "m")]
    m_to_one = detail_df[(detail_df["Behavior A"] == "m") & (detail_df["Behavior B"] == "1")]

    assert one_to_m["Latency (s)"].tolist() == [6.176, 3.84, 3.489, 3.553, 4.144]
    assert m_to_one["Latency (s)"].tolist() == [1.328, 0.832, 1.439, 2.432]

    assert len(one_to_m) == 5
    assert len(m_to_one) == 4
    assert len(detail_df) == 9

    summary_one_to_m = summary_df[
        (summary_df["Subject"] == "No focal subject")
        & (summary_df["Behavior A"] == "1")
        & (summary_df["Behavior B"] == "m")
    ].iloc[0]
    assert summary_one_to_m["count"] == 5
    assert summary_one_to_m["latency min (s)"] == 3.489
    assert summary_one_to_m["latency max (s)"] == 6.176


def test_summary_is_grouped_by_subject():
    df = _df(
        [
            ("obs1", "S1", "A", 0.0, 0.0),
            ("obs1", "S1", "B", 1.0, 1.0),
            ("obs1", "S1", "A", 2.0, 2.0),
            ("obs1", "S1", "B", 4.0, 4.0),
            ("obs1", "S2", "A", 10.0, 10.0),
            ("obs1", "S2", "B", 13.0, 13.0),
        ]
    )

    _, (summary_title, summary_df) = plugin.run(df)

    assert summary_title == "Behavior latency - Summary by subject"

    s1 = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "A") & (summary_df["Behavior B"] == "B")].iloc[0]
    s2 = summary_df[(summary_df["Subject"] == "S2") & (summary_df["Behavior A"] == "A") & (summary_df["Behavior B"] == "B")].iloc[0]

    assert s1["count"] == 2
    assert s1["latency mean (s)"] == 1.5
    assert s2["count"] == 1
    assert s2["latency mean (s)"] == 3.0


def test_duration_events_use_stop_time_for_latency():
    df = _df(
        [
            ("obs1", "S1", "A", 0.0, 4.0),
            ("obs1", "S1", "B", 7.5, 9.0),
            ("obs1", "S1", "A", 10.0, 12.0),
            ("obs1", "S1", "B", 15.0, 18.0),
        ]
    )

    (_, detail_df), (_, summary_df) = plugin.run(df)

    a_to_b = detail_df[(detail_df["Behavior A"] == "A") & (detail_df["Behavior B"] == "B")]
    b_to_a = detail_df[(detail_df["Behavior A"] == "B") & (detail_df["Behavior B"] == "A")]

    assert a_to_b["Latency (s)"].tolist() == [3.5, 3.0]
    assert b_to_a["Latency (s)"].tolist() == [1.0]

    summary_a_to_b = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "A") & (summary_df["Behavior B"] == "B")].iloc[0]
    assert summary_a_to_b["count"] == 2
    assert summary_a_to_b["latency mean (s)"] == 3.25


def test_mixed_duration_and_point_events():
    df = _df(
        [
            ("obs1", "S1", "A", 0.0, 4.0),
            ("obs1", "S1", "P", 5.0, 5.0),
            ("obs1", "S1", "B", 8.0, 10.0),
            ("obs1", "S1", "P", 11.0, 11.0),
            ("obs1", "S1", "A", 15.0, 17.0),
        ]
    )

    (_, detail_df), (_, summary_df) = plugin.run(df)

    a_to_p = detail_df[(detail_df["Behavior A"] == "A") & (detail_df["Behavior B"] == "P")]
    p_to_b = detail_df[(detail_df["Behavior A"] == "P") & (detail_df["Behavior B"] == "B")]
    b_to_p = detail_df[(detail_df["Behavior A"] == "B") & (detail_df["Behavior B"] == "P")]
    p_to_a = detail_df[(detail_df["Behavior A"] == "P") & (detail_df["Behavior B"] == "A")]

    assert a_to_p["Latency (s)"].tolist() == [1.0, 7.0]
    assert p_to_b["Latency (s)"].tolist() == [3.0]
    assert b_to_p["Latency (s)"].tolist() == [1.0]
    assert p_to_a["Latency (s)"].tolist() == [4.0]

    summary_a_to_p = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "A") & (summary_df["Behavior B"] == "P")].iloc[0]
    summary_p_to_a = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "P") & (summary_df["Behavior B"] == "A")].iloc[0]
    assert summary_a_to_p["count"] == 2
    assert summary_a_to_p["latency mean (s)"] == 4.0
    assert summary_p_to_a["count"] == 1
    assert summary_p_to_a["latency mean (s)"] == 4.0


def test_project2dataframe_integration_with_boris_project_format():
    project = {
        "time_format": "hh:mm:ss",
        "project_date": "2023-11-25T13:26:14",
        "project_name": "Latency test project",
        "project_description": "",
        "project_format_version": "7.0",
        config.SUBJECTS: {},
        config.ETHOGRAM: {
            "0": {"type": "State event", "key": "a", "code": "A", "description": "", "color": "", "category": "", "modifiers": ""},
            "1": {"type": "Point event", "key": "b", "code": "B", "description": "", "color": "", "category": "", "modifiers": ""},
        },
        config.OBSERVATIONS: {
            "obs1": {
                "file": {"1": ["video1.mp4"], "2": [], "3": [], "4": [], "5": [], "6": [], "7": [], "8": []},
                "type": config.MEDIA,
                "date": "2023-11-25T13:27:51",
                "description": "",
                "time offset": 0.0,
                config.EVENTS: [
                    [0.0, "S1", "A", "", "", 0],
                    [4.0, "S1", "A", "", "", "NA"],
                    [5.0, "S1", "B", "", "", 0],
                    [10.0, "S1", "A", "", "", 0],
                    [13.0, "S1", "A", "", "", "NA"],
                    [16.0, "S1", "B", "", "", 0],
                ],
                config.OBSERVATION_TIME_INTERVAL: [0, 0],
                config.INDEPENDENT_VARIABLES: {},
                "visualize_spectrogram": False,
                "visualize_waveform": False,
                "media_creation_date_as_offset": False,
                "media_scan_sampling_duration": 0,
                "image_display_duration": 1,
                "close_behaviors_between_videos": False,
                "media_info": {
                    "length": {"video1.mp4": 179.96},
                    "fps": {"video1.mp4": 25.0},
                    "hasVideo": {"video1.mp4": True},
                    "hasAudio": {"video1.mp4": False},
                    "offset": {"1": 0.0},
                    "display": {"video1.mp4": "Nothing"},
                },
            }
        },
        config.BEHAVIORAL_CATEGORIES: [],
        config.INDEPENDENT_VARIABLES: {},
        config.CODING_MAP: {},
        config.BEHAVIORS_CODING_MAP: [],
        config.CONVERTERS: {},
        config.BEHAVIORAL_CATEGORIES_CONF: {},
    }

    message, df = project_functions.project2dataframe(project, ["obs1"])

    assert message == ""
    assert list(df.columns[:6]) == [
        "Observation id",
        "Observation date",
        "Description",
        "Observation type",
        "Observation interval start",
        "Observation interval stop",
    ]

    (detail_title, detail_df), (_, summary_df) = plugin.run(df)

    assert detail_title == "Behavior latency - Detail"

    a_to_b = detail_df[(detail_df["Behavior A"] == "A") & (detail_df["Behavior B"] == "B")]
    b_to_a = detail_df[(detail_df["Behavior A"] == "B") & (detail_df["Behavior B"] == "A")]

    assert a_to_b["Latency (s)"].tolist() == [1.0, 3.0]
    assert b_to_a["Latency (s)"].tolist() == [5.0]

    summary_a_to_b = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "A") & (summary_df["Behavior B"] == "B")].iloc[0]
    summary_b_to_a = summary_df[(summary_df["Subject"] == "S1") & (summary_df["Behavior A"] == "B") & (summary_df["Behavior B"] == "A")].iloc[0]

    assert summary_a_to_b["count"] == 2
    assert summary_b_to_a["count"] == 1
