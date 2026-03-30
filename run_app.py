"""
Reusable backend logic for the Streamlit deployment of FloatChat AI.

This module exposes functions only. It does not start any server,
use local model runtimes, or depend on multiple ports.
"""

from functools import lru_cache
from pathlib import Path
import re
from typing import Any

import streamlit as st
from groq import Groq
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


DATA_PATH = Path(__file__).parent / "data" / "my_combinedfinal.csv"
SYSTEM_PROMPT = (
    "You are FloatChat AI, an expert oceanographic data assistant specializing in "
    "Argo float observations. Answer with concise, scientific, accurate explanations. "
    "Use clear markdown. Keep responses to 2-4 short paragraphs."
)

VISUALIZATION_KEYWORDS = {
    "plot", "chart", "graph", "visualize", "visualise", "show",
    "histogram", "trajectory", "map", "profile", "draw", "display",
    "heatmap", "scatter", "compare", "vs", "versus",
}
TEMPERATURE_KEYWORDS = {"temperature", "temp", "thermal"}
SALINITY_KEYWORDS = {"salinity", "salt", "psal", "saline"}
TRAJECTORY_KEYWORDS = {"trajectory", "path", "location", "map", "route", "track"}
HISTOGRAM_KEYWORDS = {"histogram", "distribution", "frequency", "hist"}
HEATMAP_KEYWORDS = {"heatmap", "heat map", "heat-map", "density"}
COMBINED_KEYWORDS = {"combined", "both", "together", "side by side", "all", "compare", "vs", "versus"}


@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Load and normalize the bundled float dataset."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Data file not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    for col in ["pres", "temp", "psal", "latitude", "longitude"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_available_floats() -> list[str]:
    """Return the list of float IDs available in the dataset."""
    df = load_data()
    return sorted(df["float_id"].astype(str).unique().tolist())


def extract_float_id(query: str) -> str | None:
    match = re.search(r"\b(1\d{6,7})\b", query)
    return match.group(1) if match else None


def detect_visualization_request(query: str) -> bool:
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in VISUALIZATION_KEYWORDS)


def detect_chart_type(query: str) -> str:
    query_lower = query.lower()
    if any(keyword in query_lower for keyword in HEATMAP_KEYWORDS):
        return "heatmap"
    if any(keyword in query_lower for keyword in TRAJECTORY_KEYWORDS):
        return "trajectory"
    if any(keyword in query_lower for keyword in HISTOGRAM_KEYWORDS):
        if any(keyword in query_lower for keyword in TEMPERATURE_KEYWORDS):
            return "temp_histogram"
        return "salinity_histogram"
    if any(keyword in query_lower for keyword in COMBINED_KEYWORDS):
        return "combined"
    if any(keyword in query_lower for keyword in SALINITY_KEYWORDS):
        return "salinity_profile"
    return "temperature_profile"


def retrieve_data(query: str, float_id: str | None = None, limit: int = 200) -> pd.DataFrame:
    """Return a slice of dataset rows relevant to the request."""
    del query

    df = load_data().copy()
    if float_id:
        filtered = df[df["float_id"].astype(str) == str(float_id)]
        if not filtered.empty:
            return filtered.head(limit).copy()
    return df.head(limit).copy()


def _build_query_with_history(prompt: str, history: list[dict[str, Any]] | None = None) -> str:
    if not history:
        return prompt

    formatted_messages = []
    for message in history[-6:]:
        role = str(message.get("role", "user")).strip().title()
        content = str(message.get("content", "")).strip()
        if content:
            formatted_messages.append(f"{role}: {content}")

    if not formatted_messages:
        return prompt

    return (
        "Use the recent conversation context when it is helpful.\n\n"
        f"Conversation history:\n{chr(10).join(formatted_messages)}\n\n"
        f"Current user request: {prompt}"
    )


