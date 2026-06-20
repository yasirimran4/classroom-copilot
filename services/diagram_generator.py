"""Generate lightweight educational diagrams in Mermaid format."""


def build_mermaid_diagram(topic: str) -> str:
    """Generate simple Mermaid flowchart text based on classroom topic."""
    normalized = topic.lower()

    if "photosynthesis" in normalized:
        return "\n".join(
            [
                "flowchart TD",
                '    sunlight["Sunlight"] --> plant["Green Plant"]',
                '    water["Water + CO2"] --> plant["Green Plant"]',
                '    plant["Green Plant"] --> food["Food (Glucose)"]',
                '    plant["Green Plant"] --> oxygen["Oxygen Release"]',
            ]
        )

    if "water cycle" in normalized:
        return "\n".join(
            [
                "flowchart TD",
                '    evaporation["Evaporation"] --> clouds["Cloud Formation"]',
                '    clouds["Cloud Formation"] --> rain["Rain"]',
                '    rain["Rain"] --> collection["Water Collection"]',
                '    collection["Water Collection"] --> evaporation["Evaporation"]',
            ]
        )

    return "\n".join(
        [
            "flowchart TD",
            f'    topic["{topic.title()}"] --> keyIdea1["Key Idea 1"]',
            '    keyIdea1["Key Idea 1"] --> keyIdea2["Key Idea 2"]',
            '    keyIdea2["Key Idea 2"] --> recap["Quick Recap"]',
        ]
    )