def build_context_text(df: pd.DataFrame, float_id: str | None) -> str:
    """Summarize the data slice for the LLM and fallback responses."""
    if df.empty:
        return "No matching float data was found."

    lines = [f"Data for Argo float {float_id}:" if float_id else "Oceanographic float data summary:"]

    for col, label in [
        ("temp", "Temperature (deg C)"),
        ("psal", "Salinity (PSU)"),
        ("pres", "Pressure (dbar)"),
    ]:
        if col in df.columns:
            values = pd.to_numeric(df[col], errors="coerce").dropna()
            if not values.empty:
                lines.append(
                    f"- {label}: min={values.min():.3f}, max={values.max():.3f}, "
                    f"mean={values.mean():.3f}, std={values.std():.3f}"
                )

    if {"latitude", "longitude"}.issubset(df.columns):
        latitudes = pd.to_numeric(df["latitude"], errors="coerce").dropna()
        longitudes = pd.to_numeric(df["longitude"], errors="coerce").dropna()
        if not latitudes.empty and not longitudes.empty:
            lines.append(
                f"- Location range: lat [{latitudes.min():.3f}, {latitudes.max():.3f}], "
                f"lon [{longitudes.min():.3f}, {longitudes.max():.3f}]"
            )

    if "cycle" in df.columns:
        lines.append(f"- Cycles measured: {df['cycle'].nunique()}")

    lines.append("- Sample measurements:")
    for _, row in df.head(3).iterrows():
        lines.append(
            f"  pres={row.get('pres', 'N/A')} dbar, temp={row.get('temp', 'N/A')} deg C, "
            f"psal={row.get('psal', 'N/A')} PSU"
        )

    return "\n".join(lines)


def create_temperature_profile(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    sorted_df = df.sort_values("pres")
    title = f"Temperature Profile - Float {float_id}" if float_id else "Temperature Profile"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sorted_df["temp"],
            y=sorted_df["pres"],
            mode="lines+markers",
            name="Temperature",
            line=dict(color="#1d4ed8", width=2.5),
            marker=dict(size=5, color="#38bdf8"),
            hovertemplate="Temp: %{x:.2f} deg C<br>Pressure: %{y} dbar<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Temperature (deg C)",
        yaxis_title="Pressure (dbar)",
        yaxis_autorange="reversed",
        height=460,
    )
    return fig


def create_salinity_profile(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    sorted_df = df.sort_values("pres")
    title = f"Salinity Profile - Float {float_id}" if float_id else "Salinity Profile"
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=sorted_df["psal"],
            y=sorted_df["pres"],
            mode="lines+markers",
            name="Salinity",
            line=dict(color="#0f766e", width=2.5),
            marker=dict(size=5, color="#2dd4bf"),
            hovertemplate="Salinity: %{x:.3f} PSU<br>Pressure: %{y} dbar<extra></extra>",
        )
    )
    fig.update_layout(
        title=title,
        xaxis_title="Salinity (PSU)",
        yaxis_title="Pressure (dbar)",
        yaxis_autorange="reversed",
        height=460,
    )
    return fig


def create_combined_profile(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    sorted_df = df.sort_values("pres")
    title = f"Combined Profile - Float {float_id}" if float_id else "Combined Profile"
    fig = make_subplots(rows=1, cols=2, shared_yaxes=True, subplot_titles=("Temperature", "Salinity"))
    fig.add_trace(
        go.Scatter(
            x=sorted_df["temp"],
            y=sorted_df["pres"],
            mode="lines+markers",
            name="Temperature",
            line=dict(color="#1d4ed8", width=2.5),
            marker=dict(size=4, color="#38bdf8"),
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=sorted_df["psal"],
            y=sorted_df["pres"],
            mode="lines+markers",
            name="Salinity",
            line=dict(color="#0f766e", width=2.5),
            marker=dict(size=4, color="#2dd4bf"),
        ),
        row=1,
        col=2,
    )
    fig.update_yaxes(autorange="reversed", title_text="Pressure (dbar)", row=1, col=1)
    fig.update_xaxes(title_text="Temperature (deg C)", row=1, col=1)
    fig.update_xaxes(title_text="Salinity (PSU)", row=1, col=2)
    fig.update_layout(title=title, height=480)
    return fig


def create_temperature_histogram(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    title = f"Temperature Distribution - Float {float_id}" if float_id else "Temperature Distribution"
    fig = go.Figure(
        go.Histogram(
            x=df["temp"].dropna(),
            nbinsx=30,
            marker=dict(color="#1d4ed8"),
            hovertemplate="Temp: %{x:.2f} deg C<br>Count: %{y}<extra></extra>",
        )
    )
    fig.update_layout(title=title, xaxis_title="Temperature (deg C)", yaxis_title="Frequency", height=420)
    return fig


def create_salinity_histogram(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    title = f"Salinity Distribution - Float {float_id}" if float_id else "Salinity Distribution"
    fig = go.Figure(
        go.Histogram(
            x=df["psal"].dropna(),
            nbinsx=30,
            marker=dict(color="#0f766e"),
            hovertemplate="Salinity: %{x:.3f} PSU<br>Count: %{y}<extra></extra>",
        )
    )
    fig.update_layout(title=title, xaxis_title="Salinity (PSU)", yaxis_title="Frequency", height=420)
    return fig


def create_heatmap(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    clean_df = df[["temp", "psal"]].dropna()
    title = f"Temperature-Salinity Density - Float {float_id}" if float_id else "Temperature-Salinity Density"
    fig = go.Figure()
    fig.add_trace(
        go.Histogram2dContour(
            x=clean_df["psal"],
            y=clean_df["temp"],
            colorscale="Blues",
            contours=dict(showlabels=True),
            name="Density",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=clean_df["psal"],
            y=clean_df["temp"],
            mode="markers",
            marker=dict(size=4, opacity=0.35, color="#0f766e"),
            name="Observations",
        )
    )
    fig.update_layout(title=title, xaxis_title="Salinity (PSU)", yaxis_title="Temperature (deg C)", height=460)
    return fig


def create_trajectory_map(df: pd.DataFrame, float_id: str | None) -> go.Figure:
    title = f"Float Trajectory - {float_id}" if float_id else "Float Trajectory"
    location_df = df.dropna(subset=["latitude", "longitude"]).drop_duplicates(subset=["latitude", "longitude"]).copy()
    if "cycle" in location_df.columns:
        location_df = location_df.sort_values("cycle")

    fig = go.Figure(
        go.Scattergeo(
            lat=location_df["latitude"],
            lon=location_df["longitude"],
            mode="lines+markers",
            line=dict(width=2, color="#1d4ed8"),
            marker=dict(size=7, color="#38bdf8"),
            hovertemplate="Lat: %{lat:.3f}<br>Lon: %{lon:.3f}<extra></extra>",
            name="Trajectory",
        )
    )
    fig.update_layout(
        title=title,
        geo=dict(
            showland=True,
            landcolor="#ecfccb",
            showocean=True,
            oceancolor="#dbeafe",
            projection_type="natural earth",
        ),
        height=500,
    )
    return fig


def generate_chart(chart_type: str, df: pd.DataFrame, float_id: str | None) -> go.Figure:
    builders = {
        "temperature_profile": create_temperature_profile,
        "salinity_profile": create_salinity_profile,
        "combined": create_combined_profile,
        "temp_histogram": create_temperature_histogram,
        "salinity_histogram": create_salinity_histogram,
        "heatmap": create_heatmap,
        "trajectory": create_trajectory_map,
    }
    return builders.get(chart_type, create_temperature_profile)(df, float_id)


def fallback_response(query: str, df: pd.DataFrame, float_id: str | None) -> str:
    if df.empty:
        return (
            f"No oceanographic data was found for query: `{query}`. "
            "Try a different float ID or ask a broader question."
        )

    context = build_context_text(df, float_id)
    return (
        f"**Query:** {query}\n\n"
        f"{context}\n\n"
        "This response used the local scientific fallback summary because a live Groq response "
        "was not available."
    )


def query_groq(prompt: str, api_key: str) -> tuple[str | None, str | None]:
    """Call Groq chat completions with basic error handling."""
    if not api_key:
        return None, "Missing Groq API key."

    try:
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=600,
        )
        text = (completion.choices[0].message.content or "").strip() or None
        return text, None
    except Exception as exc:
        return None, f"Groq API request failed: {exc}"


def get_response(prompt: str, history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """
    Generate a chatbot response and optional Plotly figure.

    Returns:
    - text: str
    - chart: go.Figure | None
    """
    query = _build_query_with_history(prompt=prompt, history=history)
    float_id = extract_float_id(prompt)
    df = retrieve_data(query=query, float_id=float_id)

    chart = None
    if detect_visualization_request(prompt) and not df.empty:
        try:
            chart = generate_chart(detect_chart_type(prompt), df, float_id)
        except Exception:
            chart = None

    context = build_context_text(df, float_id)
    llm_prompt = (
        f"User query: {prompt}\n\n"
        f"Available data:\n{context}\n\n"
        "Use the data above to answer the question accurately. If a chart was requested, "
        "describe what the visualization shows in a scientist-friendly way."
    )
    if history:
        llm_prompt = f"{query}\n\n{llm_prompt}"

    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": llm_prompt}],
        )
        groq_text = response.choices[0].message.content
        groq_error = None
    except Exception as exc:
        groq_text = None
        groq_error = str(exc)

    text = groq_text or fallback_response(prompt, df, float_id)
    result = {"text": text, "chart": chart}
    if groq_error:
        result["error"] = groq_error
    return result
